import json
import tempfile
import unittest
from pathlib import Path

from extraction.extract import extract_report
from extraction.models import get_model, load_registry
from extraction.parsing import parse_model_output
from extraction.prompts import build_messages, load_few_shots


VALID_OUTPUT = [
    {
        "metadata": {
            "report_id": "demo-001",
            "diagnosis": {"who_grade": "not specified"},
            "molecular": [],
            "immunohistochemistry": [],
        }
    }
]


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.messages = None

    def complete(self, messages):
        self.messages = messages
        return self.response


class ExtractionTests(unittest.TestCase):
    def test_packaged_registry_contains_experiment_models(self):
        registry = load_registry()
        self.assertEqual(len(registry["models"]), 9)
        self.assertEqual(get_model("qwen38_27b")["temperature"], 0.0)

    def test_builds_language_specific_prompt(self):
        messages = build_messages("demo-001", "synthetic input", "ja")
        self.assertEqual(len(messages), 1)
        self.assertIn("written in Japanese", messages[0]["content"])
        self.assertIn("synthetic input", messages[0]["content"])

    def test_parses_fenced_output(self):
        result = parse_model_output(f"```json\n{json.dumps(VALID_OUTPUT)}\n```")
        self.assertEqual(result, VALID_OUTPUT)

    def test_uses_last_schema_shaped_json(self):
        echoed = [{"metadata": {"report_id": "schema"}}]
        response = f"echo {json.dumps(echoed)} answer {json.dumps(VALID_OUTPUT)}"
        self.assertEqual(parse_model_output(response), VALID_OUTPUT)

    def test_rejects_non_string_leaf(self):
        invalid = [{"metadata": {"report_id": 1}}]
        with self.assertRaisesRegex(ValueError, "must be a string"):
            parse_model_output(json.dumps(invalid))

    def test_extract_report_uses_direct_response(self):
        client = FakeClient(json.dumps(VALID_OUTPUT))
        result = extract_report("synthetic input", "demo-001", "en", client)
        self.assertEqual(result, VALID_OUTPUT)
        self.assertIn("synthetic input", client.messages[-1]["content"])

    def test_template_must_be_filled_before_use(self):
        template = [
            {
                "report_id": "demo-001",
                "report": "<replace with report text>",
                "output": VALID_OUTPUT,
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "fewshot.json")
            path.write_text(json.dumps(template), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "replace the placeholders"):
                load_few_shots(path)


if __name__ == "__main__":
    unittest.main()

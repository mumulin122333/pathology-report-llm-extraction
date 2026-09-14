import json
import tempfile
import unittest
from pathlib import Path

from evaluation.evaluate import evaluate_directories


class DirectoryEvaluationTests(unittest.TestCase):
    def test_pairs_by_filename_and_reports_unpaired_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            references = root / "references"
            predictions = root / "predictions"
            references.mkdir()
            predictions.mkdir()

            payload = {
                "label": "class a",
                "molecular": [{"molecular_marker": "marker-a"}],
                "immunohistochemistry": [{"IHC_marker": "stain-a"}],
            }
            (references / "case-001.json").write_text(json.dumps(payload), encoding="utf-8")
            (references / "case-002.json").write_text(json.dumps(payload), encoding="utf-8")
            (predictions / "case-001.json").write_text(json.dumps(payload), encoding="utf-8")

            rows, summary = evaluate_directories([references], [predictions])

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["case"], "CASE-001")
            self.assertEqual(rows[0]["overall"], 1.0)
            self.assertEqual(summary["reference_only"], 1)
            self.assertEqual(summary["prediction_only"], 0)

    def test_can_pair_by_report_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            references = root / "references"
            predictions = root / "predictions"
            references.mkdir()
            predictions.mkdir()

            reference = {"report_id": "case-001", "label": "a"}
            prediction = {"report_id": "CASE-001", "label": "a"}
            (references / "reference.json").write_text(json.dumps(reference), encoding="utf-8")
            (predictions / "prediction.json").write_text(json.dumps(prediction), encoding="utf-8")

            rows, summary = evaluate_directories(
                [references], [predictions], key_mode="report_id"
            )

            self.assertEqual(len(rows), 1)
            self.assertEqual(summary["scored"], 1)


if __name__ == "__main__":
    unittest.main()

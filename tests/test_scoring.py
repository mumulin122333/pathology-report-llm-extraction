import json
import tempfile
import unittest
from pathlib import Path

from evaluation.scoring import load_metadata, marker_f1, score_case


class ScoringTests(unittest.TestCase):
    def test_exact_case_scores_one(self):
        reference = {
            "report_id": "case-001",
            "diagnosis": {"label": "class a"},
            "molecular": [{"molecular_marker": "marker-a"}],
            "immunohistochemistry": [{"IHC_marker": "stain-a"}],
        }
        prediction = {
            "report_id": "CASE-001",
            "diagnosis": {"label": "Class A"},
            "molecular": [{"molecular_marker": "marker a"}],
            "immunohistochemistry": [{"IHC_marker": "STAIN-A"}],
        }

        self.assertEqual(
            score_case(reference, prediction),
            {"scalar": 1.0, "mol_f1": 1.0, "ihc_f1": 1.0, "overall": 1.0},
        )

    def test_missing_lists_score_zero_f1(self):
        result = score_case(
            {"label": "a", "molecular": [], "immunohistochemistry": []},
            {"label": "a", "molecular": [], "immunohistochemistry": []},
        )
        self.assertEqual(result["scalar"], 1.0)
        self.assertEqual(result["mol_f1"], 0.0)
        self.assertEqual(result["ihc_f1"], 0.0)
        self.assertEqual(result["overall"], 0.5)

    def test_marker_f1_uses_unique_normalized_names(self):
        reference = [{"marker": "A-1"}, {"marker": "B"}]
        prediction = [{"marker": "a 1"}, {"marker": "A-1"}, {"marker": "C"}]
        self.assertEqual(marker_f1(reference, prediction, "marker"), 0.5)

    def test_loads_wrapped_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "case.json")
            path.write_text(
                json.dumps([{"metadata": {"report_id": "case-001"}}]),
                encoding="utf-8",
            )
            self.assertEqual(load_metadata(path), {"report_id": "case-001"})


if __name__ == "__main__":
    unittest.main()

"""Output schema shared by the English and Japanese prompt profiles."""

SCHEMA = {
    "metadata": {
        "report_id": "string",
        "clinical_context": {
            "patient_age": "string",
            "lesion_location": "string",
            "lesion_laterality": "string",
        },
        "diagnosis": {
            "integrated_diagnosis": "string",
            "who_entity": "string",
            "who_grade": "string",
            "molecular_entity": "string",
            "diagnostic_certainty": "string",
        },
        "histopathology": {
            "growth_pattern": "string",
            "necrosis": "string",
            "microvascular_proliferation": "string",
            "cellular_morphology": "string",
        },
        "proliferation": {
            "ki67_index": "string",
        },
        "molecular": [
            {
                "molecular_marker": "string",
                "molecular_status": "string",
                "molecular_method": "string",
            }
        ],
        "immunohistochemistry": [
            {
                "IHC_marker": "string",
                "IHC_result": "string",
            }
        ],
    }
}

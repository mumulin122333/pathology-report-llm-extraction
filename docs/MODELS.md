# Models

The packaged registry contains the model keys used by the extraction command.

| Key | Label | Model ID |
|---|---|---|
| `qwen38_27b` | Qwen3.8-27B | `Qwen/Qwen3.8-27B` |
| `qwen36_27b` | Qwen3.6-27B | `Qwen/Qwen3.6-27B` |
| `qwen35_27b_bf16` | Qwen3.5-27B | `Qwen/Qwen3.5-27B` |
| `muse_glimmer` | Muse-Glimmer-30B | `meta-models/Muse-Glimmer-30B` |
| `nemotron35` | Nemotron-3.5-30B-A3B | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` |
| `gemma4_26b` | Gemma-4-26B-A4B | `google/gemma-4-26B-A4B-it` |
| `medgemma_27b` | MedGemma-27B-text | `google/medgemma-27b-text-it` |
| `medgemma_15_4b` | MedGemma-1.5-4B | `google/medgemma-1.5-4b-it` |
| `medgemma_4b` | MedGemma-4B | `google/medgemma-4b-it` |

The repository does not distribute model weights. Access requirements and
hardware needs depend on the selected model and serving environment.

Registry defaults use one local port per model. Edit a copy of the registry or
use the CLI endpoint overrides if the local setup is different.

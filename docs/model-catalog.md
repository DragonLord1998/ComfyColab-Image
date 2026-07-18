# Image model catalog

The pack owns six schema-versioned catalogs:

| Catalog | Family | Default |
| --- | --- | --- |
| `z_image_turbo.json` | Z-Image Turbo | `Q4_K_M` |
| `qwen_image_edit_2511.json` | Qwen Image Edit 2511 | `Q4_K_M` |
| `krea_2.json` | Krea 2 | `Turbo FP8` |
| `flux_2_klein_4b.json` | FLUX.2 Klein 4B | `Q4_K_M` |
| `flux_2_klein_9b.json` | FLUX.2 Klein 9B | `Q4_K_M` |
| `flux_2_dev.json` | FLUX.2 Dev | `Q4_K_M` |

Each selection records an immutable Hugging Face revision, destination
filename, byte size, SHA-256, and the required text encoder and VAE.
`catalog.py` rejects malformed records and filename collisions where two
catalogs would publish different bytes to the same component destination.

`scripts/verify_catalogs.py` performs an explicit online comparison against
Hugging Face metadata. Unit tests remain offline and validate the same local
catalog contract without claiming that remote metadata was refreshed.

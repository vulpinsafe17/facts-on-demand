# Local image generation (ComfyUI)

Free pictures on the owner's PC (RTX 5070, 12 GB VRAM, 16 GB RAM). Gemini stays as backup.

## One-time setup
1. ComfyUI Desktop: Manager -> install **ComfyUI-GGUF** (city96). Restart ComfyUI.
2. Download these files into the ComfyUI folder shown (the runner also prints the list if one is missing):

| File | Folder | Size |
|---|---|---|
| [qwen-image-edit-2511-Q3_K_M.gguf](https://huggingface.co/unsloth/Qwen-Image-Edit-2511-GGUF/resolve/main/qwen-image-edit-2511-Q3_K_M.gguf) | `models/unet` | 9.9 GB |
| [qwen_2.5_vl_7b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors) | `models/text_encoders` | 8.7 GB |
| [qwen_image_vae.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors) | `models/vae` | 0.24 GB |
| [Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors](https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning/resolve/main/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors) | `models/loras` | 0.81 GB |

Q3_K_M is the safe size for 12 GB VRAM. If it runs well, try `qwen-image-edit-2511-Q4_0.gguf` (11.9 GB, a bit sharper): the runner picks the biggest one it finds.

## Running a job
- Start ComfyUI, then double-click a `make-*-comfy.bat` in the repo root (e.g. `make-owl-comfy.bat`).
- Pictures that already exist are skipped. Each result gets a `.json` sidecar saying exactly how it was made.
- Same workflow + same reference + same seed = the same picture. To try another look, change that job's `seed` in `comfy/jobs/*.json`.

## Files
- `comfy/workflows/qwen-edit-2511-gguf.json`: the image-edit workflow (API format), built from ComfyUI's official Qwen-Image-Edit-2511 template, Lightning 4 steps.
- `comfy/jobs/*.json`: batches (reference picture, prompts, seeds, output folder).
- `tools/comfy_run.py`: talks to ComfyUI on localhost (port 8000 or 8188). Stdlib only.

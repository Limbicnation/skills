---
name: hugging-face-trainer
description: Train and fine-tune diffusion models (LoRA, DreamBooth) on Hugging Face. Supports FLUX, SDXL, and SD1.5 with optimized configs for different GPU VRAM levels. Use when training image generation models, creating custom LoRAs, fine-tuning diffusion models, or uploading trained models to Hugging Face Hub.
---

# Hugging Face Diffusion Model Trainer

Train custom LoRA adapters for diffusion models (FLUX, SDXL, SD1.5) and upload to Hugging Face Hub.

## Quick Start

### 1. Prepare Training Data

Structure your dataset:
```
dataset/
├── image1.png          # Training images
├── image1.txt          # Captions (same basename)
├── image2.png
├── image2.txt
└── ...
```

Caption format:
```
trigger_word, description of image, style tags
```

### 2. Choose Training Method

| Method | Best For | VRAM | Location |
|--------|----------|------|----------|
| AI-Toolkit | FLUX models | 12GB+ | `./ai-toolkit/` |
| Diffusers | SDXL/SD1.5 | 8GB+ | `train_pixelart_diffusers.py` |
| Custom Trainer | FLUX.2-klein | 16GB+ | `./flux2-klein-lora/` |

### 3. Train with AI-Toolkit (Recommended for FLUX)

```bash
# Create config from template
cp train_pixelart_flux_klein.yaml my_config.yaml

# Edit config for your dataset
# - Update trigger_word
# - Set folder_path to your dataset
# - Adjust steps based on dataset size

# Run training
uv run ./ai-toolkit/run.py my_config.yaml
```

### 4. Upload to Hub

```bash
# Create model repo first
uv run scripts/create_model_repo.py --name "username/my-lora"

# Upload trained weights
uv run scripts/upload_lora.py \
  -- weights ./output/model.safetensors \
  -- repo_id "username/my-lora"
```

## Configuration Templates

### FLUX.1-dev (12GB VRAM)
```yaml
job: extension
config:
  name: "my-flux-lora"
  process:
    - type: 'sd_trainer'
      training_folder: "./output"
      device: cuda:0
      trigger_word: "your trigger"
      network:
        type: "lora"
        linear: 16
        linear_alpha: 16
      save:
        save_every: 500
        push_to_hub: true
        hf_repo_id: username/model-name
      datasets:
        - folder_path: "./training_data"
          caption_ext: "txt"
          resolution: [512, 768]
      train:
        batch_size: 1
        steps: 2000
        gradient_accumulation_steps: 8
        optimizer: "adamw8bit"
        lr: 1e-4
        dtype: bf16
      model:
        name_or_path: "black-forest-labs/FLUX.1-dev"
        is_flux: true
        quantize: true
```

### SDXL (8GB VRAM)
```python
# train_sdxl_lora.py
BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
RESOLUTION = 1024
BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 4
NUM_EPOCHS = 10
LEARNING_RATE = 1e-4
LORA_RANK = 64
```

### SD 1.5 (6GB VRAM)
```python
BASE_MODEL = "runwayml/stable-diffusion-v1-5"
RESOLUTION = 512
BATCH_SIZE = 2
GRADIENT_ACCUMULATION_STEPS = 2
NUM_EPOCHS = 15
LEARNING_RATE = 1e-4
LORA_RANK = 32
```

## Training Parameter Guide

### LoRA Rank
- **Rank 4-8**: Minimal style transfer, small files (~10MB)
- **Rank 16-32**: Good balance for most use cases (~50MB)
- **Rank 64-128**: High fidelity, complex styles (~200MB)
- **Rank 256+**: Near full fine-tune quality (~500MB+)

### Learning Rate
| Model | Recommended LR | Notes |
|-------|---------------|-------|
| FLUX | 1e-4 | Can go up to 2e-4 for small datasets |
| SDXL | 1e-4 | Standard LoRA rate |
| SD 1.5 | 1e-4 to 5e-4 | Higher rates often work |

### Steps vs Epochs
- Small dataset (<50 images): 2000-4000 steps
- Medium dataset (50-200): 1500-2500 steps
- Large dataset (200+): 1000-2000 steps
- Rule: More images = fewer steps needed per image

### Resolution Guidelines
| Model | Min | Recommended | Max |
|-------|-----|-------------|-----|
| FLUX | 512 | 512-1024 | 2048 |
| SDXL | 512 | 1024 | 1536 |
| SD 1.5 | 256 | 512 | 768 |

## Scripts Reference

All scripts use PEP 723 inline dependencies. Run with `uv run script.py`.

### `scripts/create_model_repo.py`
Create a new model repository on Hugging Face Hub.
```bash
uv run scripts/create_model_repo.py \
  --name "username/my-lora" \
  --private  # Optional
```

### `scripts/upload_lora.py`
Upload trained LoRA weights to Hub.
```bash
uv run scripts/upload_lora.py \
  --weights "./output/pytorch_lora_weights.safetensors" \
  --repo_id "username/my-lora" \
  --trigger_word "pixel art sprite" \
  --tags "lora flux pixel-art"
```

### `scripts/estimate_training.py`
Estimate training time and VRAM requirements.
```bash
uv run scripts/estimate_training.py \
  --model "FLUX" \
  --resolution 512 \
  --batch_size 1 \
  --steps 2000
```

## Troubleshooting

### Out of Memory
1. Reduce `batch_size` to 1
2. Enable `gradient_checkpointing: true`
3. Use 8-bit optimizer: `adamw8bit`
4. Enable CPU offloading for FLUX
5. Reduce resolution to 512

### Poor Quality Results
1. **Undertrained**: Increase steps by 50%
2. **Overtrained**: Reduce steps, check loss curve
3. **Weak style**: Increase LoRA rank
4. **Inconsistent**: Check caption quality, add more examples

### Training Crashes
1. Check captions match images (same basename)
2. Verify images load correctly (corruption check)
3. Ensure enough disk space for checkpoints
4. Update diffusers: `pip install -U diffusers`

## Inference After Training

### Python (Diffusers)
```python
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16
).to("cuda")

# Load your LoRA
pipe.load_lora_weights("username/my-lora")

image = pipe(
    "your trigger word, a description",
    num_inference_steps=20,
    guidance_scale=4.0
).images[0]
```

### ComfyUI
1. Download: `huggingface-cli download username/my-lora --local-dir ./loras`
2. Load LoRA node in workflow
3. Use trigger word in prompt

### Automatic1111/Forge
1. Place in `models/Lora/`
2. Select in UI (weight: 0.7-1.0)
3. Include trigger word in prompt

## Advanced Techniques

### Multi-Resolution Training
```yaml
resolution: [512, 768, 1024]  # List of resolutions
```

### Text Encoder Training (SDXL)
```yaml
train_text_encoder: true
text_encoder_lr: 5e-5  # Lower than unet lr
```

### EMA (Exponential Moving Average)
```yaml
ema_config:
  use_ema: true
  ema_decay: 0.99
```

### Sample During Training
```yaml
sample:
  sample_every: 500
  prompts:
    - "trigger, example 1"
    - "trigger, example 2"
  width: 512
  height: 512
```

## Hardware Recommendations

| Use Case | Minimum | Recommended | Ideal |
|----------|---------|-------------|-------|
| SD 1.5 LoRA | GTX 1060 6GB | RTX 3060 12GB | RTX 4090 |
| SDXL LoRA | RTX 3060 12GB | RTX 3090 24GB | A100 40GB |
| FLUX LoRA | RTX 3090 24GB | RTX 4090 24GB | A100 80GB |

## Cloud Training Options

### RunPod
```bash
# Template: PyTorch 2.1 + CUDA 12.1
# GPU: RTX 4090 or A100
# Upload: runpod_train_lora.sh
```

### Google Colab (Free T4)
```python
# Use low VRAM config
# Enable gradient checkpointing
# Batch size 1, grad accum 4
```

### Lambda Labs / Vast.ai
- RTX A6000 (48GB): Good for larger batch sizes
- A100: Fastest training, supports full fine-tuning

---

## Integration with Other Skills

- **hugging-face-datasets**: Prepare training datasets
- Use `dataset_manager.py` to create and populate datasets
- Use `sql_manager.py` to filter/transform existing datasets

---

*Version: 1.0.0*

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "huggingface-hub",
# ]
# ///

"""Upload trained LoRA weights to Hugging Face Hub."""

import argparse
import sys
from pathlib import Path
from huggingface_hub import HfApi, upload_file


def create_model_card(
    repo_id: str,
    trigger_word: str,
    base_model: str,
    tags: list,
    license_type: str = "apache-2.0",
) -> str:
    """Generate a model card for the LoRA."""
    
    default_tags = ["lora", "diffusion", "text-to-image"]
    all_tags = list(dict.fromkeys(default_tags + tags))
    tags_yaml = chr(10).join(f'- {tag}' for tag in all_tags)

    card = f"""---
license: {license_type}
library_name: diffusers
tags:
{tags_yaml}
---

# LoRA Model

This is a LoRA (Low-Rank Adaptation) model for fine-tuning diffusion models.

## Trigger Words

Use the following trigger word in your prompts:

```
{trigger_word}
```

## Base Model

- **Model**: {base_model}
- **Type**: LoRA

## Usage

### With Diffusers

```python
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "{base_model}",
    torch_dtype=torch.float16
).to("cuda")

pipe.load_lora_weights("{repo_id}")

image = pipe(
    "{trigger_word}, your description here",
    num_inference_steps=20,
    guidance_scale=7.5
).images[0]
```

### With ComfyUI

1. Download the model files
2. Place in your `models/loras/` folder
3. Load via LoRA node
4. Use trigger word in prompts

### With Automatic1111/Forge

1. Place in `models/Lora/`
2. Select in UI (recommended weight: 0.7-1.0)
3. Include trigger word in prompt

## Training Details

- **Method**: LoRA
- **Framework**: Diffusers / AI-Toolkit
- **License**: {license_type.upper()}

## Examples

Example prompts:
- `{trigger_word}, a detailed description of your style`
- `{trigger_word}, subject in your trained style`

---

*This model was uploaded using the hugging-face-trainer skill.*
"""
    return card


def main():
    parser = argparse.ArgumentParser(
        description="Upload trained LoRA weights to Hugging Face Hub"
    )
    parser.add_argument(
        "--weights",
        required=True,
        help="Path to LoRA weights file (.safetensors or .bin)",
    )
    parser.add_argument(
        "--repo_id",
        required=True,
        help="Repository ID (username/repo-name)",
    )
    parser.add_argument(
        "--trigger_word",
        default="",
        help="Trigger word for the LoRA",
    )
    parser.add_argument(
        "--base_model",
        default="stabilityai/stable-diffusion-xl-base-1.0",
        help="Base model used for training",
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated tags for the model",
    )
    parser.add_argument(
        "--license",
        default="apache-2.0",
        help="License for the model",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Hugging Face token (or set HF_TOKEN env var)",
    )
    
    args = parser.parse_args()
    
    weights_path = Path(args.weights)
    if not weights_path.exists():
        print(f"❌ Error: Weights file not found: {weights_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        api = HfApi(token=args.token)
        
        print(f"📤 Uploading to {args.repo_id}...")
        
        # Validate file extension
        supported_exts = [".safetensors", ".bin", ".pt", ".pth"]
        ext = weights_path.suffix
        if ext not in supported_exts:
            print(f"❌ Error: Unsupported file format '{ext}'. Supported: {', '.join(supported_exts)}", file=sys.stderr)
            sys.exit(1)
        
        # Upload weights
        print(f"   Uploading {weights_path.name}...")
        api.upload_file(
            path_or_fileobj=str(weights_path),
            path_in_repo=f"model{ext}",
            repo_id=args.repo_id,
            repo_type="model",
        )
        
        # Create and upload model card
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        model_card = create_model_card(
            repo_id=args.repo_id,
            trigger_word=args.trigger_word,
            base_model=args.base_model,
            tags=tags,
            license_type=args.license,
        )
        
        print(f"   Uploading README.md...")
        api.upload_file(
            path_or_fileobj=model_card.encode(),
            path_in_repo="README.md",
            repo_id=args.repo_id,
            repo_type="model",
        )
        
        print(f"✅ Upload complete!")
        print(f"🔗 https://huggingface.co/{args.repo_id}")
        
        if args.trigger_word:
            print(f"\n🎯 Trigger word: '{args.trigger_word}'")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

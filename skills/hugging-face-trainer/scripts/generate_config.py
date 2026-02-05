# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml",
# ]
# ///

"""Generate training configuration files for different models and VRAM levels."""

import argparse
import yaml


CONFIG_TEMPLATES = {
    "FLUX": {
        "job": "extension",
        "config": {
            "name": "flux-lora",
            "process": [{
                "type": "sd_trainer",
                "training_folder": "./output",
                "device": "cuda:0",
                "trigger_word": "your trigger",
                "network": {
                    "type": "lora",
                    "linear": 16,
                    "linear_alpha": 16,
                },
                "save": {
                    "dtype": "float16",
                    "save_every": 500,
                    "max_step_saves_to_keep": 3,
                },
                "datasets": [{
                    "folder_path": "./training_data",
                    "caption_ext": "txt",
                    "caption_dropout_rate": 0.05,
                    "shuffle_tokens": False,
                    "cache_latents_to_disk": True,
                    "resolution": [512, 768],
                }],
                "train": {
                    "batch_size": 1,
                    "steps": 2000,
                    "gradient_accumulation_steps": 8,
                    "train_unet": True,
                    "train_text_encoder": False,
                    "gradient_checkpointing": True,
                    "noise_scheduler": "flowmatch",
                    "optimizer": "adamw8bit",
                    "lr": 1e-4,
                    "dtype": "bf16",
                },
                "model": {
                    "name_or_path": "black-forest-labs/FLUX.1-dev",
                    "is_flux": True,
                    "quantize": True,
                    "low_vram": True,
                },
                "sample": {
                    "sampler": "flowmatch",
                    "sample_every": 500,
                    "width": 512,
                    "height": 512,
                    "prompts": [
                        "your trigger, example prompt 1",
                        "your trigger, example prompt 2",
                    ],
                    "guidance_scale": 4,
                    "sample_steps": 20,
                },
            }],
        },
    },
    "SDXL": {
        "job": "extension",
        "config": {
            "name": "sdxl-lora",
            "process": [{
                "type": "sd_trainer",
                "training_folder": "./output",
                "device": "cuda:0",
                "trigger_word": "your trigger",
                "network": {
                    "type": "lora",
                    "linear": 64,
                    "linear_alpha": 128,
                },
                "save": {
                    "dtype": "float16",
                    "save_every": 500,
                    "max_step_saves_to_keep": 3,
                },
                "datasets": [{
                    "folder_path": "./training_data",
                    "caption_ext": "txt",
                    "caption_dropout_rate": 0.05,
                    "shuffle_tokens": False,
                    "cache_latents_to_disk": True,
                    "resolution": 1024,
                }],
                "train": {
                    "batch_size": 1,
                    "steps": 2000,
                    "gradient_accumulation_steps": 4,
                    "train_unet": True,
                    "train_text_encoder": False,
                    "gradient_checkpointing": True,
                    "noise_scheduler": "ddpm",
                    "optimizer": "adamw",
                    "lr": 1e-4,
                    "dtype": "fp16",
                },
                "model": {
                    "name_or_path": "stabilityai/stable-diffusion-xl-base-1.0",
                },
            }],
        },
    },
}


def generate_config(model: str, vram_gb: int, output_path: str):
    """Generate a training config optimized for the given VRAM."""
    
    if model not in CONFIG_TEMPLATES:
        print(f"Error: Unknown model {model}. Choose from: {list(CONFIG_TEMPLATES.keys())}")
        return False
    
    config = CONFIG_TEMPLATES[model].copy()
    
    # Adjust for VRAM
    train_config = config["config"]["process"][0]["train"]
    model_config = config["config"]["process"][0]["model"]
    
    if model == "FLUX":
        if vram_gb < 16:
            # Low VRAM settings
            train_config["batch_size"] = 1
            train_config["gradient_accumulation_steps"] = 8
            train_config["gradient_checkpointing"] = True
            model_config["quantize"] = True
            model_config["low_vram"] = True
            train_config["optimizer"] = "adamw8bit"
        elif vram_gb < 24:
            # Medium VRAM
            train_config["batch_size"] = 1
            train_config["gradient_accumulation_steps"] = 4
            train_config["gradient_checkpointing"] = True
            model_config["quantize"] = False
            model_config["low_vram"] = False
        else:
            # High VRAM
            train_config["batch_size"] = 2
            train_config["gradient_accumulation_steps"] = 2
            train_config["gradient_checkpointing"] = False
            model_config["quantize"] = False
            model_config["low_vram"] = False
    
    elif model == "SDXL":
        if vram_gb < 12:
            train_config["batch_size"] = 1
            train_config["gradient_accumulation_steps"] = 4
            train_config["gradient_checkpointing"] = True
        elif vram_gb < 16:
            train_config["batch_size"] = 1
            train_config["gradient_accumulation_steps"] = 2
            train_config["gradient_checkpointing"] = True
        else:
            train_config["batch_size"] = 2
            train_config["gradient_accumulation_steps"] = 2
            train_config["gradient_checkpointing"] = False
    
    # Write config
    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Generated {model} config for {vram_gb}GB VRAM")
    print(f"   Batch size: {train_config['batch_size']}")
    print(f"   Gradient accumulation: {train_config['gradient_accumulation_steps']}")
    print(f"   Gradient checkpointing: {train_config['gradient_checkpointing']}")
    print(f"   Saved to: {output_path}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate training configuration files"
    )
    parser.add_argument(
        "--model",
        choices=["FLUX", "SDXL", "SD15"],
        required=True,
        help="Model type",
    )
    parser.add_argument(
        "--vram",
        type=int,
        default=12,
        help="Available VRAM in GB (default: 12)",
    )
    parser.add_argument(
        "--output",
        default="train_config.yaml",
        help="Output file path (default: train_config.yaml)",
    )
    
    args = parser.parse_args()
    
    success = generate_config(args.model, args.vram, args.output)
    
    if success:
        print(f"\n📝 Next steps:")
        print(f"   1. Edit {args.output} to set your trigger_word")
        print(f"   2. Update dataset folder_path")
        print(f"   3. Run training with your config")


if __name__ == "__main__":
    main()

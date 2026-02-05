# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Estimate training time and VRAM requirements for LoRA training."""

import argparse


# VRAM estimates in GB for different models at batch_size=1, resolution=512
VRAM_ESTIMATES = {
    "SD1.5": {"base": 6.0, "per_res_sq": 0.0005, "grad_chkpt": -1.5},
    "SDXL": {"base": 8.0, "per_res_sq": 0.001, "grad_chkpt": -2.0},
    "FLUX": {"base": 12.0, "per_res_sq": 0.002, "grad_chkpt": -3.0, "quantize": -4.0},
    "FLUX2-klein": {"base": 10.0, "per_res_sq": 0.0015, "grad_chkpt": -2.5, "quantize": -3.0},
}

# Seconds per step on different GPUs (approximate)
GPU_SPEED = {
    "GTX 1060": {"SD1.5": 3.0, "SDXL": None, "FLUX": None},
    "RTX 3060": {"SD1.5": 1.5, "SDXL": 3.0, "FLUX": None},
    "RTX 3090": {"SD1.5": 0.5, "SDXL": 1.0, "FLUX": 2.5},
    "RTX 4090": {"SD1.5": 0.3, "SDXL": 0.6, "FLUX": 1.5},
    "A100": {"SD1.5": 0.2, "SDXL": 0.4, "FLUX": 1.0},
    "T4": {"SD1.5": 2.0, "SDXL": 4.0, "FLUX": 8.0},
}


def estimate_vram(model: str, resolution: int, batch_size: int, grad_checkpoint: bool, quantize: bool) -> float:
    """Estimate VRAM usage in GB."""
    if model not in VRAM_ESTIMATES:
        model = "SDXL"  # Default
    
    est = VRAM_ESTIMATES[model]
    vram = est["base"]
    
    # Resolution factor (VRAM scales roughly with resolution squared)
    res_factor = (resolution / 512) ** 2
    vram += est["per_res_sq"] * (resolution ** 2 - 512 ** 2)
    
    # Batch size multiplier
    vram *= batch_size
    
    # Gradient checkpointing saves VRAM
    if grad_checkpoint:
        vram += est.get("grad_chkpt", 0)
    
    # Quantization saves VRAM (FLUX only)
    if quantize and "quantize" in est:
        vram += est["quantize"]
    
    return max(vram, 4.0)  # Minimum 4GB


def estimate_time(model: str, steps: int, gpu: str) -> dict:
    """Estimate training time."""
    if gpu not in GPU_SPEED:
        gpu = "RTX 3090"  # Default
    
    speeds = GPU_SPEED[gpu]
    if model not in speeds or speeds[model] is None:
        return {"seconds_per_step": None, "total_minutes": None, "can_train": False}
    
    sec_per_step = speeds[model]
    total_sec = sec_per_step * steps
    
    return {
        "seconds_per_step": sec_per_step,
        "total_minutes": total_sec / 60,
        "total_hours": total_sec / 3600,
        "can_train": True,
    }


def get_recommendations(model: str, vram_required: float) -> list:
    """Get training recommendations."""
    recommendations = []
    
    if vram_required > 24:
        recommendations.append("⚠️  VRAM requirement exceeds consumer GPUs. Use cloud training (A100).")
    elif vram_required > 16:
        recommendations.append("💡 Enable gradient checkpointing and 8-bit optimizer.")
        recommendations.append("💡 Use batch_size=1 with gradient_accumulation_steps=4+")
    elif vram_required > 12:
        recommendations.append("✅ Trainable on RTX 3090/4090 with optimizations.")
    else:
        recommendations.append("✅ Trainable on most modern GPUs.")
    
    if model == "FLUX":
        recommendations.append("💡 FLUX works best with bf16 dtype.")
        recommendations.append("💡 Consider using AI-Toolkit for automatic optimizations.")
    
    return recommendations


def main():
    parser = argparse.ArgumentParser(
        description="Estimate training time and VRAM requirements"
    )
    parser.add_argument(
        "--model",
        choices=["SD1.5", "SDXL", "FLUX", "FLUX2-klein"],
        default="SDXL",
        help="Model type",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=512,
        help="Training resolution",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Batch size",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=1000,
        help="Number of training steps",
    )
    parser.add_argument(
        "--gpu",
        default="RTX 3090",
        choices=list(GPU_SPEED.keys()),
        help="GPU to estimate for",
    )
    parser.add_argument(
        "--grad_checkpoint",
        action="store_true",
        help="Enable gradient checkpointing",
    )
    parser.add_argument(
        "--quantize",
        action="store_true",
        help="Enable quantization (FLUX only)",
    )
    
    args = parser.parse_args()
    
    print(f"📊 Training Estimation")
    print(f"   Model: {args.model}")
    print(f"   Resolution: {args.resolution}x{args.resolution}")
    print(f"   Batch size: {args.batch_size}")
    print(f"   Steps: {args.steps}")
    print(f"   GPU: {args.gpu}")
    print()
    
    # VRAM estimate
    vram = estimate_vram(
        args.model,
        args.resolution,
        args.batch_size,
        args.grad_checkpoint,
        args.quantize,
    )
    
    print(f"💾 VRAM Estimate: {vram:.1f} GB")
    
    # Time estimate
    time_est = estimate_time(args.model, args.steps, args.gpu)
    
    if time_est["can_train"]:
        print(f"⏱️  Time Estimate:")
        print(f"   {time_est['seconds_per_step']:.1f} sec/step")
        if time_est['total_hours'] >= 1:
            print(f"   Total: {time_est['total_hours']:.1f} hours")
        else:
            print(f"   Total: {time_est['total_minutes']:.0f} minutes")
    else:
        print(f"⏱️  Time Estimate: Not trainable on {args.gpu}")
    
    # Recommendations
    print()
    print("📋 Recommendations:")
    for rec in get_recommendations(args.model, vram):
        print(f"   {rec}")
    
    # Hardware compatibility
    print()
    print("🔧 Hardware Compatibility:")
    for gpu in ["GTX 1060", "RTX 3060", "RTX 3090", "RTX 4090"]:
        gpu_vram = {"GTX 1060": 6, "RTX 3060": 12, "RTX 3090": 24, "RTX 4090": 24}[gpu]
        can_train = gpu_vram >= vram
        status = "✅" if can_train else "❌"
        print(f"   {status} {gpu} ({gpu_vram}GB)")


if __name__ == "__main__":
    main()

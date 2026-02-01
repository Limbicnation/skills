#!/usr/bin/env python3
"""
Generate Synthetic Image Prompts for Diffusion Models

Target Dataset: Limbicnation/Images-Diffusion-Prompt-Style
Compatible Models: Flux, Z Image, Qwen

Usage:
    python scripts/generate_synthetic_image_prompts.py --count 50 --push
    python scripts/generate_synthetic_image_prompts.py --count 10 --dry-run
"""

import os
import json
import argparse
import random
import time
from typing import List, Dict, Any, Optional
from tqdm import tqdm

# Try importing inference clients
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configuration
DEFAULT_MODEL = "Qwen/Qwen2.5-72B-Instruct"
GEMINI_MODEL = "gemini-2.0-flash"
DATASET_REPO = "Limbicnation/Images-Diffusion-Prompt-Style"

# Image-focused seed concepts
IMAGE_SEED_CONCEPTS = [
    # Portraits
    "Ethereal woman with glowing eyes in misty forest",
    "Cyberpunk hacker with neon reflections on face",
    "Old sailor with weathered face and dramatic side lighting",
    "Warrior princess in golden armor at sunset",
    "Street musician playing violin in rain",
    
    # Landscapes
    "Floating islands above clouds at golden hour",
    "Bioluminescent cave with crystal formations",
    "Post-apocalyptic cityscape overgrown with nature",
    "Northern lights over frozen lake reflection",
    "Ancient temple hidden in jungle mist",
    
    # Abstract/Artistic
    "Fractal geometry emerging from liquid metal",
    "Surreal melting clock in endless desert",
    "Prismatic light through crystal sphere",
    "Ink explosion frozen in time",
    "Geometric patterns in sacred architecture",
    
    # Product/Commercial
    "Luxury watch on marble with dramatic shadows",
    "Perfume bottle with ethereal mist and flowers",
    "Minimalist tech device on gradient background",
    "Artisan coffee with latte art steam rising",
    "Handcrafted jewelry on velvet with spotlight",
    
    # Fantasy/Sci-Fi
    "Dragon perched on ancient temple ruins at dusk",
    "Alien marketplace with strange bioluminescent flora",
    "Steampunk airship in stormy crimson sky",
    "Enchanted library with floating glowing books",
    "Robot gardener tending to neon flowers",
    
    # Nature/Wildlife
    "Macro shot of dewdrop on spider web",
    "Owl in flight with moon behind",
    "Coral reef with sunbeams penetrating water",
    "Wolf howling on snowy mountain peak",
    "Butterfly emerging from chrysalis",
    
    # Architecture/Urban
    "Brutalist building in golden hour light",
    "Neon-lit Tokyo alley in rain",
    "Gothic cathedral interior with light rays",
    "Futuristic city skyline at night",
    "Abandoned factory with nature reclaiming",
]

SYSTEM_PROMPT = """You are an expert AI Image Prompt Engineer specializing in diffusion models.
Generate high-quality, structured prompts optimized for Flux, Z Image, and similar models.

Output EXACT JSON (no markdown):
{
  "style_name": "Short descriptive name (e.g., 'Ethereal Portrait', 'Cyberpunk Cityscape')",
  "prompt_text": "Detailed visual description with composition, lighting, mood, and quality tokens. [Style tags] --ar 1:1 --model flux",
  "negative_prompt": "blurry, low quality, watermark, text, deformed, ugly, duplicate",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "compatible_models": ["Flux", "Z Image", "Qwen"]
}

RULES:
1. Focus on COMPOSITION, LIGHTING, TEXTURE, and MOOD (NO camera motion instructions)
2. Include quality tokens: photorealistic, 8k, detailed, masterpiece, sharp focus
3. Use rich descriptive language with sensory details
4. Tags should be lowercase, specific, and useful for filtering
5. Negative prompt should list common artifacts to avoid
6. Model considerations:
   - Flux: Prefers natural, descriptive language with emphasis on style and mood
   - Z Image: Benefits from technical tokens and precise lighting descriptors
7. Output valid JSON only - no markdown formatting"""


def generate_prompt(client, concept: str, model: str) -> Optional[Dict[str, Any]]:
    """Generates a single synthetic image prompt using HF Inference API."""
    try:
        response = client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Generate an image prompt for: {concept}"}
            ],
            max_tokens=600,
            temperature=0.8
        )
        content = response.choices[0].message.content.strip()
        return _parse_json_response(content, concept)
        
    except Exception as e:
        print(f"  ⚠️ Error generating for '{concept[:30]}...': {e}")
        return None


def generate_prompt_gemini(model, concept: str) -> Optional[Dict[str, Any]]:
    """Generates a single synthetic image prompt using Gemini API."""
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nGenerate an image prompt for: {concept}"
        response = model.generate_content(prompt)
        content = response.text.strip()
        return _parse_json_response(content, concept)
        
    except Exception as e:
        print(f"  ⚠️ Gemini error for '{concept[:30]}...': {e}")
        return None


def _parse_json_response(content: str, concept: str) -> Optional[Dict[str, Any]]:
    """Parse and validate JSON from LLM response."""
    try:
        # Clean up potential markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        
        # Validate required fields
        required = ['style_name', 'prompt_text', 'negative_prompt', 'tags', 'compatible_models']
        if not all(k in result for k in required):
            print(f"  ⚠️ Missing fields in response, skipping")
            return None
            
        return result
        
    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON parse error for '{concept[:30]}...': {e}")
        return None


def format_for_flux(prompt: Dict[str, Any]) -> str:
    """Format prompt for Flux model (natural language emphasis)."""
    base = prompt['prompt_text']
    tags = ', '.join(prompt['tags'])
    return f"{base}, {tags}, masterpiece, best quality"


def format_for_zimage(prompt: Dict[str, Any]) -> str:
    """Format prompt for Z Image model (technical tokens)."""
    base = prompt['prompt_text']
    return f"{base} --quality ultra --detail extreme"


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic image prompts for diffusion models"
    )
    parser.add_argument("--count", type=int, default=10, 
                        help="Number of examples to generate")
    parser.add_argument("--push", action="store_true", 
                        help="Push directly to Hugging Face Hub")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate and validate without saving or pushing")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"LLM model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--output", type=str, default="synthetic_image_prompts.json",
                        help="Output JSON file path")
    args = parser.parse_args()
    
    # Load token
    token = os.environ.get("HF_TOKEN")
    if not token:
        # Try loading from .env
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("HF_TOKEN="):
                        token = line.strip().split("=", 1)[1].strip('"').strip("'")
                        break
    
    if not token:
        print("❌ Error: HF_TOKEN not found in environment or .env file")
        exit(1)
    
    client = InferenceClient(token=token)
    
    print(f"🖼️  Image Prompt Generator")
    print(f"   Model: {args.model}")
    print(f"   Target: {args.count} prompts")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()
    
    generated_data = []
    attempts = 0
    max_attempts = args.count * 3  # Allow 3x attempts for failures
    
    pbar = tqdm(total=args.count, desc="Generating")
    while len(generated_data) < args.count and attempts < max_attempts:
        concept = random.choice(IMAGE_SEED_CONCEPTS)
        result = generate_prompt(client, concept, args.model)
        attempts += 1
        
        if result:
            # Add seed for reproducibility
            if "--seed" not in result.get("prompt_text", ""):
                result["prompt_text"] += f" --seed {random.randint(1000, 9999)}"
            
            generated_data.append(result)
            pbar.update(1)
        
        time.sleep(0.5)  # Rate limit protection
    
    pbar.close()
    
    print(f"\n✅ Generated {len(generated_data)}/{args.count} prompts ({attempts} attempts)")
    
    if args.dry_run:
        print("\n📋 DRY RUN - Sample output:")
        for i, item in enumerate(generated_data[:3]):
            print(f"\n--- Sample {i+1} ---")
            print(f"Style: {item['style_name']}")
            print(f"Prompt: {item['prompt_text'][:100]}...")
            print(f"Tags: {item['tags']}")
        return
    
    # Save locally
    with open(args.output, "w") as f:
        json.dump(generated_data, f, indent=2)
    print(f"💾 Saved to {args.output}")
    
    # Push to Hub
    if args.push:
        print(f"\n📤 Pushing to {DATASET_REPO}...")
        try:
            from datasets import load_dataset, Dataset, concatenate_datasets
            
            # Try to append to existing
            try:
                existing_ds = load_dataset(DATASET_REPO, split="train", token=token)
                new_ds = Dataset.from_list(generated_data)
                final_ds = concatenate_datasets([existing_ds, new_ds])
                print(f"   Appending to existing dataset ({len(existing_ds)} + {len(new_ds)} = {len(final_ds)})")
            except Exception:
                print("   Creating new dataset...")
                final_ds = Dataset.from_list(generated_data)
            
            final_ds.push_to_hub(
                DATASET_REPO, 
                token=token,
                commit_message=f"Add {len(generated_data)} synthetic image prompts"
            )
            print("🎉 Successfully pushed to Hub!")
            
        except ImportError:
            print("⚠️ 'datasets' library not installed. Run: pip install datasets")
        except Exception as e:
            print(f"❌ Failed to push to Hub: {e}")


if __name__ == "__main__":
    main()

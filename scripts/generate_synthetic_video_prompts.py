#!/usr/bin/env python3
import os
import json
import argparse
import random
import time
from typing import List, Dict, Any
from huggingface_hub import InferenceClient, HfApi
from tqdm import tqdm

# Configuration
DEFAULT_MODEL = "Qwen/Qwen2.5-72B-Instruct"  # High capability model for structured generation
DATASET_REPO = "Limbicnation/Video-Diffusion-Prompt-Style"

# Seed Concepts (A starter list of diverse visual ideas)
SEED_CONCEPTS = [
    # Sci-Fi / Cyberpunk
    "Cyberpunk street food vendor in heavy rain",
    "Futuristic hospital clean room with robots",
    "Spaceship crash site in a desert",
    "Holographic advertisement malfunctioning",
    "Android getting repaired in a back alley",
    
    # Nature / Documentary
    "Slow motion hummingbird wings",
    "Time-lapse of a flower blooming",
    "Drone shot of a waterfall in Iceland",
    "Lion hunting in tall grass",
    "Underwater coral reef teeming with life",
    
    # Cinematic / Noir
    "Detective walking down a foggy alley",
    "Jazz musician playing saxophone in smoke",
    "Car chase through a tunnel at night",
    "Dramatic courtroom confrontation",
    "Silhouette of a figure in a doorway",
    
    # Abstract / Experimental
    "Ink dropping into water macro shot",
    "Fractal patterns morphing in 3D",
    "Liquid metal flowing uphill",
    "Explosion of colorful powder in slow motion",
    "Light painting in a dark room",
    
    # Fantasy
    "Dragon flying over a medieval castle",
    "Wizard casting a spell with particles",
    "Enchanted forest with glowing mushrooms",
    "Giant walking through a cloud city",
    "Potion brewing in a witch's cauldron",

    # Daily Life / Realism
    "Barista pouring latte art",
    "Skater landing a trick in a park",
    "Busy Tokyo crossing at night",
    "Chef chopping vegetables rapidly",
    "Painter applying brushstrokes to canvas",
    
    # Horror / Thriller
    "Shadow moving in a dark hallway",
    "Abandoned carnival ride creaking",
    "Hand reaching out from under a bed",
    "Flickering light in a basement",
    "Fog rolling over a graveyard"
]

SYSTEM_PROMPT = """You are an expert AI Video Prompt Engineer. 
Your goal is to generate high-quality, structured training data for a Video Diffusion Prompting Dataset.
You will be given a simple concept (e.g., "A car chase").
You must transform it into a sophisticated, highly detailed video prompt following this EXACT JSON structure:

{
  "style_name": "A short, descriptive name for the style (e.g., 'Cinematic Action', 'Macro Nature')",
  "prompt_text": "(Camera/Motion description) The main visual subject description. [Style tags, Lighting, Technical specs] --ar 16:9 --model WanVideo --seed 1234",
  "negative_prompt": "A list of things to avoid (e.g., blurry, static, distorted)",
  "tags": ["tag1", "tag2", "tag3"],
  "compatible_models": ["WanVideo", "Sora", "LTX-Video"]
}

RULES:
1. The 'prompt_text' MUST start with camera/motion instructions in parentheses ().
2. The 'prompt_text' MUST end with style tags in brackets [].
3. The 'prompt_text' MUST include flags like --ar 16:9 and --model.
4. The output must be valid JSON only. No markdown formatting around it.
"""

def generate_prompt(client: InferenceClient, concept: str, model: str) -> Dict[str, Any]:
    """Generates a single synthetic example using the LLM."""
    try:
        response = client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Generate a video prompt for: {concept}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        
        # Clean up potential markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content)
    except Exception as e:
        print(f"Error generating for '{concept}': {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic video prompts")
    parser.add_argument("--count", type=int, default=10, help="Number of examples to generate")
    parser.add_argument("--push", action="store_true", help="Push directly to Hub")
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN environment variable not set.")
        exit(1)

    client = InferenceClient(token=token)
    
    print(f"🚀 Starting generation of {args.count} synthetic examples using {DEFAULT_MODEL}...")
    
    generated_data = []
    
    # Loop until we have enough data
    pbar = tqdm(total=args.count)
    while len(generated_data) < args.count:
        concept = random.choice(SEED_CONCEPTS)
        result = generate_prompt(client, concept, DEFAULT_MODEL)
        
        if result:
            # Add some randomness to flags if not present
            if "--seed" not in result["prompt_text"]:
                 result["prompt_text"] += f" --seed {random.randint(1000, 9999)}"
            
            generated_data.append(result)
            pbar.update(1)
            time.sleep(0.5) # Avoid rate limits
            
    pbar.close()
    
    # Save locally
    output_file = "synthetic_video_prompts.json"
    with open(output_file, "w") as f:
        json.dump(generated_data, f, indent=2)
    print(f"\n✅ Saved {len(generated_data)} examples to {output_file}")

    # Push to Hub
    if args.push:
        print(f"📤 Pushing to {DATASET_REPO}...")
        try:
            # We use the dataset_manager script logic indirectly by just using the API
            # But simpler here to just load and push since we have the JSON
            from datasets import load_dataset, Dataset
            
            # Load existing to append, or create new
            try:
                ds = load_dataset(DATASET_REPO, split="train")
                new_ds = Dataset.from_list(generated_data)
                # Concatenate
                from datasets import concatenate_datasets
                final_ds = concatenate_datasets([ds, new_ds])
            except:
                print("Creating new dataset from scratch (no existing data found or accessible)...")
                final_ds = Dataset.from_list(generated_data)
            
            final_ds.push_to_hub(DATASET_REPO, private=True)
            print("🎉 Successfully pushed to Hub!")
            
        except ImportError:
            print("⚠️ 'datasets' library not installed. Install with: pip install datasets")
        except Exception as e:
            print(f"❌ Failed to push to Hub: {e}")

if __name__ == "__main__":
    main()

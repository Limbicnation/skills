# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "huggingface-hub",
# ]
# ///

"""Create a new model repository on Hugging Face Hub."""

import argparse
import sys
from huggingface_hub import create_repo, HfApi


def main():
    parser = argparse.ArgumentParser(
        description="Create a new model repository on Hugging Face Hub"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Repository name (format: username/repo-name or org/repo-name)",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create private repository",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Hugging Face token (or set HF_TOKEN env var)",
    )
    
    args = parser.parse_args()
    
    try:
        print(f"📦 Creating repository: {args.name}")
        
        repo_url = create_repo(
            repo_id=args.name,
            repo_type="model",
            private=args.private,
            token=args.token,
            exist_ok=True,
        )
        
        print(f"✅ Repository created successfully!")
        print(f"🔗 URL: {repo_url}")
        
        # Get repo info
        api = HfApi(token=args.token)
        repo_info = api.repo_info(repo_id=args.name, repo_type="model")
        
        print(f"\n📋 Repository Info:")
        print(f"   ID: {repo_info.id}")
        print(f"   Private: {repo_info.private}")
        print(f"   URL: https://huggingface.co/{args.name}")
        
        print(f"\n📝 Next steps:")
        print(f"   1. Upload your model files:")
        print(f"      uv run scripts/upload_lora.py --weights ./model.safetensors --repo_id {args.name}")
        print(f"   2. Edit the model card at: https://huggingface.co/{args.name}/edit/main/README.md")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

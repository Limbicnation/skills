# Hugging Face Skills Project Memory

## Environment

- **Conda Environment**: `hf-skills`
- **Python Version**: 3.10
- **Key Dependencies**: `huggingface_hub`, `tqdm`, `datasets`, `requests`
- **Setup Command**: `conda run -n hf-skills pip install huggingface_hub tqdm datasets`

## Tools & Scripts

### Synthetic Prompt Generation

- **Script**: `scripts/generate_synthetic_video_prompts.py`
- **Usage**: `conda run -n hf-skills python scripts/generate_synthetic_video_prompts.py --count <number> --push`
- **Model**: Defaulted to `Qwen/Qwen2.5-72B-Instruct` (requires Hugging Face PRO or Inference Credits).
- **Output**: Generates `synthetic_video_prompts.json` and pushes to `Limbicnation/Video-Diffusion-Prompt-Style` dataset.

## Repositories

- **Source**: `https://github.com/huggingface/skills.git` (origin)
- **Fork**: `https://github.com/Limbicnation/skills.git` (fork)
- **Key Branch**: `prompts-generation` (contains the script and documentation)

## Project State (2026-01-30)

- Successfully generated 500 high-quality prompts.
- Dataset is live on HF Hub.
- Codebase updated with generation script and `.gitignore` refinements.
- Documentation added: `hf-skills-training.md`, `prompt-gen-dataset-plan.md`, `GEMINI.md`.

## Guidelines

- Avoid pushing `.env` or log files (already in `.gitignore`).
- Use the `hf-skills` environment for all script execution.
- Maintain the structured prompt format (Camera instructions in parentheses, style tags in brackets).

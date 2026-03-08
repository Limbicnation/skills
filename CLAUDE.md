# AI Skills Collection — Project Memory

## Environment

- **Conda Environment**: `hf-skills`
- **Python Version**: 3.10
- **Key Dependencies**: `huggingface_hub`, `tqdm`, `datasets`, `requests`
- **Setup Command**: `conda run -n hf-skills pip install huggingface_hub tqdm datasets`

## Repositories

- **Source**: `https://github.com/huggingface/skills.git` (origin)
- **Fork**: `https://github.com/Limbicnation/skills.git` (fork)
- **Active Branches**: `main`, `prompts-generation`, `feat/trainer-skill`

## Custom Skills (contributed to fork)

### hugging-face-trainer
- **Path**: `skills/hugging-face-trainer/`
- **Purpose**: Diffusion model LoRA training via HF Autotrain / training scripts
- **Scripts**: `create_model_repo.py`, `estimate_training.py`, `generate_config.py`, `upload_lora.py`, `validate_dataset.py`
- **Branch**: `feat/trainer-skill` (audited & bug-fixed)

### blender-3d-pipeline
- **Path**: `skills/blender-3d-pipeline/`
- **Purpose**: Blender Python scripting for 3D asset creation, PBR materials, sprite rendering, Godot export
- **Scripts**: `primitives.py`, `materials.py`, `export.py`, `sprite_render.py`

### godot-2d-engine
- **Path**: `skills/godot-2d-engine/`
- **Purpose**: Godot 4 GDScript patterns for 2D game development
- **Scripts**: `gdscript_2d.py`
- **References**: `gdscript_templates.md`, `node_properties.md`

## Tools & Scripts

### Synthetic Prompt Generation
- **Script**: `scripts/generate_synthetic_video_prompts.py`
- **Usage**: `conda run -n hf-skills python scripts/generate_synthetic_video_prompts.py --count <number> --push`
- **Model**: Defaulted to `Qwen/Qwen2.5-72B-Instruct` (requires HF PRO or Inference Credits)
- **Output**: Pushes to `Limbicnation/Video-Diffusion-Prompt-Style` dataset

## Project State (2026-03-02)

- 500 high-quality video prompts generated and live on HF Hub.
- Three custom skills added: `hugging-face-trainer`, `blender-3d-pipeline`, `godot-2d-engine`.
- `feat/trainer-skill` branch: skills audited, bug-fixed, and validated against quality standards.
- Code review completed: reverted broken `.mcp.json` (npx-based HF MCP package doesn't exist on npm), added `anthropic/` to `.gitignore`.
- Documentation: `hf-skills-training.md`, `prompt-gen-dataset-plan.md`, `GEMINI.md`.
- **Next**: Commit cleanup fixes, merge `feat/trainer-skill` into `main`, and push to fork.

## Guidelines

- Avoid pushing `.env` or log files (already in `.gitignore`).
- Use the `hf-skills` environment for all script execution.
- Maintain the structured prompt format (Camera instructions in parentheses, style tags in brackets).
- Follow HF skills standard: each skill needs `SKILL.md`, optional `scripts/`, `references/`, `tests/`.
- **MCP config**: Use upstream URL-based HF MCP (`"url": "https://huggingface.co/mcp?login"`), not npx — the npm package doesn't exist.
- **Local reference repos** (e.g. `anthropic/`) are gitignored — don't commit cloned repos into the tree.

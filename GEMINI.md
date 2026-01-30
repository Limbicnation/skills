# Hugging Face Skills

This repository contains **Hugging Face Skills** — definitions, instructions, and tools designed to supercharge AI agents (like Gemini, Claude, and Codex) with capabilities to interact with the Hugging Face ecosystem.

## Project Overview

The primary goal of this project is to provide a standardized way for AI coding agents to perform complex tasks such as:
*   Managing Hugging Face repositories (Models, Datasets, Spaces).
*   Training and fine-tuning models on cloud infrastructure.
*   Evaluating models and publishing results.
*   Creating and managing datasets.
*   Tracking experiments.

The project is structured as a **Gemini CLI Extension** (via `gemini-extension.json`) and a **Claude Plugin**, making these skills directly installable and usable within your terminal or IDE.

## Directory Structure

*   **`skills/`**: The core of the repository. Each subdirectory represents a distinct skill and contains:
    *   `SKILL.md`: The "prompt" or instruction set for the AI agent.
    *   `scripts/`: Python scripts that the agent can execute to perform tasks.
    *   `templates/`: JSON or Markdown templates used by the skill.
    *   `references/`: Documentation and cheat sheets for the agent.
*   **`apps/`**: Standalone applications (mostly Gradio apps) related to the ecosystem.
    *   `hackers-leaderboard/`: A leaderboard app tracking contributions.
    *   `evals-leaderboard/`: An application for collecting and displaying evaluation results.
    *   `quests/`: Markdown guides for specific challenges/quests.
*   **`agents/`**: Contains `AGENTS.md`, a consolidated definition file for agents that don't support the granular "Skills" format.
*   **`scripts/`**: Maintenance scripts for the repository (e.g., generating the main `AGENTS.md` from individual skills).

## Available Skills

| Skill Directory | Description |
| :--- | :--- |
| `hugging-face-cli` | Automates `hf` CLI operations: auth, download, upload, repo management, and cache control. |
| `hugging-face-datasets` | Tools for creating, configuring, and updating datasets on the Hub, including SQL integration. |
| `hugging-face-evaluation` | workflows for evaluating models (vLLM, lighteval) and posting results to Model Cards. |
| `hugging-face-jobs` | Manages compute jobs (Docker/Python) on Hugging Face infrastructure. |
| `hugging-face-model-trainer` | specialized skill for training/fine-tuning models (TRL, SFT, DPO) on HF hardware. |
| `hugging-face-paper-publisher`| Helpers for publishing research papers to arXiv and the Hub. |
| `hugging-face-tool-builder` | Metatool for creating reusable scripts and API chains. |
| `hugging-face-trackio` | Integration with Trackio for logging and visualizing ML experiments. |

## Usage

### 1. As a Gemini Extension
This repository is configured as a Gemini CLI extension. To install it locally for testing:

```bash
gemini extensions install . --consent
```

Once installed, you can ask Gemini to perform tasks like:
> "Use the hugging-face-cli skill to download the 'gpt2' model."
> "Train a model using the hugging-face-model-trainer skill."

### 2. Developing & Customizing Skills
To add a new skill or modify an existing one:
1.  Create or duplicate a folder in `skills/`.
2.  Edit `SKILL.md` to define the agent's persona and instructions.
3.  Add necessary scripts to `scripts/`.
4.  Run the generation script to update the master lists:

```bash
python scripts/generate_agents.py
```

### 3. Running Applications
The `apps/` directory contains standalone Python applications (Gradio).

**Example: Hackers Leaderboard**
```bash
cd apps/hackers-leaderboard
pip install -r requirements.txt
HF_TOKEN=your_token python app.py
```

**Example: Collecting Points**
```bash
cd apps/hackers-leaderboard
HF_TOKEN=your_token python collect_points.py --scan-external
```

## Key Files
*   `gemini-extension.json`: Configuration file defining this repo as a Gemini extension.
*   `README.md`: Main entry point and documentation.
*   `skills/*/SKILL.md`: The specific instructions for each capability.
*   `agents/AGENTS.md`: Auto-generated fallback file for broader compatibility.

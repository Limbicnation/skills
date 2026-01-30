# Hugging Face Skills Implementation Guide

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Learn to use the 4 Hugging Face skills (dataset-creator, evaluation-manager, model-trainer, paper-publisher) in Claude Code for end-to-end ML workflows.

**Architecture:** Each skill is a self-contained Claude Code plugin with a SKILL.md instruction file and Python scripts in scripts/. Skills use PEP 723 headers for automatic dependency installation via `uv run`.

**Tech Stack:** Claude Code plugins, Python 3.13+, uv package manager, Hugging Face Hub API, TRL (training), lighteval/inspect-ai (evaluation)

---

## Prerequisites

### Task 0: Environment Setup

**Files:**
- Check: `~/.bashrc` or `~/.zshrc` for HF_TOKEN
- Check: Claude Code installed and working

**Step 1: Verify Hugging Face token is set**

Run:
```bash
echo $HF_TOKEN | head -c 10
```
Expected: `hf_` prefix showing (token exists)

If missing, set it:
```bash
export HF_TOKEN="hf_your_token_here"
```

**Step 2: Verify uv is installed**

Run:
```bash
uv --version
```
Expected: `uv 0.x.x` version output

If missing, install:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 3: Verify Claude Code plugin system**

Run in Claude Code:
```
/plugins list
```
Expected: List of installed plugins (may be empty)

---

## Part 1: Installing the Skills

### Task 1: Install Skills from Marketplace

**Step 1: Install all Hugging Face skills**

Run in Claude Code:
```
/plugin marketplace add huggingface/skills
```
Expected: "Plugin added from marketplace"

**Step 2: Install individual skill plugins**

Run in Claude Code:
```
/plugin install hugging-face-dataset-creator@huggingface-skills
/plugin install hugging-face-evaluation-manager@huggingface-skills
/plugin install model-trainer@huggingface-skills
/plugin install hugging-face-paper-publisher@huggingface-skills
```
Expected: Each shows "Plugin installed successfully"

**Step 3: Verify installation**

Run in Claude Code:
```
/plugins list
```
Expected: All 4 Hugging Face skills listed

---

## Part 2: Dataset Creator Skill

### Task 2: Create a Classification Dataset

**Files:**
- Script: `hf_dataset_creator/scripts/dataset_manager.py`
- Reference: `hf_dataset_creator/SKILL.md`

**Step 1: List available templates**

Run:
```bash
cd /home/gero/GitHub/DeepLearning_Lab/skills
uv run hf_dataset_creator/scripts/dataset_manager.py list_templates
```
Expected: Output showing chat, classification, qa, completion, tabular, custom templates

**Step 2: Initialize a new dataset repository**

Run:
```bash
uv run hf_dataset_creator/scripts/dataset_manager.py init \
  --repo_id "YOUR_USERNAME/my-test-dataset" \
  --private
```
Expected: "Dataset repository initialized at https://huggingface.co/datasets/YOUR_USERNAME/my-test-dataset"

**Step 3: Quick setup with classification template**

Run:
```bash
uv run hf_dataset_creator/scripts/dataset_manager.py quick_setup \
  --repo_id "YOUR_USERNAME/my-test-dataset" \
  --template classification \
  --system_prompt "Classify text sentiment as positive, negative, or neutral"
```
Expected: "Configuration saved. Ready to add rows."

**Step 4: Add sample rows**

Run:
```bash
uv run hf_dataset_creator/scripts/dataset_manager.py add_rows \
  --repo_id "YOUR_USERNAME/my-test-dataset" \
  --template classification \
  --rows_json '[{"text": "I love this product!", "label": "positive"}, {"text": "Terrible experience", "label": "negative"}]'
```
Expected: "Added 2 rows to dataset"

**Step 5: Check dataset statistics**

Run:
```bash
uv run hf_dataset_creator/scripts/dataset_manager.py stats \
  --repo_id "YOUR_USERNAME/my-test-dataset"
```
Expected: Row count and column statistics

---

### Task 3: Create a Chat/Conversation Dataset

**Step 1: Initialize for chat format**

Run:
```bash
uv run hf_dataset_creator/scripts/dataset_manager.py quick_setup \
  --repo_id "YOUR_USERNAME/my-chat-dataset" \
  --template chat \
  --system_prompt "You are a helpful coding assistant"
```
Expected: Configuration saved

**Step 2: Add multi-turn conversation**

Run:
```bash
uv run hf_dataset_creator/scripts/dataset_manager.py add_rows \
  --repo_id "YOUR_USERNAME/my-chat-dataset" \
  --template chat \
  --rows_json '[{"messages": [{"role": "user", "content": "How do I reverse a list in Python?"}, {"role": "assistant", "content": "Use list[::-1] or list.reverse()"}]}]'
```
Expected: "Added 1 rows to dataset"

---

## Part 3: Evaluation Manager Skill

### Task 4: Inspect Model Evaluation Tables

**Files:**
- Script: `hf_model_evaluation/scripts/evaluation_manager.py`
- Reference: `hf_model_evaluation/SKILL.md`

**Step 1: Check for existing evaluation PRs (CRITICAL - always do first)**

Run:
```bash
cd /home/gero/GitHub/DeepLearning_Lab/skills
uv run hf_model_evaluation/scripts/evaluation_manager.py get-prs \
  --repo-id "meta-llama/Llama-3.1-8B-Instruct"
```
Expected: List of open PRs (may be empty)

**Step 2: Inspect evaluation tables in model card**

Run:
```bash
uv run hf_model_evaluation/scripts/evaluation_manager.py inspect-tables \
  --repo-id "meta-llama/Llama-3.1-8B-Instruct"
```
Expected: List of numbered tables with headers and row counts

**Step 3: Extract a specific table as YAML (preview mode)**

Run:
```bash
uv run hf_model_evaluation/scripts/evaluation_manager.py extract-readme \
  --repo-id "meta-llama/Llama-3.1-8B-Instruct" \
  --table 1
```
Expected: YAML output showing model-index format (no changes made)

---

### Task 5: Import Scores from Artificial Analysis

**Step 1: Set API key**

Run:
```bash
export AA_API_KEY="your_artificial_analysis_api_key"
```

**Step 2: Preview import (dry run)**

Run:
```bash
uv run hf_model_evaluation/scripts/evaluation_manager.py import-aa \
  --repo-id "YOUR_USERNAME/your-model" \
  --model-name "Your Model Name"
```
Expected: YAML preview of benchmark scores to import

**Step 3: Apply changes via PR**

Run:
```bash
uv run hf_model_evaluation/scripts/evaluation_manager.py import-aa \
  --repo-id "YOUR_USERNAME/your-model" \
  --model-name "Your Model Name" \
  --create-pr
```
Expected: "PR created: https://huggingface.co/YOUR_USERNAME/your-model/discussions/N"

---

### Task 6: Run Custom Model Evaluation

**Step 1: Run evaluation on HF inference providers**

Run:
```bash
uv run hf_model_evaluation/scripts/inspect_eval_uv.py \
  --model "meta-llama/Llama-3.1-8B-Instruct" \
  --tasks "mmlu_pro" \
  --limit 100
```
Expected: Evaluation results with accuracy metrics

**Step 2: Run vLLM-based evaluation (requires GPU)**

Run:
```bash
uv run hf_model_evaluation/scripts/lighteval_vllm_uv.py \
  --model "meta-llama/Llama-3.1-8B-Instruct" \
  --tasks "lighteval|mmlu|5|0" \
  --max-samples 100
```
Expected: Evaluation results from lighteval framework

---

## Part 4: Model Trainer Skill

### Task 7: Validate Dataset Before Training

**Files:**
- Script: `hf-llm-trainer/scripts/dataset_inspector.py`
- Reference: `hf-llm-trainer/SKILL.md`

**Step 1: Inspect dataset format**

Run:
```bash
cd /home/gero/GitHub/DeepLearning_Lab/skills
uv run hf-llm-trainer/scripts/dataset_inspector.py \
  --dataset "HuggingFaceH4/ultrachat_200k" \
  --split "train_sft" \
  --num-samples 5
```
Expected: Sample rows showing messages format, column info

**Step 2: Estimate training cost**

Run:
```bash
uv run hf-llm-trainer/scripts/estimate_cost.py \
  --model "meta-llama/Llama-3.1-8B" \
  --dataset "HuggingFaceH4/ultrachat_200k" \
  --split "train_sft" \
  --num-epochs 1
```
Expected: Estimated GPU hours and cost

---

### Task 8: Run SFT Training (Requires HF Pro Account)

**Step 1: Review training script**

Read: `hf-llm-trainer/scripts/train_sft_example.py`

Key parameters:
- `model_name`: Base model to fine-tune
- `dataset_name`: Training dataset
- `output_dir`: Where to save checkpoints
- `push_to_hub`: MUST be True or results are lost

**Step 2: Submit training job via MCP**

In Claude Code, use the hf_jobs MCP tool:
```
Use hf_jobs() to submit training:
- Script: hf-llm-trainer/scripts/train_sft_example.py
- Hardware: GPU (L4 or better)
- Timeout: 7200 seconds (2 hours minimum)
- Environment: HF_TOKEN set
```
Expected: Job submitted, job ID returned

**Step 3: Monitor training with Trackio**

The training script includes Trackio integration. Check the Trackio dashboard for:
- Loss curves
- Learning rate schedule
- GPU utilization

---

### Task 9: Run DPO Training (Preference Learning)

**Step 1: Prepare preference dataset**

Dataset format required:
```json
{
  "prompt": "User question",
  "chosen": "Better response",
  "rejected": "Worse response"
}
```

**Step 2: Review DPO script**

Read: `hf-llm-trainer/scripts/train_dpo_example.py`

**Step 3: Submit DPO job**

In Claude Code:
```
Use hf_jobs() to submit DPO training:
- Script: hf-llm-trainer/scripts/train_dpo_example.py
- Hardware: GPU (A10G or better for 8B models)
- Timeout: 14400 seconds (4 hours)
```

---

### Task 10: Convert Model to GGUF for Local Use

**Step 1: Run conversion script**

Run:
```bash
uv run hf-llm-trainer/scripts/convert_to_gguf.py \
  --model "YOUR_USERNAME/your-fine-tuned-model" \
  --quantization "Q4_K_M" \
  --output "model.gguf"
```
Expected: GGUF file created for use with llama.cpp, Ollama, etc.

---

## Part 5: Paper Publisher Skill

### Task 11: Index and Link Papers

**Files:**
- Script: `hf-paper-publisher/scripts/paper_manager.py`
- Reference: `hf-paper-publisher/SKILL.md`

**Step 1: Check if paper exists on Hub**

Run:
```bash
cd /home/gero/GitHub/DeepLearning_Lab/skills
uv run hf-paper-publisher/scripts/paper_manager.py check \
  --arxiv-id "2301.12345"
```
Expected: "Paper exists" or "Paper not found"

**Step 2: Index paper from arXiv**

Run:
```bash
uv run hf-paper-publisher/scripts/paper_manager.py index \
  --arxiv-id "2301.12345"
```
Expected: "Paper indexed: https://huggingface.co/papers/2301.12345"

**Step 3: Link paper to your model**

Run:
```bash
uv run hf-paper-publisher/scripts/paper_manager.py link \
  --repo-id "YOUR_USERNAME/your-model" \
  --repo-type "model" \
  --arxiv-id "2301.12345"
```
Expected: "Paper linked to model repository"

---

## Part 6: Complete ML Workflow

### Task 12: End-to-End Example

This task combines all 4 skills into a complete workflow.

**Step 1: Create training dataset**

```bash
# Initialize dataset
uv run hf_dataset_creator/scripts/dataset_manager.py quick_setup \
  --repo_id "YOUR_USERNAME/my-sft-dataset" \
  --template chat \
  --system_prompt "You are a helpful assistant"

# Add training examples (repeat for your data)
uv run hf_dataset_creator/scripts/dataset_manager.py add_rows \
  --repo_id "YOUR_USERNAME/my-sft-dataset" \
  --template chat \
  --rows_json '[{"messages": [...]}]'
```

**Step 2: Validate dataset**

```bash
uv run hf-llm-trainer/scripts/dataset_inspector.py \
  --dataset "YOUR_USERNAME/my-sft-dataset" \
  --split "train"
```

**Step 3: Train model (via Claude Code MCP)**

```
Submit SFT training job with:
- Dataset: YOUR_USERNAME/my-sft-dataset
- Base model: meta-llama/Llama-3.1-8B
- Output: YOUR_USERNAME/my-fine-tuned-model
```

**Step 4: Evaluate trained model**

```bash
uv run hf_model_evaluation/scripts/evaluation_manager.py inspect-tables \
  --repo-id "YOUR_USERNAME/my-fine-tuned-model"

# Run evaluation
uv run hf_model_evaluation/scripts/inspect_eval_uv.py \
  --model "YOUR_USERNAME/my-fine-tuned-model" \
  --tasks "mmlu_pro"
```

**Step 5: Publish paper (if applicable)**

```bash
uv run hf-paper-publisher/scripts/paper_manager.py link \
  --repo-id "YOUR_USERNAME/my-fine-tuned-model" \
  --repo-type "model" \
  --arxiv-id "YOUR_ARXIV_ID"
```

---

## Quick Reference

| Skill | Main Command | Key Flag |
|-------|--------------|----------|
| Dataset Creator | `dataset_manager.py add_rows` | `--template` |
| Evaluation Manager | `evaluation_manager.py extract-readme` | `--create-pr` |
| Model Trainer | `train_sft_example.py` | `push_to_hub=True` |
| Paper Publisher | `paper_manager.py link` | `--arxiv-id` |

**Critical Reminders:**
1. Always check for existing PRs before creating new ones (evaluation)
2. Always set `push_to_hub=True` in training (or results are lost)
3. Always validate datasets before GPU training
4. Set TIMEOUT > 2 hours for training jobs

---

## Troubleshooting

**"HF_TOKEN not set"**
```bash
export HF_TOKEN="hf_your_token_here"
```

**"uv: command not found"**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**"Permission denied on Hub"**
- Verify token has write access
- Check repository exists
- Verify you're the owner or have collaborator access

**"Training job timeout"**
- Increase timeout to minimum 7200 seconds (2 hours)
- Use smaller dataset for initial tests
- Enable checkpointing for recovery

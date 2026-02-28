---
name: git-commit-branch
description: Commit changes to a new git branch without AI attribution in commit messages. Use when the user wants to commit current changes to a new branch, create a feature branch with commits, or save work to a new branch.
---

# Git Commit to New Branch

Commit current changes to a newly created git branch.

## Workflow

1. **Check git status** - Verify there are changes to commit
2. **Create new branch** - Use a descriptive branch name based on the changes
3. **Stage and commit** - Write a clean, professional commit message
4. **Push if needed** - Push the new branch to remote

## Branch Naming

Use descriptive names following common conventions:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `update/description` - Updates/refactors
- `docs/description` - Documentation changes

## Commit Message Guidelines

Write commit messages that:
- Describe what changed and why
- Use imperative mood ("Add", "Fix", "Update")
- Are concise but descriptive
- **Do NOT mention AI tools, assistants, or automated generation**
- Keep first line under 50 characters

### Examples

**Good:**
```
Add user authentication middleware

Implement JWT-based auth with refresh tokens
```

**Bad:**
```
Claude added authentication
```

## Command Reference

```bash
# Check status
git status

# Create and switch to new branch
git checkout -b <branch-name>

# Stage all changes
git add -A

# Commit with message
git commit -m "<message>"

# Push new branch
git push -u origin <branch-name>
```

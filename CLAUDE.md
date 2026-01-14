# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

**Project**: MovieBot
**Status**: Initial setup, BDD-first development
**Stack**: Python 3.10+ with pytest-bdd for BDD testing

## Project Requirements

- [ ] GitHub repository
- [ ] README with description and run instructions
- [ ] CLAUDE.md describing AI collaboration
- [ ] BDD .feature files (pytest-bdd)
- [ ] Tests run and pass
- [ ] Every new feature has own commit
- [ ] MVP works and solves the problem

## Core Principles

### BDD-First Development
1. Write .feature files FIRST
2. Generate step definitions
3. Implement code to pass tests
4. Commit frequently (every 15-20 min)

### Simplicity First
- Write straightforward, readable code
- Prefer clarity over cleverness
- Minimal changes focused on current task
- Early returns to avoid nesting
- DRY - don't repeat yourself

### Before Any Code Changes
1. Read and understand existing code first
2. Never modify code you haven't read
3. Check existing patterns and conventions

## Commit Rules

- Atomic commits - one logical change per commit
- Conventional format: `type(scope): description`
- Examples:
  - `feat(bot): add movie search`
  - `test(search): add search scenarios`
  - `docs(readme): add setup instructions`

## Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run all BDD tests
pytest tests/ -v

# Run specific feature
pytest tests/ -v -k "feature_name"

# Run with coverage
pytest tests/ --cov=src
```

## Project Structure

```
MovieBot/
├── README.md           # Description + how to run
├── CLAUDE.md           # AI collaboration notes
├── requirements.txt    # Dependencies
├── src/
│   └── ...            # Application code
├── tests/
│   ├── features/      # BDD .feature files
│   └── steps/         # Step definitions
└── .gitignore
```

## AI Collaboration Log

### Session 1 (2026-01-14)
- Initial project setup
- Created project structure
- BDD scenarios pending from user

---

*Update this file as project evolves*

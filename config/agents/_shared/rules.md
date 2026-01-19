---
trigger: always_on
priority: 100
---

# Global Rules

## Language Requirements
- All code comments, docstrings, log messages, and git commit subjects MUST be in **English**.
- Follow Google Python Style Guide for all Python code.

## Code Quality Standards
- All function signatures MUST include type hints.
- Use Google-style docstrings for all public modules, functions, classes, and methods.
- Files should ideally be under 1000 lines.

## Reproducibility
- Always include code to lock random seeds (PyTorch, NumPy, Python random) for stochastic algorithms.
- No silent failures - explicitly raise exceptions instead of using default values to mask errors.

## Naming Conventions
- Use physical/mathematical meaning (e.g., `synaptic_weight`, `angular_velocity`) over generic names.
- Prefer vectorized operations over explicit loops in NumPy/PyTorch contexts.

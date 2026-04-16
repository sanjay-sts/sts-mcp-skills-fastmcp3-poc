---
name: project-scaffolding
description: >
  Scaffold new projects from templates with proper structure, config,
  and boilerplate. Use when creating new Python packages, FastAPI services,
  CLI tools, or MCP servers. Generates directory structure, config files,
  and starter code. NOT for modifying existing projects.
compatibility: Requires Python 3.10+
metadata:
  author: sanjay-sts
  version: "1.0"
  tags: "scaffolding,project,template,generator"
---

# Project Scaffolding

## Instructions

### Available Templates
Read `references/templates-guide.md` for the full list of templates and when to use each.

### Workflow

1. Ask the user which template they want (or infer from context)
2. Read `references/templates-guide.md` for template details
3. Run the scaffold script to generate the project:
   ```bash
   uv run scripts/scaffold.py --template <template-name> --name <project-name> --output <directory>
   ```
4. Review the generated structure with the user
5. Customize generated files based on user requirements

### Template Data
The template definitions are in `assets/project-template.json`. The scaffold script reads this file to determine what files and directories to create.

### Script Help
```bash
uv run scripts/scaffold.py --help
```

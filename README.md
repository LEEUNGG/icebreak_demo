# LangGraph Workspace

A workspace containing multiple LangGraph-based projects. You can place your own LangGraph projects here as subfolders.

## Project Structure

- **ice_break_agent/**: Original IceBreak demo project (an AI conversation agent with modes and scripted branches)
- **personality_agent/**: Code for a personality-driven agent
- **common/**: Shared models and utilities
- **langgraph_academy/**: Notebooks and sample graphs for learning LangGraph (modules 0–6)
- **other_script/**: Auxiliary scripts (e.g., content generation workflows) and sample outputs

## Requirements

- Python 3.11 or later is recommended
- See `requirements.txt` for core dependencies (LangGraph, LangChain, etc.)

## Installation

```bash
pip install -r requirements.txt
```

If you use `pyproject.toml`, you can also install with your preferred build tool (e.g., `pip`, `uv`, or `poetry`).

## Usage

1. Optionally rename the root folder to whatever you like (e.g., `langgraph-projects`).
2. Add your own LangGraph projects as subfolders under the root.
3. Ensure each subproject includes its own configuration and any extra dependencies.

## Running

Run each subproject according to its own `README` or `main.py` entry point. For example, within a subproject:

```bash
python main.py
```

For the materials in `langgraph_academy/`, open the notebooks with Jupyter, or launch the LangGraph Studio projects inside each `studio/` directory as documented there.
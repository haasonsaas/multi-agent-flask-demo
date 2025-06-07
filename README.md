# Multi-Agent Python Data Processing Demo

This project demonstrates how to use multiple AI agents working in parallel using git worktrees, as described in claude.md.

## Overview

The project includes:
- A parallelizable web scraping and data analysis task
- Automatic git worktree setup for agent isolation
- Work distribution across multiple agents
- Results collection and aggregation
- Performance analysis and visualization

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the multi-agent system:
```bash
python launch_agents.py
```

Or with custom URLs:
```bash
python launch_agents.py https://example1.com https://example2.com ...
```

3. Analyze results:
```bash
python aggregate_results.py
```

## How It Works

1. **Agent Setup**: Creates separate git worktrees for each agent (default: 4 agents)
2. **Work Distribution**: Divides URLs equally among agents
3. **Parallel Processing**: Each agent processes its assigned URLs independently
4. **Results Collection**: Aggregates results from all agents
5. **Cleanup**: Removes worktrees and branches after completion

## File Structure

- `data_processor.py` - Core processing logic for each agent
- `launch_agents.py` - Multi-agent orchestration
- `aggregate_results.py` - Results analysis and visualization
- `claude.md` - Multi-agent development guidelines
- `results/` - Output directory for all results

## Agent Isolation

Each agent works in its own git worktree with:
- Separate branch (agent-1, agent-2, etc.)
- Independent working directory
- Isolated results storage
- No conflicts between agents

## Example Output

Agents process URLs in parallel and generate:
- Web scraping results (title, links, images)
- Content analysis metrics
- Performance statistics
- Combined JSON results
- Visual analysis report
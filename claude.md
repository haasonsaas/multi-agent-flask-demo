# Multi-Agent AI Development with Git Worktrees

## When to Use Multi-Agent Approach
- Task success rate per agent < 50%
- Task can be parallelized (no interdependencies)
- Cost of running 4 agents < value of time saved
- Use 4 agents minimum for statistical advantage (68% vs 25% success rate)

## Agent Workspace Setup
```bash
# Create isolated worktree for this agent
git worktree add -b agent-{id} ../$(basename $PWD)-agent-{id}
cd ../$(basename $PWD)-agent-{id}

# Verify isolation
git status  # Should show clean working tree
git branch  # Should show agent-{id} branch
```

## Development Server Management
- Assign unique port: BASE_PORT + agent_id (e.g., 3001, 3002, 3003)
- Start server: `PORT={assigned_port} npm run dev`
- Verify no port conflicts before starting

## Agent Coordination Rules
- Never modify main branch directly
- Use branch naming: `agent-{id}` or `agent-{id}/{feature}`
- Commit frequently with clear messages: "Agent-{id}: {description}"
- Check for conflicts before merging: `git fetch && git rebase main`

## Integration Process
```bash
# Before merging
git checkout main
git pull origin main
git checkout agent-{id}
git rebase main

# If successful, merge
git checkout main
git merge --no-ff agent-{id}
git push origin main

# Cleanup
git branch -D agent-{id}
git worktree remove ../$(basename $PWD)-agent-{id}
```

## File Collision Prevention
- Check `git worktree list` before starting work
- Avoid modifying shared config files simultaneously
- Focus on isolated modules/components when possible
- Use sparse checkout if working on specific directories:
```bash
git config core.sparseCheckout true
echo "src/components/*" > .git/info/sparse-checkout
git read-tree -m -u HEAD
```

## Status Monitoring
```bash
# Check all agent branches
git for-each-ref --format='%(refname:short) %(committerdate:short)' refs/heads/agent-*

# Check worktree status
git worktree list

# Verify development servers
lsof -ti:3001,3002,3003,3004
```

## Error Recovery
- If worktree corrupted: `git worktree remove {path} --force && git worktree add -b agent-{id} {path}`
- If branch conflicts: `git reset --hard main && git clean -fd`
- If port occupied: Increment port number and retry

## Agent Communication
- Broadcast identical prompts to all agents initially
- Share context through git commit messages
- Use branch names to indicate work areas
- No shared state files - use git history only

## Success Criteria
- At least one agent produces working solution
- Solution passes basic tests/validation
- Code integrates cleanly with main branch
- No merge conflicts or broken dependencies
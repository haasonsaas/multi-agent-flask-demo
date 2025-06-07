#!/usr/bin/env python3

import subprocess
import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict
import shutil


class MultiAgentLauncher:
    def __init__(self, num_agents: int = 4):
        self.num_agents = num_agents
        self.base_dir = Path.cwd()
        self.project_name = self.base_dir.name
        
    def setup_git_worktrees(self):
        print("Setting up git worktrees for agents...")
        
        # First, make initial commit
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        worktree_paths = []
        
        for agent_id in range(1, self.num_agents + 1):
            branch_name = f"agent-{agent_id}"
            worktree_path = self.base_dir.parent / f"{self.project_name}-agent-{agent_id}"
            
            # Remove existing worktree if it exists
            if worktree_path.exists():
                subprocess.run(["git", "worktree", "remove", str(worktree_path), "--force"])
            
            # Create new worktree
            subprocess.run([
                "git", "worktree", "add", "-b", branch_name, 
                str(worktree_path)
            ], check=True)
            
            print(f"Created worktree for Agent {agent_id} at {worktree_path}")
            worktree_paths.append(worktree_path)
            
        return worktree_paths
    
    def distribute_work(self, urls: List[str]) -> Dict[int, List[str]]:
        chunk_size = len(urls) // self.num_agents
        remainder = len(urls) % self.num_agents
        
        distribution = {}
        start = 0
        
        for agent_id in range(1, self.num_agents + 1):
            end = start + chunk_size + (1 if agent_id <= remainder else 0)
            distribution[agent_id] = urls[start:end]
            start = end
            
        return distribution
    
    def launch_agent(self, agent_id: int, worktree_path: Path, urls: List[str]):
        print(f"\nLaunching Agent {agent_id} with {len(urls)} URLs...")
        
        # Create agent-specific task file
        task_file = worktree_path / f"agent_{agent_id}_task.json"
        with open(task_file, 'w') as f:
            json.dump({
                'agent_id': agent_id,
                'urls': urls,
                'timestamp': time.time()
            }, f, indent=2)
        
        # Run the data processor in the worktree
        cmd = [
            sys.executable, 
            "data_processor.py", 
            str(agent_id)
        ] + urls
        
        process = subprocess.Popen(
            cmd,
            cwd=str(worktree_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
    
    def collect_results(self, worktree_paths: List[Path]):
        print("\nCollecting results from all agents...")
        
        all_results = []
        
        for i, worktree_path in enumerate(worktree_paths):
            agent_id = i + 1
            results_dir = worktree_path / f"results/agent_{agent_id}"
            
            if results_dir.exists():
                for result_file in results_dir.glob("*.json"):
                    with open(result_file, 'r') as f:
                        results = json.load(f)
                        all_results.extend(results)
        
        # Save combined results
        os.makedirs("results", exist_ok=True)
        output_file = f"results/combined_results_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"Combined results saved to {output_file}")
        return output_file
    
    def cleanup_worktrees(self, worktree_paths: List[Path]):
        print("\nCleaning up worktrees...")
        
        for i, worktree_path in enumerate(worktree_paths):
            agent_id = i + 1
            branch_name = f"agent-{agent_id}"
            
            # Remove worktree
            subprocess.run(["git", "worktree", "remove", str(worktree_path), "--force"])
            
            # Delete branch
            subprocess.run(["git", "branch", "-D", branch_name])
            
        print("Cleanup completed")


def main():
    # Example URLs to process
    urls = [
        "https://example.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://python.org",
        "https://numpy.org",
        "https://pandas.pydata.org",
        "https://matplotlib.org",
        "https://scikit-learn.org"
    ]
    
    if len(sys.argv) > 1:
        # Allow custom URLs from command line
        urls = sys.argv[1:]
    
    launcher = MultiAgentLauncher(num_agents=4)
    
    try:
        # Setup worktrees
        worktree_paths = launcher.setup_git_worktrees()
        
        # Distribute work
        work_distribution = launcher.distribute_work(urls)
        
        # Launch agents
        processes = []
        for agent_id, agent_urls in work_distribution.items():
            process = launcher.launch_agent(
                agent_id, 
                worktree_paths[agent_id - 1], 
                agent_urls
            )
            processes.append(process)
        
        # Wait for all agents to complete
        print("\nWaiting for agents to complete...")
        for i, process in enumerate(processes):
            stdout, stderr = process.communicate()
            print(f"\nAgent {i+1} output:")
            print(stdout)
            if stderr:
                print(f"Agent {i+1} errors: {stderr}")
        
        # Collect results
        launcher.collect_results(worktree_paths)
        
    finally:
        # Cleanup
        launcher.cleanup_worktrees(worktree_paths)


if __name__ == "__main__":
    main()
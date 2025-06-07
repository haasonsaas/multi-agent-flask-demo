import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List
import numpy as np


class ResultsAggregator:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        
    def load_combined_results(self) -> List[Dict]:
        latest_file = max(self.results_dir.glob("combined_results_*.json"), 
                         key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def analyze_agent_performance(self, results: List[Dict]):
        df = pd.DataFrame(results)
        
        # Agent performance summary
        agent_summary = df.groupby('agent_id').agg({
            'url': 'count',
            'error': lambda x: x.notna().sum()
        }).rename(columns={'url': 'total_processed', 'error': 'errors'})
        
        agent_summary['success_rate'] = (
            (agent_summary['total_processed'] - agent_summary['errors']) / 
            agent_summary['total_processed'] * 100
        )
        
        return agent_summary
    
    def analyze_content_metrics(self, results: List[Dict]):
        successful_results = [r for r in results if 'error' not in r]
        
        if not successful_results:
            return None
        
        metrics = []
        for result in successful_results:
            if 'analysis' in result:
                metrics.append({
                    'url': result['url'],
                    'agent_id': result['agent_id'],
                    'content_density': result['analysis']['content_density'],
                    'media_ratio': result['analysis']['media_ratio'],
                    'header_count': result['analysis']['header_count']
                })
        
        return pd.DataFrame(metrics)
    
    def generate_report(self):
        results = self.load_combined_results()
        
        print("=" * 50)
        print("MULTI-AGENT PROCESSING REPORT")
        print("=" * 50)
        
        # Agent performance
        agent_perf = self.analyze_agent_performance(results)
        print("\nAgent Performance Summary:")
        print(agent_perf)
        
        # Content metrics
        content_df = self.analyze_content_metrics(results)
        if content_df is not None:
            print("\nContent Metrics Summary:")
            print(content_df.describe())
            
            # Visualizations
            self.create_visualizations(agent_perf, content_df)
        
        # Processing time analysis
        self.analyze_processing_times(results)
        
    def create_visualizations(self, agent_perf: pd.DataFrame, content_df: pd.DataFrame):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Agent success rates
        ax = axes[0, 0]
        agent_perf['success_rate'].plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Agent Success Rates')
        ax.set_xlabel('Agent ID')
        ax.set_ylabel('Success Rate (%)')
        
        # Content density by agent
        ax = axes[0, 1]
        content_df.boxplot(column='content_density', by='agent_id', ax=ax)
        ax.set_title('Content Density Distribution by Agent')
        
        # Media ratio distribution
        ax = axes[1, 0]
        content_df['media_ratio'].hist(bins=20, ax=ax, color='lightgreen')
        ax.set_title('Media Ratio Distribution')
        ax.set_xlabel('Media Ratio')
        
        # Header count by URL
        ax = axes[1, 1]
        url_headers = content_df.groupby('url')['header_count'].mean()
        url_headers.plot(kind='bar', ax=ax, color='coral')
        ax.set_title('Average Header Count by URL')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig('results/analysis_report.png', dpi=300, bbox_inches='tight')
        print("\nVisualization saved to results/analysis_report.png")
        
    def analyze_processing_times(self, results: List[Dict]):
        from datetime import datetime
        
        timestamps = []
        for result in results:
            if 'timestamp' in result:
                timestamps.append({
                    'agent_id': result['agent_id'],
                    'time': datetime.fromisoformat(result['timestamp'])
                })
        
        if timestamps:
            df = pd.DataFrame(timestamps)
            processing_times = df.groupby('agent_id').agg({
                'time': ['min', 'max']
            })
            
            processing_times['duration'] = (
                processing_times[('time', 'max')] - 
                processing_times[('time', 'min')]
            ).dt.total_seconds()
            
            print("\nProcessing Time by Agent (seconds):")
            print(processing_times['duration'])


if __name__ == "__main__":
    aggregator = ResultsAggregator()
    aggregator.generate_report()
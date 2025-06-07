# import pandas as pd
# import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os
import sys
from typing import List, Dict, Any


class DataProcessor:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.results_dir = f"results/agent_{agent_id}"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def process_urls(self, urls: List[str]) -> Dict[str, Any]:
        results = []
        
        for url in urls:
            print(f"Agent {self.agent_id}: Processing {url}")
            try:
                data = self._scrape_url(url)
                analysis = self._analyze_data(data)
                results.append({
                    'url': url,
                    'data': data,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat(),
                    'agent_id': self.agent_id
                })
            except Exception as e:
                print(f"Agent {self.agent_id}: Error processing {url}: {e}")
                results.append({
                    'url': url,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'agent_id': self.agent_id
                })
        
        return results
    
    def _scrape_url(self, url: str) -> Dict[str, Any]:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return {
            'title': soup.title.string if soup.title else 'No title',
            'text_length': len(soup.get_text()),
            'num_links': len(soup.find_all('a')),
            'num_images': len(soup.find_all('img')),
            'headers': [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]
        }
    
    def _analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'content_density': data['text_length'] / (data['num_links'] + 1),
            'media_ratio': data['num_images'] / (data['num_links'] + data['num_images'] + 1),
            'header_count': len(data['headers']),
            'avg_header_length': sum([len(h) for h in data['headers']]) / len(data['headers']) if data['headers'] else 0
        }
    
    def save_results(self, results: List[Dict[str, Any]]):
        output_file = f"{self.results_dir}/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Agent {self.agent_id}: Results saved to {output_file}")
        return output_file


def process_chunk(agent_id: int, urls: List[str]):
    processor = DataProcessor(agent_id)
    results = processor.process_urls(urls)
    output_file = processor.save_results(results)
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python data_processor.py <agent_id> <url1> [url2] ...")
        sys.exit(1)
    
    agent_id = int(sys.argv[1])
    urls = sys.argv[2:]
    
    print(f"Starting Agent {agent_id} with {len(urls)} URLs")
    output_file = process_chunk(agent_id, urls)
    print(f"Agent {agent_id} completed. Results in {output_file}")
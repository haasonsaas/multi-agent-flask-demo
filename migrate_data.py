"""
Script to migrate existing JSON results from data_processor.py output to SQLite database.
"""
import json
import os
import glob
from datetime import datetime
from typing import List, Dict, Any
import argparse
from database import Database, init_database
from models import ScrapingResult


class DataMigrator:
    """Handles migration of JSON data to SQLite database."""
    
    def __init__(self, db_path: str = "dashboard.db"):
        """Initialize the migrator with database connection."""
        self.db = Database(db_path)
        
    def find_json_files(self, results_dir: str = "results") -> List[str]:
        """Find all JSON result files in the results directory."""
        pattern = os.path.join(results_dir, "**", "*.json")
        json_files = glob.glob(pattern, recursive=True)
        return sorted(json_files)
    
    def parse_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse a JSON file and return the results."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Handle both single result and list of results
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                print(f"Warning: Unexpected data format in {file_path}")
                return []
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
    
    def transform_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a JSON result to match the database schema."""
        # Parse timestamp
        timestamp_str = result.get('timestamp', '')
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            timestamp = datetime.utcnow()
        
        # Extract data fields
        data = result.get('data', {})
        analysis = result.get('analysis', {})
        
        # Build the database record
        db_record = {
            'url': result.get('url', ''),
            'agent_id': result.get('agent_id', 0),
            'timestamp': timestamp,
            'error': result.get('error', None)
        }
        
        # Add scraped data if no error
        if not db_record['error'] and data:
            db_record.update({
                'title': data.get('title', 'No title'),
                'text_length': data.get('text_length', 0),
                'num_links': data.get('num_links', 0),
                'num_images': data.get('num_images', 0),
                'headers': data.get('headers', [])
            })
            
            # Add analysis results
            if analysis:
                db_record.update({
                    'content_density': analysis.get('content_density', 0.0),
                    'media_ratio': analysis.get('media_ratio', 0.0),
                    'header_count': analysis.get('header_count', 0),
                    'avg_header_length': analysis.get('avg_header_length', 0.0)
                })
        
        return db_record
    
    def migrate_file(self, file_path: str, skip_duplicates: bool = True) -> int:
        """Migrate a single JSON file to the database."""
        print(f"Processing {file_path}...")
        results = self.parse_json_file(file_path)
        
        if not results:
            return 0
        
        migrated_count = 0
        skipped_count = 0
        
        for result in results:
            try:
                # Transform the result
                db_record = self.transform_result(result)
                
                # Check for duplicates if requested
                if skip_duplicates:
                    existing = self.db.get_results_by_url(db_record['url'])
                    if existing:
                        # Check if we already have this exact result
                        duplicate = any(
                            r.agent_id == db_record['agent_id'] and 
                            abs((r.timestamp - db_record['timestamp']).total_seconds()) < 60
                            for r in existing
                        )
                        if duplicate:
                            skipped_count += 1
                            continue
                
                # Create the database record
                self.db.create_scraping_result(db_record)
                migrated_count += 1
                
            except Exception as e:
                print(f"Error migrating result for {result.get('url', 'unknown')}: {e}")
        
        print(f"  Migrated: {migrated_count}, Skipped: {skipped_count}")
        return migrated_count
    
    def migrate_all(self, results_dir: str = "results", skip_duplicates: bool = True) -> Dict[str, int]:
        """Migrate all JSON files from the results directory."""
        # Initialize database
        self.db.init_db()
        
        # Find all JSON files
        json_files = self.find_json_files(results_dir)
        
        if not json_files:
            print(f"No JSON files found in {results_dir}")
            return {'files': 0, 'records': 0}
        
        print(f"Found {len(json_files)} JSON files to migrate")
        
        total_migrated = 0
        for file_path in json_files:
            migrated = self.migrate_file(file_path, skip_duplicates)
            total_migrated += migrated
        
        # Update agent statistics
        print("\nUpdating agent statistics...")
        unique_agents = set()
        with self.db.get_session() as session:
            agent_ids = session.query(ScrapingResult.agent_id).distinct().all()
            unique_agents = {aid[0] for aid in agent_ids}
        
        for agent_id in unique_agents:
            self.db.update_agent_stats(agent_id)
        
        print(f"\nMigration complete!")
        print(f"Total files processed: {len(json_files)}")
        print(f"Total records migrated: {total_migrated}")
        print(f"Unique agents: {len(unique_agents)}")
        
        return {
            'files': len(json_files),
            'records': total_migrated,
            'agents': len(unique_agents)
        }
    
    def generate_sample_data(self, num_agents: int = 3, urls_per_agent: int = 5):
        """Generate sample data for testing if no real data exists."""
        print(f"Generating sample data for {num_agents} agents...")
        
        sample_urls = [
            "https://example.com",
            "https://test.com",
            "https://demo.com",
            "https://sample.org",
            "https://placeholder.com",
            "https://mocksite.net",
            "https://testpage.io",
            "https://demosite.org"
        ]
        
        for agent_id in range(1, num_agents + 1):
            agent_dir = f"results/agent_{agent_id}"
            os.makedirs(agent_dir, exist_ok=True)
            
            results = []
            for i in range(urls_per_agent):
                url = sample_urls[i % len(sample_urls)]
                
                # Simulate some successful and some failed scrapes
                if i % 4 == 0:  # 25% failure rate
                    result = {
                        'url': url,
                        'error': 'Connection timeout',
                        'timestamp': datetime.utcnow().isoformat(),
                        'agent_id': agent_id
                    }
                else:
                    result = {
                        'url': url,
                        'data': {
                            'title': f'Sample Page {i + 1}',
                            'text_length': 1000 + i * 100,
                            'num_links': 10 + i * 2,
                            'num_images': 5 + i,
                            'headers': [f'Header {j}' for j in range(3)]
                        },
                        'analysis': {
                            'content_density': 100.0 + i * 10,
                            'media_ratio': 0.3 + i * 0.05,
                            'header_count': 3,
                            'avg_header_length': 8.5
                        },
                        'timestamp': datetime.utcnow().isoformat(),
                        'agent_id': agent_id
                    }
                results.append(result)
            
            # Save to JSON file
            output_file = f"{agent_dir}/sample_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Generated sample data for agent {agent_id}: {output_file}")


def main():
    """Main function to run the migration."""
    parser = argparse.ArgumentParser(description='Migrate JSON results to SQLite database')
    parser.add_argument('--db', default='dashboard.db', help='Database file path')
    parser.add_argument('--results-dir', default='results', help='Results directory path')
    parser.add_argument('--no-skip-duplicates', action='store_true', 
                        help='Do not skip duplicate entries')
    parser.add_argument('--generate-sample', action='store_true',
                        help='Generate sample data if no results exist')
    parser.add_argument('--reset-db', action='store_true',
                        help='Drop all tables and recreate (WARNING: deletes all data)')
    
    args = parser.parse_args()
    
    # Create migrator instance
    migrator = DataMigrator(args.db)
    
    # Reset database if requested
    if args.reset_db:
        response = input("WARNING: This will delete all existing data. Continue? (y/N): ")
        if response.lower() == 'y':
            migrator.db.drop_all_tables()
            print("Database reset complete.")
        else:
            print("Database reset cancelled.")
            return
    
    # Generate sample data if requested
    if args.generate_sample:
        migrator.generate_sample_data()
    
    # Run migration
    skip_duplicates = not args.no_skip_duplicates
    stats = migrator.migrate_all(args.results_dir, skip_duplicates)
    
    # Print final statistics
    if stats['records'] > 0:
        db_stats = migrator.db.get_stats()
        print("\nDatabase Statistics:")
        print(f"  Total results: {db_stats['total_results']}")
        print(f"  Successful scrapes: {db_stats['successful_results']}")
        print(f"  Failed scrapes: {db_stats['failed_results']}")
        print(f"  Unique URLs: {db_stats['unique_urls']}")
        print(f"  Average text length: {db_stats['avg_text_length']:.1f}")
        print(f"  Average links per page: {db_stats['avg_links_per_page']:.1f}")
        print(f"  Average images per page: {db_stats['avg_images_per_page']:.1f}")


if __name__ == "__main__":
    main()
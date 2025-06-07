"""
Database initialization and helper functions for the Flask dashboard project.
"""
import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from models import Base, ScrapingResult, AgentStats


class Database:
    """Database connection and operation manager."""
    
    def __init__(self, db_path: str = "dashboard.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def init_db(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        print(f"Database initialized at {self.db_path}")
        
    def drop_all_tables(self):
        """Drop all tables (use with caution)."""
        Base.metadata.drop_all(bind=self.engine)
        print("All tables dropped")
        
    @contextmanager
    def get_session(self):
        """Provide a transactional scope for database operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # CRUD Operations for ScrapingResult
    
    def create_scraping_result(self, data: Dict[str, Any]) -> ScrapingResult:
        """Create a new scraping result."""
        with self.get_session() as session:
            result = ScrapingResult(**data)
            session.add(result)
            session.flush()
            session.refresh(result)
            return result
    
    def get_scraping_result(self, result_id: int) -> Optional[ScrapingResult]:
        """Get a scraping result by ID."""
        with self.get_session() as session:
            return session.query(ScrapingResult).filter(ScrapingResult.id == result_id).first()
    
    def get_all_scraping_results(self, limit: Optional[int] = None, offset: int = 0) -> List[ScrapingResult]:
        """Get all scraping results with optional pagination."""
        with self.get_session() as session:
            query = session.query(ScrapingResult).order_by(ScrapingResult.timestamp.desc())
            if limit:
                query = query.limit(limit).offset(offset)
            return query.all()
    
    def get_results_by_agent(self, agent_id: int) -> List[ScrapingResult]:
        """Get all results for a specific agent."""
        with self.get_session() as session:
            return session.query(ScrapingResult)\
                .filter(ScrapingResult.agent_id == agent_id)\
                .order_by(ScrapingResult.timestamp.desc())\
                .all()
    
    def get_results_by_url(self, url: str) -> List[ScrapingResult]:
        """Get all results for a specific URL."""
        with self.get_session() as session:
            return session.query(ScrapingResult)\
                .filter(ScrapingResult.url == url)\
                .order_by(ScrapingResult.timestamp.desc())\
                .all()
    
    def update_scraping_result(self, result_id: int, data: Dict[str, Any]) -> Optional[ScrapingResult]:
        """Update an existing scraping result."""
        with self.get_session() as session:
            result = session.query(ScrapingResult).filter(ScrapingResult.id == result_id).first()
            if result:
                for key, value in data.items():
                    if hasattr(result, key):
                        setattr(result, key, value)
                session.flush()
                session.refresh(result)
            return result
    
    def delete_scraping_result(self, result_id: int) -> bool:
        """Delete a scraping result."""
        with self.get_session() as session:
            result = session.query(ScrapingResult).filter(ScrapingResult.id == result_id).first()
            if result:
                session.delete(result)
                return True
            return False
    
    # Bulk operations
    
    def bulk_create_scraping_results(self, data_list: List[Dict[str, Any]]) -> List[ScrapingResult]:
        """Create multiple scraping results in a single transaction."""
        with self.get_session() as session:
            results = [ScrapingResult(**data) for data in data_list]
            session.bulk_save_objects(results, return_defaults=True)
            return results
    
    # Statistics and aggregation
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics from the database."""
        with self.get_session() as session:
            total_results = session.query(func.count(ScrapingResult.id)).scalar()
            successful_results = session.query(func.count(ScrapingResult.id))\
                .filter(ScrapingResult.error.is_(None)).scalar()
            failed_results = session.query(func.count(ScrapingResult.id))\
                .filter(ScrapingResult.error.isnot(None)).scalar()
            
            avg_text_length = session.query(func.avg(ScrapingResult.text_length))\
                .filter(ScrapingResult.error.is_(None)).scalar() or 0
            avg_links = session.query(func.avg(ScrapingResult.num_links))\
                .filter(ScrapingResult.error.is_(None)).scalar() or 0
            avg_images = session.query(func.avg(ScrapingResult.num_images))\
                .filter(ScrapingResult.error.is_(None)).scalar() or 0
            
            unique_urls = session.query(func.count(func.distinct(ScrapingResult.url))).scalar()
            unique_agents = session.query(func.count(func.distinct(ScrapingResult.agent_id))).scalar()
            
            return {
                'total_results': total_results,
                'successful_results': successful_results,
                'failed_results': failed_results,
                'avg_text_length': float(avg_text_length),
                'avg_links_per_page': float(avg_links),
                'avg_images_per_page': float(avg_images),
                'unique_urls': unique_urls,
                'unique_agents': unique_agents
            }
    
    def get_agent_stats(self, agent_id: int) -> Dict[str, Any]:
        """Get statistics for a specific agent."""
        with self.get_session() as session:
            results = session.query(ScrapingResult).filter(ScrapingResult.agent_id == agent_id).all()
            
            if not results:
                return {
                    'agent_id': agent_id,
                    'total_urls_processed': 0,
                    'successful_scrapes': 0,
                    'failed_scrapes': 0,
                    'avg_text_length': 0.0,
                    'avg_links_per_page': 0.0,
                    'avg_images_per_page': 0.0
                }
            
            successful = [r for r in results if r.error is None]
            
            return {
                'agent_id': agent_id,
                'total_urls_processed': len(results),
                'successful_scrapes': len(successful),
                'failed_scrapes': len(results) - len(successful),
                'avg_text_length': sum(r.text_length for r in successful) / len(successful) if successful else 0,
                'avg_links_per_page': sum(r.num_links for r in successful) / len(successful) if successful else 0,
                'avg_images_per_page': sum(r.num_images for r in successful) / len(successful) if successful else 0
            }
    
    def update_agent_stats(self, agent_id: int):
        """Update or create agent statistics."""
        stats = self.get_agent_stats(agent_id)
        
        with self.get_session() as session:
            agent_stat = session.query(AgentStats).filter(AgentStats.agent_id == agent_id).first()
            
            if agent_stat:
                # Update existing
                agent_stat.total_urls_processed = stats['total_urls_processed']
                agent_stat.successful_scrapes = stats['successful_scrapes']
                agent_stat.failed_scrapes = stats['failed_scrapes']
                agent_stat.avg_text_length = stats['avg_text_length']
                agent_stat.avg_links_per_page = stats['avg_links_per_page']
                agent_stat.avg_images_per_page = stats['avg_images_per_page']
            else:
                # Create new
                agent_stat = AgentStats(**stats)
                session.add(agent_stat)
    
    def get_recent_results(self, limit: int = 10) -> List[ScrapingResult]:
        """Get the most recent scraping results."""
        with self.get_session() as session:
            return session.query(ScrapingResult)\
                .order_by(ScrapingResult.timestamp.desc())\
                .limit(limit)\
                .all()
    
    def search_results(self, search_term: str) -> List[ScrapingResult]:
        """Search results by URL or title."""
        with self.get_session() as session:
            return session.query(ScrapingResult)\
                .filter(
                    (ScrapingResult.url.contains(search_term)) |
                    (ScrapingResult.title.contains(search_term))
                )\
                .order_by(ScrapingResult.timestamp.desc())\
                .all()


# Convenience functions for direct use

def init_database(db_path: str = "dashboard.db"):
    """Initialize the database with all tables."""
    db = Database(db_path)
    db.init_db()
    return db


def get_db_instance(db_path: str = "dashboard.db") -> Database:
    """Get a database instance."""
    return Database(db_path)
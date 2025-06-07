"""
SQLAlchemy models for the Flask dashboard project.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ScrapingResult(Base):
    """Model for storing web scraping results."""
    __tablename__ = 'scraping_results'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # URL and basic info
    url = Column(String(500), nullable=False)
    title = Column(String(500))
    
    # Scraped data metrics
    text_length = Column(Integer, default=0)
    num_links = Column(Integer, default=0)
    num_images = Column(Integer, default=0)
    
    # Analysis results
    content_density = Column(Float, default=0.0)
    media_ratio = Column(Float, default=0.0)
    header_count = Column(Integer, default=0)
    avg_header_length = Column(Float, default=0.0)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    agent_id = Column(Integer, nullable=False)
    
    # Store headers as JSON array
    headers = Column(JSON)
    
    # Error tracking
    error = Column(Text)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_agent_timestamp', 'agent_id', 'timestamp'),
        Index('idx_url', 'url'),
        Index('idx_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<ScrapingResult(id={self.id}, url='{self.url}', agent_id={self.agent_id})>"
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'text_length': self.text_length,
            'num_links': self.num_links,
            'num_images': self.num_images,
            'content_density': self.content_density,
            'media_ratio': self.media_ratio,
            'header_count': self.header_count,
            'avg_header_length': self.avg_header_length,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'agent_id': self.agent_id,
            'headers': self.headers,
            'error': self.error
        }


class AgentStats(Base):
    """Model for storing aggregated statistics per agent."""
    __tablename__ = 'agent_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, unique=True, nullable=False)
    total_urls_processed = Column(Integer, default=0)
    successful_scrapes = Column(Integer, default=0)
    failed_scrapes = Column(Integer, default=0)
    avg_text_length = Column(Float, default=0.0)
    avg_links_per_page = Column(Float, default=0.0)
    avg_images_per_page = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AgentStats(agent_id={self.agent_id}, total_urls={self.total_urls_processed})>"
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'total_urls_processed': self.total_urls_processed,
            'successful_scrapes': self.successful_scrapes,
            'failed_scrapes': self.failed_scrapes,
            'avg_text_length': self.avg_text_length,
            'avg_links_per_page': self.avg_links_per_page,
            'avg_images_per_page': self.avg_images_per_page,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
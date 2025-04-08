import os
import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy without arguments - will be initialized with app later
db = SQLAlchemy()

class ProcessedFile(db.Model):
    __tablename__ = 'processed_files'
    
    id = db.Column(db.Integer, primary_key=True)
    original_path = db.Column(db.String(255), nullable=False)
    new_path = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False)  # success, error, skipped
    author = db.Column(db.String(100))
    journal = db.Column(db.String(100))
    year = db.Column(db.String(10))
    title = db.Column(db.Text)
    error_message = db.Column(db.Text)
    processing_time = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def from_log_entry(cls, log_entry):
        """Create a ProcessedFile object from a log entry dictionary"""
        processed_file = cls()
        processed_file.original_path = log_entry.get('original_path', '')
        processed_file.new_path = log_entry.get('new_path', '')
        processed_file.status = log_entry.get('status', 'unknown')
        processed_file.processing_time = log_entry.get('processing_time', 0.0)
        processed_file.error_message = log_entry.get('error', '')
        
        # Extract metadata if available
        metadata = log_entry.get('metadata', {})
        if metadata:
            processed_file.author = metadata.get('author', '')
            processed_file.journal = metadata.get('journal', '')
            processed_file.year = metadata.get('year', '')
            processed_file.title = metadata.get('title', '')
        
        # Parse timestamp if available
        timestamp_str = log_entry.get('timestamp', '')
        if timestamp_str:
            try:
                processed_file.timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                processed_file.timestamp = datetime.utcnow()
        
        return processed_file
    
    def to_dict(self):
        """Convert the model to a dictionary for JSON serialization"""
        return {
            'id': self.id,
            'original_path': self.original_path,
            'new_path': self.new_path,
            'status': self.status,
            'metadata': {
                'author': self.author,
                'journal': self.journal,
                'year': self.year,
                'title': self.title
            },
            'error': self.error_message,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else ""
        }
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pdf_processor import process_pdf_file

class PDFHandler(FileSystemEventHandler):
    """Handler for PDF file events"""
    
    def __init__(self, callback):
        """Initialize with a callback function"""
        self.callback = callback
        self.logger = logging.getLogger(__name__)
    
    def on_created(self, event):
        """Called when a file is created"""
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            self.logger.info(f"New PDF detected: {event.src_path}")
            self._process_pdf(event.src_path)
    
    def on_modified(self, event):
        """Called when a file is modified"""
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            self.logger.info(f"Modified PDF detected: {event.src_path}")
            self._process_pdf(event.src_path)
    
    def _process_pdf(self, pdf_path):
        """Process the PDF file and invoke callback"""
        try:
            result = process_pdf_file(pdf_path)
            self.callback(result)
        except Exception as e:
            error_message = f"Error processing {pdf_path}: {str(e)}"
            self.logger.error(error_message)
            self.callback({
                "status": "error",
                "original_path": pdf_path,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

class FolderMonitor:
    """Monitors a folder for PDF files"""
    
    def __init__(self, directory, callback):
        """
        Initialize the monitor
        
        Args:
            directory (str): Directory to monitor
            callback (function): Function to call when a file is processed
        """
        self.directory = directory
        self.callback = callback
        self.observer = None
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Start monitoring the directory"""
        self.logger.info(f"Starting to monitor directory: {self.directory}")
        
        # Process existing PDF files
        self._process_existing_files()
        
        # Set up watchdog observer
        event_handler = PDFHandler(self.callback)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.directory, recursive=False)
        self.observer.start()
        
        try:
            # Keep the thread alive
            while self.observer.is_alive():
                self.observer.join(1)
        except Exception as e:
            self.logger.error(f"Error in monitor: {str(e)}")
            self.stop()
    
    def stop(self):
        """Stop monitoring the directory"""
        if self.observer:
            self.logger.info("Stopping directory monitor")
            self.observer.stop()
            self.observer.join()
            self.observer = None
    
    def _process_existing_files(self):
        """Process PDF files that already exist in the directory"""
        self.logger.info(f"Checking for existing PDF files in {self.directory}")
        try:
            files = [f for f in os.listdir(self.directory) 
                    if os.path.isfile(os.path.join(self.directory, f)) 
                    and f.lower().endswith('.pdf')]
            
            self.logger.info(f"Found {len(files)} existing PDF files")
            
            for filename in files:
                filepath = os.path.join(self.directory, filename)
                self.logger.info(f"Processing existing file: {filepath}")
                try:
                    result = process_pdf_file(filepath)
                    self.callback(result)
                except Exception as e:
                    error_message = f"Error processing existing file {filepath}: {str(e)}"
                    self.logger.error(error_message)
                    self.callback({
                        "status": "error",
                        "original_path": filepath,
                        "error": str(e),
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
        except Exception as e:
            self.logger.error(f"Error listing directory contents: {str(e)}")

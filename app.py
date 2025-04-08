import os
import logging
from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from folder_monitor import FolderMonitor
import threading
from models import db, ProcessedFile

# 設置日誌
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 檢查是否有.env文件，自動加載環境變量
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("已從.env文件加載環境變量")
except ImportError:
    logger.warning("python-dotenv未安裝，無法從.env文件加載環境變量")
except Exception as e:
    logger.warning(f"加載.env文件時出錯: {str(e)}")

# 檢查SiliconFlow API密鑰
if not os.environ.get("SILICONFLOW_API_KEY"):
    logger.warning(
        "未設置SILICONFLOW_API_KEY環境變量，AI功能將無法使用。"
        "請複製.env.example為.env並設置您的API密鑰。"
    )

# 創建Flask應用
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# 設置端口（本地運行時使用自定義端口）
port = int(os.environ.get("PORT", 5100))

# 配置數據庫
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///pdf_processor.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 輸出數據庫配置用於調試
logger.debug(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

# 初始化數據庫
db.init_app(app)

# 創建數據表
with app.app_context():
    db.create_all()

# Global variables to store state
monitor_thread = None
folder_monitor = None
is_monitoring = False
processed_files = []
monitor_dir = ""

@app.route('/')
def index():
    """Render the main page"""
    global is_monitoring, monitor_dir, processed_files
    
    # Load processed files from database if the in-memory list is empty
    if not processed_files:
        try:
            db_files = ProcessedFile.query.order_by(ProcessedFile.timestamp.desc()).all()
            processed_files = [file.to_dict() for file in db_files]
            logger.debug(f"Loaded {len(processed_files)} files from database")
        except Exception as e:
            logger.error(f"Error loading files from database: {str(e)}")
    
    return render_template('index.html', 
                          is_monitoring=is_monitoring,
                          monitor_dir=monitor_dir,
                          processed_files=processed_files)

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    """處理指定目錄中的所有PDF文件（批處理模式）"""
    global monitor_thread, folder_monitor, is_monitoring, monitor_dir, processed_files
    
    # 獲取表單中的目錄
    directory = request.form.get('directory', '')
    
    if not directory:
        flash("請提供要處理的目錄", "danger")
        return redirect(url_for('index'))
    
    # 驗證目錄是否存在
    if not os.path.isdir(directory):
        flash(f"目錄 '{directory}' 不存在", "danger")
        return redirect(url_for('index'))
    
    # 如果有正在運行的監控，停止它
    if is_monitoring and folder_monitor:
        folder_monitor.stop()
        if monitor_thread:
            monitor_thread.join(timeout=5)
    
    # 清空處理文件列表
    processed_files.clear()
    
    # 設置當前處理的目錄
    monitor_dir = directory
    
    # 創建新的文件夾處理器，但僅處理現有文件，不監控變更
    folder_monitor = FolderMonitor(directory, on_file_processed)
    
    # 在單獨的線程中處理所有現有PDF文件
    def process_existing_files_only():
        folder_monitor._process_existing_files()
        global is_monitoring
        is_monitoring = False  # 處理完成後自動停止
    
    monitor_thread = threading.Thread(target=process_existing_files_only)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    is_monitoring = True
    flash(f"正在處理目錄中的所有PDF文件: {directory}", "success")
    return redirect(url_for('index'))

@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """停止處理文件"""
    global is_monitoring, folder_monitor, monitor_thread
    
    if folder_monitor:
        folder_monitor.stop()
        is_monitoring = False
        flash("已停止處理文件", "info")
    
    return redirect(url_for('index'))

@app.route('/get_logs', methods=['GET'])
def get_logs():
    """Return the logs as JSON"""
    global processed_files
    
    # If in-memory list is empty, load from database
    if not processed_files:
        with app.app_context():
            db_files = ProcessedFile.query.order_by(ProcessedFile.timestamp.desc()).all()
            processed_files = [file.to_dict() for file in db_files]
    
    return jsonify(processed_files)

def on_file_processed(log_entry):
    """Callback function when a file is processed"""
    global processed_files
    
    # Add to in-memory list
    processed_files.append(log_entry)
    logger.info(f"File processed: {log_entry}")
    
    # Save to database
    with app.app_context():
        db_file = ProcessedFile.from_log_entry(log_entry)
        db.session.add(db_file)
        db.session.commit()
        logger.debug(f"Saved to database: {db_file.id}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)

import os
import re
import time
import logging
from metadata_extractor import extract_metadata_from_pdf

# Configure logging
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """
    移除或替換文件名中不允許的字符
    
    Args:
        filename (str): 原始文件名
        
    Returns:
        str: 處理後的文件名
    """
    # 替換不允許的字符
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 將多個空格和下劃線替換為單個下劃線
    filename = re.sub(r'[\s_]+', '_', filename)
    
    # 截斷過長的文件名（最大255個字符）
    if len(filename) > 255:
        # 保留文件擴展名
        name, ext = os.path.splitext(filename)
        max_name_length = 255 - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename

def process_pdf_file(pdf_path):
    """
    處理PDF文件：提取元數據並根據命名規則進行重命名
    
    Args:
        pdf_path (str): PDF文件路徑
        
    Returns:
        dict: 處理結果信息
    """
    start_time = time.time()
    logger.info(f"處理PDF文件: {pdf_path}")
    
    try:
        # 直接使用語言模型提取元數據
        metadata = extract_metadata_from_pdf(pdf_path)
        
        # 檢查是否有缺失的必要字段
        required_fields = ['author_lastname', 'journal', 'journal_abbr', 'year', 'title', 'doc_type']
        missing_fields = [field for field in required_fields if not metadata.get(field)]
        
        if missing_fields:
            logger.warning(f"缺失元數據字段: {', '.join(missing_fields)}")
            
            # 為缺失字段填充默認值
            for field in missing_fields:
                if field == 'doc_type':
                    metadata[field] = 'paper'  # 默認為論文
                else:
                    metadata[field] = 'Unknown'
        
        # 獲取元數據
        author_lastname = metadata['author_lastname'] if metadata['author_lastname'] else 'Unknown'
        year = metadata['year'] if metadata['year'] else 'Unknown'
        title = metadata['title'] if metadata['title'] else 'Unknown'
        doc_type = metadata.get('doc_type', 'paper').lower()
        
        # 檢查是否為書籍
        is_book = doc_type == 'book'
        
        # 截斷標題（如果太長）
        max_title_length = 100
        if len(title) > max_title_length:
            title = title[:max_title_length-3] + "..."
        
        # 根據文檔類型創建新文件名
        if is_book:
            # 書籍格式: FirstAuthorLastname_年份_書名.pdf
            new_filename = f"{author_lastname}_{year}_{title}.pdf"
        else:
            # 論文格式: FirstAuthorLastname_年份_期刊或會議縮寫_論文標題.pdf
            # 優先使用語言模型提供的縮寫
            journal_abbr = metadata['journal_abbr'] if metadata['journal_abbr'] else 'Unknown'
            new_filename = f"{author_lastname}_{year}_{journal_abbr}_{title}.pdf"
        
        # 處理文件名中的非法字符
        new_filename = sanitize_filename(new_filename)
        
        # 獲取原始文件所在的目錄
        directory = os.path.dirname(pdf_path)
        
        # 創建新的文件路徑
        new_path = os.path.join(directory, new_filename)
        
        # 如果文件已存在，不要覆蓋它
        original_new_path = new_path
        counter = 1
        while os.path.exists(new_path) and os.path.abspath(pdf_path) != os.path.abspath(new_path):
            name, ext = os.path.splitext(original_new_path)
            new_path = f"{name}_{counter}{ext}"
            counter += 1
        
        # 如果文件已經有正確的名稱，跳過重命名
        if os.path.abspath(pdf_path) == os.path.abspath(new_path):
            logger.info(f"文件已經有正確的名稱: {pdf_path}")
            return {
                "status": "skipped",
                "original_path": pdf_path,
                "reason": "文件已經有正確的名稱",
                "metadata": metadata,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "processing_time": round(time.time() - start_time, 2)
            }
        
        # 重命名文件
        os.rename(pdf_path, new_path)
        logger.info(f"重命名完成: {pdf_path} -> {new_path}")
        
        return {
            "status": "success",
            "original_path": pdf_path,
            "new_path": new_path,
            "metadata": metadata,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": round(time.time() - start_time, 2)
        }
    
    except Exception as e:
        logger.error(f"處理PDF文件時發生錯誤: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "original_path": pdf_path,
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": round(time.time() - start_time, 2)
        }
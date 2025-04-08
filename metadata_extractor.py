import logging
import PyPDF2
from ai_metadata_extractor import SiliconFlowQwenExtractor

# 設置日誌
logger = logging.getLogger(__name__)

# 初始化AI提取器
ai_extractor = SiliconFlowQwenExtractor()
USE_AI_EXTRACTION = ai_extractor.is_available()

def extract_metadata_from_pdf(pdf_path):
    """
    直接從PDF文件提取文本並使用語言模型提取元數據
    
    Args:
        pdf_path (str): PDF文件路徑
        
    Returns:
        dict: 包含提取的元數據的字典
    """
    # 默認元數據
    metadata = {
        'author_lastname': '',
        'journal': '',
        'journal_abbr': '',
        'year': '',
        'title': '',
        'doc_type': 'paper'
    }
    
    logger.info(f"從PDF提取文本並使用AI提取元數據: {pdf_path}")
    
    try:
        # 從PDF提取文本
        text = extract_text_from_pdf(pdf_path)
        
        # 如果無法提取文本，返回空元數據
        if not text:
            logger.warning(f"無法從PDF提取文本: {pdf_path}")
            return metadata
        
        # 使用通義千問API提取元數據
        if USE_AI_EXTRACTION:
            logger.info("使用通義千問API直接提取元數據...")
            ai_metadata = ai_extractor.extract_pdf_metadata(text)
            
            if ai_metadata:
                logger.info(f"成功提取元數據: {ai_metadata}")
                return ai_metadata
            else:
                logger.warning("AI提取元數據失敗，返回空值")
        else:
            logger.warning("未設置SiliconFlow API密鑰，無法提取元數據")
        
        return metadata
        
    except Exception as e:
        logger.error(f"提取元數據過程中發生錯誤: {str(e)}", exc_info=True)
        return metadata

def extract_text_from_pdf(pdf_path):
    """
    從PDF文件提取完整文本內容
    
    Args:
        pdf_path (str): PDF文件路徑
        
    Returns:
        str: 提取的文本內容
    """
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # 提取PDF屬性信息（通常包含標題、作者等）
            info = reader.metadata
            if info:
                # 嘗試從PDF屬性中獲取元數據
                text += f"PDF標題: {info.get('/Title', '')}\n"
                text += f"PDF作者: {info.get('/Author', '')}\n"
                text += f"PDF主題: {info.get('/Subject', '')}\n"
                text += f"PDF關鍵詞: {info.get('/Keywords', '')}\n\n"
            
            # 獲取總頁數
            page_count = len(reader.pages)
            
            # 提取前幾頁（通常包含論文的主要信息）
            max_pages = min(10, page_count)  # 最多提取前10頁
            for i in range(max_pages):
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text += f"第{i+1}頁內容:\n{page_text}\n\n"
        
        return text
    
    except Exception as e:
        logger.error(f"提取PDF文本時發生錯誤: {str(e)}", exc_info=True)
        return ""
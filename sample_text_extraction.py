"""
示範提取PDF文本並傳送到AI模型的代碼
"""
import os
import logging
from metadata_extractor import extract_text_from_pdf

# 設置日誌格式
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demonstrate_text_extraction(pdf_path):
    """
    示範從PDF中提取文本的過程
    
    Args:
        pdf_path (str): PDF文件路徑
    """
    logger.info(f"開始示範從PDF提取文本: {pdf_path}")
    
    try:
        # 檢查文件是否存在
        if not os.path.exists(pdf_path):
            logger.error(f"文件不存在: {pdf_path}")
            return
            
        # 從PDF提取文本
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # 顯示提取的文本長度和一部分內容
        if extracted_text:
            text_length = len(extracted_text)
            preview_length = min(500, text_length)  # 顯示前500個字符
            
            logger.info(f"提取成功! 文本總長度: {text_length} 字符")
            logger.info(f"文本預覽 (前{preview_length}字符):")
            logger.info("-" * 50)
            logger.info(extracted_text[:preview_length] + "..." if text_length > preview_length else extracted_text)
            logger.info("-" * 50)
            
            # 如果要提取元數據，這裡會將文本發送給AI模型
            logger.info("文本提取完成後，會將其發送給通義千問AI模型，由AI直接提取元數據:")
            logger.info("1. 第一作者姓氏 (author_lastname)")
            logger.info("2. 期刊/會議完整名稱 (journal)")
            logger.info("3. 期刊/會議縮寫 (journal_abbr)")
            logger.info("4. 出版年份 (year)")
            logger.info("5. 論文標題 (title)")
            logger.info("6. 文檔類型 (doc_type: 'paper'或'book')")
            
            return True
        else:
            logger.warning("未能從PDF提取到文本")
            return False
    
    except Exception as e:
        logger.error(f"示範過程中發生錯誤: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # 使用示例
    sample_pdf = "path/to/your/sample.pdf"  # 替換為實際PDF路徑
    
    logger.info("這是一個示範如何從PDF提取文本並發送給AI的腳本")
    logger.info("該過程不使用元數據或正則表達式匹配，而是直接讓AI從文本提取所有需要的信息")
    
    if os.path.exists(sample_pdf):
        demonstrate_text_extraction(sample_pdf)
    else:
        logger.info(f"請將代碼中的sample_pdf變量替換為實際的PDF文件路徑")
        logger.info(f"當前設置的路徑不存在: {sample_pdf}")
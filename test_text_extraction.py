"""
測試從PDF提取文本的代碼
"""
import logging
import os
import sys
from metadata_extractor import extract_text_from_pdf

# 設置日誌
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    測試從PDF提取文本的功能
    用法: python test_text_extraction.py <pdf文件路徑>
    """
    # 檢查命令行參數
    if len(sys.argv) < 2:
        logger.error("請提供PDF文件路徑作為命令行參數")
        logger.info("用法: python test_text_extraction.py <pdf文件路徑>")
        return
    
    pdf_path = sys.argv[1]
    
    # 檢查文件是否存在
    if not os.path.exists(pdf_path):
        logger.error(f"文件不存在: {pdf_path}")
        return
    
    # 提取文本
    logger.info(f"從PDF提取文本: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    # 顯示結果
    if text:
        text_length = len(text)
        preview_length = min(500, text_length)
        logger.info(f"成功提取文本，總長度: {text_length} 字符")
        logger.info(f"文本預覽 (前{preview_length}字符):")
        logger.info("-" * 50)
        logger.info(text[:preview_length] + "..." if text_length > preview_length else text)
        logger.info("-" * 50)
    else:
        logger.warning("未能提取到文本")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import os
import logging
from ai_metadata_extractor import SiliconFlowQwenExtractor

# 配置日誌
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extractor():
    """測試 SiliconFlowQwen 提取器"""
    logger.info("開始測試 SiliconFlowQwen 提取器")
    
    # 創建示例文本
    sample_text = """
    Title: Enhanced Metadata Extraction from Academic Papers Using Deep Learning
    
    Author: Zhang Wei
    
    Department of Computer Science, Beijing University
    
    Journal: IEEE Transactions on Information Technology
    
    Published: 2024
    
    Abstract:
    This paper presents a novel approach to automatic metadata extraction from academic 
    papers using deep learning techniques. Traditional methods often rely on rule-based 
    systems with limited accuracy. We propose a transformer-based model that can accurately 
    identify and extract key metadata elements including author names, journal information, 
    publication year, and titles. Our system demonstrates superior performance on a diverse 
    dataset of academic papers across multiple disciplines.
    
    Keywords: metadata extraction, academic papers, deep learning, natural language processing
    """
    
    # 初始化提取器
    extractor = SiliconFlowQwenExtractor()
    
    # 檢查API密鑰是否可用
    if not extractor.is_available():
        logger.error("API密鑰不可用，無法進行測試")
        return
    
    # 提取元數據
    logger.info("正在提取元數據...")
    metadata = extractor.extract_metadata(sample_text)
    
    # 輸出結果
    logger.info("提取結果:")
    logger.info(f"作者: {metadata.get('author', '未提取')}")
    logger.info(f"期刊: {metadata.get('journal', '未提取')}")
    logger.info(f"年份: {metadata.get('year', '未提取')}")
    logger.info(f"標題: {metadata.get('title', '未提取')}")

if __name__ == "__main__":
    test_extractor()
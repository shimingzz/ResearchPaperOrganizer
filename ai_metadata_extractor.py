import os
import json
import logging
import requests
from typing import Dict, List

# 設置日誌
logger = logging.getLogger(__name__)

class SiliconFlowQwenExtractor:
    """
    使用通義千問(Qwen)模型通過SiliconFlow API從PDF文本中提取元數據
    """
    def __init__(self):
        """初始化提取器"""
        # 從環境變量獲取API密鑰
        self.api_key = os.environ.get("SILICONFLOW_API_KEY")
        if not self.api_key:
            logger.warning("未設置SILICONFLOW_API_KEY環境變量")
            
        # API配置
        self.api_base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.model = "Qwen/Qwen2.5-7B-Instruct"  # 指定使用的模型
        
        # 設定模型上下文窗口大小
        self.max_context_length = 30000  # 模型最大上下文窗口約32K，保守設置為30K
    
    def extract_pdf_metadata(self, text: str) -> Dict[str, str]:
        """
        直接從PDF文本提取元數據（作者姓氏、期刊名、期刊縮寫、年份、標題、文檔類型）
        
        Args:
            text (str): PDF文本內容
            
        Returns:
            Dict[str, str]: 包含元數據的字典
        """
        if not self.api_key:
            logger.error("未設置API密鑰，無法提取元數據")
            return {
                'author_lastname': '',
                'journal': '',
                'journal_abbr': '',
                'year': '',
                'title': '',
                'doc_type': 'paper'
            }
        
        # 裁剪文本避免超出上下文窗口
        if len(text) > self.max_context_length:
            logger.info(f"文本過長 ({len(text)} 字符)，將截取前 {self.max_context_length} 字符")
            text = text[:self.max_context_length]
        
        # 構建提示詞
        prompt = f"""分析以下PDF文本，提取以下關鍵元數據，以JSON格式返回：

1. author_lastname: 第一作者的姓氏（僅姓，不含名）
2. journal: 期刊或會議的完整名稱
3. journal_abbr: 期刊或會議的標準縮寫（若不確定，請給出最可能的縮寫）
4. year: 出版年份（4位數字）
5. title: 論文完整標題
6. doc_type: 文檔類型，僅限"paper"或"book"

僅返回JSON格式，無需其他解釋。若無法確定某字段，使用空字符串。

PDF文本內容：
{text}"""

        # 調用API提取元數據
        result = self._call_api(prompt)
        
        # 記錄結果
        if self._has_essential_fields(result):
            logger.info("成功從PDF提取出主要元數據")
        else:
            logger.warning("無法從PDF提取出完整元數據")
            
        return result
    
    def _call_api(self, prompt: str) -> Dict[str, str]:
        """
        調用通義千問API
        
        Args:
            prompt (str): 提示詞
            
        Returns:
            Dict[str, str]: 提取的元數據字典
        """
        try:
            # 準備API請求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,  # 低溫度以獲得更確定性的回答
                "max_tokens": 1000
            }
            
            # 發送API請求
            logger.info("發送請求到通義千問API...")
            response = requests.post(
                self.api_base_url,
                headers=headers,
                json=payload
            )
            
            # 解析響應
            if response.status_code == 200:
                response_data = response.json()
                logger.debug(f"API響應: {response_data}")
                
                # 提取生成的文本
                ai_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                logger.info(f"獲得API響應: {ai_response[:100]}...")
                
                # 嘗試解析JSON響應
                try:
                    # 查找文本中的JSON部分
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = ai_response[json_start:json_end]
                        metadata = json.loads(json_str)
                        
                        # 確保所有必需字段都存在
                        expected_fields = ['author_lastname', 'journal', 'journal_abbr', 'year', 'title', 'doc_type']
                        for field in expected_fields:
                            if field not in metadata or metadata[field] is None:
                                metadata[field] = ''
                        
                        # 確保文檔類型為'paper'或'book'
                        if metadata.get('doc_type', '').lower() not in ['paper', 'book']:
                            # 預設為paper
                            metadata['doc_type'] = 'paper'
                        
                        return metadata
                    else:
                        logger.warning("無法在API響應中找到JSON數據")
                except json.JSONDecodeError as e:
                    logger.error(f"解析API返回的JSON時出錯: {e}")
                    logger.debug(f"原始回應: {ai_response}")
            else:
                logger.error(f"API請求失敗，狀態碼: {response.status_code}, 回應: {response.text}")
                
        except Exception as e:
            logger.error(f"調用SiliconFlow API時出錯: {e}")
        
        # 如果提取失敗，返回空值
        return {
            'author_lastname': '',
            'journal': '',
            'journal_abbr': '',
            'year': '',
            'title': '',
            'doc_type': 'paper'
        }
    
    def _has_essential_fields(self, result: Dict[str, str]) -> bool:
        """
        檢查是否提取到了主要字段
        
        Args:
            result (Dict[str, str]): 提取的元數據
            
        Returns:
            bool: 如果主要字段存在則返回True
        """
        essential_fields = ['author_lastname', 'title', 'year']
        return all(bool(result.get(field)) for field in essential_fields)
    
    def is_available(self) -> bool:
        """
        檢查API服務是否可用
        
        Returns:
            bool: 如果API可用返回True，否則返回False
        """
        return self.api_key is not None
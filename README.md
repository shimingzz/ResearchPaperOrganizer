# 研究文獻自動命名工具

這是一個基於 AI 的 PDF 文件自動處理工具，可以提取文檔數據並按統一格式重命名文件。

## 功能特點

- 從 PDF 文件中提取文本
- 使用通義千問 AI 模型自動識別元數據
- 自動提取作者姓氏、期刊/會議名稱、期刊縮寫、年份和標題
- 根據文檔類型（論文或書籍）使用不同的命名格式
- 批量處理指定目錄中的所有 PDF 文件

## 安裝和設置

1. 克隆此倉庫
2. 安裝依賴
   ```
   pip install -r dependencies.txt
   ```
3. 設置環境變量
   - 建立文件為 `.env`
   - 在 `.env` 文件中添加您的 SiliconFlow API 密鑰
   ```
   SILICONFLOW_API_KEY=your_api_key_here
   ```

## 使用方法

1. 啟動應用
   ```
   python main.py
   ```
2. 在瀏覽器中訪問 http://localhost:5100
3. 選擇要處理的目錄並開始處理 PDF 文件

## 命名規則

- 學術論文: `FirstAuthorLastname_年份_期刊或會議縮寫_論文標題.pdf`
- 書籍: `FirstAuthorLastname_年份_書名.pdf`

## 測試文本提取功能

您可以使用以下命令測試從 PDF 提取文本的功能：
```
python test_text_extraction.py path/to/your.pdf
```

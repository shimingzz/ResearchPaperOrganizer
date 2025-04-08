from dotenv import load_dotenv
import os

load_dotenv()  # 會讀取 .env 檔案並載入環境變數

from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)

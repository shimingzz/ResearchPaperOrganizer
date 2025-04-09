#!/usr/bin/env python3
"""
本地環境設置腳本
幫助用戶設置API密鑰和安裝必要的依賴
"""
import os
import subprocess
import sys
import platform
from pathlib import Path

# 顏色代碼
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_color(text, color):
    """打印帶顏色的文本"""
    print(f"{color}{text}{Colors.END}")

def check_python_version():
    """檢查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_color("錯誤: 需要Python 3.8或更高版本", Colors.RED)
        print_color(f"當前版本: Python {version.major}.{version.minor}.{version.micro}", Colors.RED)
        return False
    return True

def create_env_file():
    """創建.env文件"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    # 檢查.env文件是否已存在
    if env_file.exists():
        print_color(".env文件已存在", Colors.YELLOW)
        update = input("是否要更新API密鑰? (y/n): ").lower()
        if update != 'y':
            return
    
    # 檢查.env.example是否存在
    if not env_example.exists():
        print_color(".env.example文件不存在，創建默認配置", Colors.YELLOW)
        with open(env_example, 'w') as f:
            f.write("# API密鑰設置\n")
            f.write("SILICONFLOW_API_KEY=your_api_key_here\n\n")
            f.write("# 數據庫設置\n")
            f.write("DATABASE_URL=sqlite:///pdf_processor.db\n")
    
    # 從用戶獲取API密鑰
    print_color("\n請提供您的通義千問API密鑰:", Colors.BLUE)
    print("訪問 https://siliconflow.cn 獲取密鑰")
    api_key = input("SiliconFlow API密鑰: ").strip()
    
    # 讀取.env.example文件
    with open(env_example, 'r') as f:
        env_content = f.read()
    
    # 替換API密鑰
    env_content = env_content.replace("your_api_key_here", api_key)
    
    # 寫入.env文件
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print_color("成功創建.env文件！", Colors.GREEN)

def install_dependencies():
    """安裝依賴項"""
    print_color("\n正在安裝依賴項...", Colors.BLUE)
    
    dependencies_file = Path("dependencies.txt")
    if not dependencies_file.exists():
        print_color("找不到dependencies.txt文件", Colors.RED)
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "dependencies.txt"], check=True)
        print_color("依賴項安裝成功！", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_color(f"安裝依賴項時發生錯誤: {e}", Colors.RED)
        return False

def main():
    """主函數"""
    print_color("=" * 60, Colors.BOLD)
    print_color("PDF文件自動組織工具 - 本地環境設置", Colors.BOLD)
    print_color("=" * 60, Colors.BOLD)
    
    # 檢查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 創建.env文件
    create_env_file()
    
    # 安裝依賴項
    if install_dependencies():
        print_color("\n環境設置完成！", Colors.GREEN)
        print_color("\n您可以通過以下方式啟動應用:", Colors.BLUE)
        print_color("python main.py", Colors.BOLD)
        print_color("\n默認情況下，應用將在 http://localhost:5100 運行", Colors.BLUE)
    else:
        print_color("\n環境設置失敗", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
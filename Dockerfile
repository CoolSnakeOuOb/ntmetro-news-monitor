# 使用官方 Python 簡化版作為 base image
FROM python:3.9-slim

# 安裝 Playwright 與 Chromium 需要的系統相依套件
RUN apt-get update && apt-get install -y \
    wget curl unzip fonts-liberation libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libgbm-dev libxshmfence-dev \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製需求檔案
COPY requirements.txt ./

# 安裝 Python 依賴套件
RUN pip install --no-cache-dir -r requirements.txt

# 關鍵！安裝 Playwright 及其完整系統相依 (雲端部署穩定關鍵)
RUN playwright install --with-deps chromium

# 複製你的程式碼進入容器
COPY . .

# 執行指令，啟動 Streamlit，監聽 0.0.0.0 讓雲端外部可存取
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

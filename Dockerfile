# 使用輕量級官方 Python 映像
FROM python:3.9-slim

# 安裝系統必要套件 (讓 Playwright 及 Chromium 能夠正常運作)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libgbm-dev \
    libxshmfence-dev \
    && rm -rf /var/lib/apt/lists/*

# 建立工作目錄
WORKDIR /app

# 複製專案檔案進入容器
COPY requirements.txt ./
COPY app.py ./

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 Playwright 及 Chromium browser
RUN playwright install chromium

# 預設 Streamlit 監聽所有介面，供內網瀏覽器連入
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]


# 📰 ntmetro-news-monitor

新北捷運輿情監控系統  
使用 Streamlit + Playwright + Docker 技術，提供每日輿情快速整理工具，產出可直接複製貼上至 LINE 群組的新聞彙整內容。

---

## 🔧 功能說明

- 🔎 支援多組自訂新聞關鍵字
- 📰 取得 Google News RSS 24 小時內最新新聞
- 🌐 自動解析 Google News 中轉跳轉網址，取回真實新聞連結
- 📝 產生 LINE 群組格式，可快速貼上回報
- 📦 全程封裝於 Docker 容器，部署簡單穩定
- ☁️ 完整支援 Render.com 雲端自動部署

---

## 📂 專案架構

```bash
ntmetro-news-monitor/
├── app.py              # 主程式 (Streamlit + Playwright邏輯)
├── requirements.txt     # Python 套件需求清單
├── Dockerfile           # Docker 部署腳本
├── .gitignore           # Git 版本控管忽略規則
└── README.md            # 專案說明文件 (本文件)
```

---

## ⚠ 核心技術重點

### 使用架構
- 前端框架：Streamlit
- 爬蟲來源：Google News RSS Feed
- 網址跳轉解析：Playwright (Chromium headless)
- 文字擷取格式：自動產出 LINE 可複製格式
- 容器化部署：Docker + Render

### Playwright 相關
- 需完整安裝瀏覽器
- 使用 `playwright install --with-deps chromium` 自動拉取依賴套件

---

## 🚀 本地端開發執行

### 環境準備

- Python 3.9
- pip

### 安裝依賴

```bash
pip install -r requirements.txt
playwright install chromium
```

### 啟動

```bash
streamlit run app.py
```

---

## 🐳 雲端部署完整流程（Render.com）

### 1️⃣ 建立 Render 帳號
- https://render.com/

### 2️⃣ 建立 Web Service
- 環境類型：**Docker**
- 連結 GitHub Repository
- Region 選擇：**Singapore (Asia)**

### 3️⃣ 完整自動部署
- Render 會依照 `Dockerfile` 自動進行：
  - Build
  - Deploy
  - Routing 設定
- 不需任何本地端 `docker build` 動作

---

## 🔨 Dockerfile 核心說明

```dockerfile
FROM python:3.9-slim

# 安裝 Playwright 依賴套件
RUN apt-get update && apt-get install -y \
    wget curl unzip fonts-liberation libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libgbm-dev libxshmfence-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 需搭配 --with-deps 確保瀏覽器依賴完整
RUN playwright install --with-deps chromium

COPY . .

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

---

## 🎯 內部操作流程 (使用者)

1️⃣ 輸入關鍵字（預設提供可編輯欄位）  
2️⃣ 點選「📥 抓取新聞」取得最新 Google News 資料  
3️⃣ 勾選新聞條目  
4️⃣ 點選「📤 產生 LINE 訊息」  
5️⃣ 按下「📋 複製到剪貼簿」 → 貼上 LINE 群組使用

---

## 🔧 進階規劃 (未來擴充)

- ⏰ 自動排程每日產出
- 📈 紀錄輿情每日變化趨勢
- 📬 自動寄信回報機制
- 🔐 內部帳號權限管理
- 🐳 Docker Build cache 最佳化
- ⚙ CI/CD 自動化部署流程

---


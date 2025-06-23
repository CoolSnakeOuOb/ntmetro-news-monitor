import streamlit as st
import feedparser
from datetime import datetime, timedelta
import time
from urllib.parse import quote_plus, urlparse
import asyncio
import platform
import multiprocessing
import streamlit.components.v1 as components

# For Windows, set event loop policy for Playwright
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

CUTOFF_HOURS = 24

def is_within_24_hours(pub_time_str):
    try:
        pub_time = datetime.strptime(pub_time_str, "%a, %d %b %Y %H:%M:%S %Z")
        return datetime.utcnow() - pub_time <= timedelta(hours=CUTOFF_HOURS)
    except ValueError:
        try:
            pub_time = datetime.strptime(pub_time_str, "%a, %d %b %Y %H:%M:%S %z")
            return datetime.utcnow().replace(tzinfo=None) - pub_time.replace(tzinfo=None) <= timedelta(hours=CUTOFF_HOURS)
        except:
            return False
    except:
        return False

# Playwright 解析邏輯
def playwright_worker(url: str, return_dict):
    from playwright.sync_api import sync_playwright
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    browser = None
    final_url = url
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            final_url = page.url
    except:
        final_url = url
    finally:
        return_dict['final_url'] = final_url
        if browser:
            try: browser.close()
            except: pass

# RSS 抓取
def fetch_news_for_query(query):
    encoded_query = quote_plus(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    feed = feedparser.parse(rss_url)
    results = []
    for entry in feed.entries:
        if hasattr(entry, 'published') and is_within_24_hours(entry.published):
            entry_url = entry.links[0]["href"] if entry.links else entry.link
            results.append({
                "label": query,
                "title": entry.title,
                "url": entry_url,
                "published": entry.published
            })
    return results

# 分群
def group_by_label(news_items):
    grouped = {}
    for item in news_items:
        grouped.setdefault(item["label"], []).append(item)
    return grouped

# --- Streamlit UI ---
st.set_page_config(page_title="捷運輿情工具 v4.1", page_icon="🚇", layout="wide")
st.title("📰 新北捷運輿情工具")

#使用說明
with st.expander("📖 使用說明"):
    st.markdown("""
    1. **輸入關鍵字**
    2. 點擊 **📥 抓取新聞** 取得 24 小時內新聞
    3. 在新聞列表中**勾選欲匯出之新聞**
    4. 按下 **📤 產生 LINE 訊息**
    5. 點擊 **📋 複製到剪貼簿**，將內容貼到 LINE 群組
    """)

# 初始化 session_state
if 'news_results' not in st.session_state:
    st.session_state.news_results = []
if 'resolved_url_cache' not in st.session_state:
    st.session_state.resolved_url_cache = {}
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

default_keywords = "捷運, 輕軌, 環狀線, 新北, 軌道, 鐵路"
keywords_input = st.text_input("🔍 請輸入關鍵字（以逗號分隔）", default_keywords)
keyword_list = [k.strip() for k in keywords_input.split(",") if k.strip()]

# 抓取新聞
if st.button("📥 抓取新聞"):
    with st.spinner("🔄 正在抓取新聞..."):
        all_news = []
        for keyword in keyword_list:
            all_news.extend(fetch_news_for_query(keyword))
        st.session_state.news_results = all_news
        st.session_state.form_submitted = False  # 每次抓取重置表單狀態
    st.success("✅ 抓取成功！")

# 勾選表單
if st.session_state.news_results:
    grouped = group_by_label(st.session_state.news_results)

    with st.form("news_selection"):
        for keyword in keyword_list:
            items = grouped.get(keyword, [])
            st.subheader(f"🔸 {keyword}")
            if not items:
                st.markdown("🔍 無相關新聞")
            for idx, item in enumerate(items):
                key = f"checkbox_{item['label']}_{item['title']}_{idx}"
                label_with_link = f"[{item['title']}]({item['url']})"
                st.checkbox(label_with_link, key=key)

        submitted = st.form_submit_button("📤 產生 LINE 訊息")
        if submitted:
            st.session_state.form_submitted = True

# 產生 LINE 訊息
if st.session_state.get('form_submitted', False):

    def get_current_checked_news():
        current_selected_news = []
        for keyword in keyword_list:
            items = grouped.get(keyword, [])
            for idx, item in enumerate(items):
                key = f"checkbox_{item['label']}_{item['title']}_{idx}"
                if st.session_state.get(key, False):
                    current_selected_news.append(item)
        return current_selected_news

    selected_news = get_current_checked_news()

    if not selected_news:
        st.warning("⚠️ 請至少勾選一則新聞")
    else:
        from collections import defaultdict
        label_group = defaultdict(list)
        for item in selected_news:
            label_group[item['label']].append(item)

        line_msg = "各位長官、同仁早安，\n今日新聞輿情連結如下：\n\n"
        for label, items in label_group.items():
            line_msg += f"【{label}】\n"
            for item in items:
                url = item['url']

                if url in st.session_state.resolved_url_cache:
                    resolved_url = st.session_state.resolved_url_cache[url]
                else:
                    parsed_url = urlparse(url)
                    if "news.google.com" in parsed_url.netloc:
                        manager = multiprocessing.Manager()
                        return_dict = manager.dict()
                        p = multiprocessing.Process(target=playwright_worker, args=(url, return_dict))
                        p.start()
                        p.join(timeout=30)
                        if p.is_alive():
                            p.terminate()
                            p.join()
                            resolved_url = url
                        else:
                            resolved_url = return_dict.get('final_url', url)
                    else:
                        resolved_url = url

                    st.session_state.resolved_url_cache[url] = resolved_url

                line_msg += f"{item['title']}\n{resolved_url}\n"
            line_msg += "\n"

        st.success("✅ 解析完成，已產生 LINE 訊息")
        st.text_area("📋 LINE 訊息內容 (可複製)", line_msg.strip(), height=400, key="line_output")

        js_safe_msg = line_msg.strip().replace('`','\\`').replace('\\','\\\\')
        components.html(f"""
            <button onclick="copyText()" style="font-size:16px;padding:8px 16px;margin-top:10px;">📋 複製到剪貼簿</button>
            <script>
            function copyText() {{
                const text = `{js_safe_msg}`;
                navigator.clipboard.writeText(text).then(function() {{
                    alert("✅ 已複製！");
                }}, function(err) {{
                    alert("❌ 失敗：" + err);
                }});
            }}
            </script>
        """, height=70)


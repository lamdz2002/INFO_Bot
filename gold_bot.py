import requests
from bs4 import BeautifulSoup
import os
import sys

# Ép Python in log ngay lập tức, không chờ bộ đệm
def log(message):
    print(message, flush=True)

def get_gold_data():
    url = "https://www.24h.com.vn/gia-vang-hom-nay-c425.html"
    # Giả lập trình duyệt Chrome mới nhất để tránh bị chặn
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5"
    }
    
    log(f"--- Bắt đầu 'chọc' vào web: {url} ---")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            log(f"❌ Web chặn truy cập (Mã lỗi: {response.status_code})")
            return f"❌ Lỗi web {response.status_code}", None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Tìm bảng giá vàng
        table = soup.find("table")
        if not table:
            log("❌ Không tìm thấy bảng nào!")
            return "❌ Lỗi: Không thấy bảng giá", None
            
        rows = table.find_all("tr")
        log(f"✅ Đã quét thấy {len(rows)} dòng dữ liệu.")

        message = "<b>🌟 GIÁ VÀNG TRỰC TUYẾN 🌟</b>\n"
        message += "<code>-------------------------------</code>\n"
        message += "<code>Loại vàng    | Mua vào | Bán ra</code>\n"
        
        found = 0
        for row in rows[1:8]: 
            cols = row.find_all(["td", "th"])
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)[:10]
                buy = cols[1].get_text(strip=True)
                sell = cols[2].get_text(strip=True)
                if buy and sell:
                    message += f"🔸 <code>{name:<10} | {buy:>7} | {sell:>7}</code>\n"
                    found += 1
        
        # Tìm ảnh biểu đồ
        chart_url = ""
        for img in soup.find_all("img"):
            src = img.get('src', '')
            if any(k in src for k in ["gia-vang", "bieu-do", "do-thi"]):
                chart_url = src if src.startswith("http") else "https://icdn.24h.com.vn" + src
                log(f"📸 Thấy ảnh biểu đồ: {chart_url}")
                break 

        return message, chart_url
    except Exception as e:
        log(f"❌ Lỗi phát sinh: {str(e)}")
        return f"❌ Lỗi: {str(e)}", None

def send_to_telegram(text, image_url):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        log("❌ Thiếu Token/ID trong Secrets!")
        return

    log(f"📤 Đang gửi tới Telegram...")
    
    if image_url:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        data = {"chat_id": chat_id, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    
    try:
        r = requests.post(url, data=data, timeout=20)
        log(f"📡 Phản hồi từ Telegram: {r.status_code}")
        if r.status_code != 200:
            log(f"⚠️ Chi tiết lỗi: {r.text}")
    except Exception as e:
        log(f"❌ Không gửi được tin nhắn: {e}")

if __name__ == "__main__":
    msg, img = get_gold_data()
    send_to_telegram(msg, img)
    log("--- Hoàn thành ---")
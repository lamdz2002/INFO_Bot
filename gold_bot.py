import requests
from bs4 import BeautifulSoup
import os
import sys

def get_gold_data():
    url = "https://www.24h.com.vn/gia-vang-hom-nay-c425.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"--- Đang kết nối tới: {url} ---")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"❌ Lỗi kết nối! Mã lỗi: {response.status_code}")
            return f"❌ Không thể truy cập web (Mã: {response.status_code})", None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Tìm bảng: Thử tìm theo class đặc trưng của 24h hoặc bảng đầu tiên
        table = soup.find("table", {"class": "table-gia-vang"})
        if not table:
            table = soup.find("table") # Nếu không thấy class thì lấy bảng đầu tiên
            
        if not table:
            print("❌ Không tìm thấy thẻ <table> nào trên trang!")
            return "❌ Website đã thay đổi cấu trúc bảng giá!", None
            
        rows = table.find_all("tr")
        print(f"✅ Tìm thấy bảng với {len(rows)} dòng.")

        message = "<b>🌟 GIÁ VÀNG TRỰC TUYẾN 9H 🌟</b>\n"
        message += "<code>-------------------------------</code>\n"
        message += "<code>Loại vàng    | Mua vào | Bán ra</code>\n"
        
        count = 0
        for row in rows[1:10]: # Lấy tối đa 9 dòng
            cols = row.find_all(["td", "th"])
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)[:10]
                buy = cols[1].get_text(strip=True)
                sell = cols[2].get_text(strip=True)
                if buy and sell and any(char.isdigit() for char in buy):
                    message += f"🔸 <code>{name:<10} | {buy:>7} | {sell:>7}</code>\n"
                    count += 1
        
        if count == 0:
            print("❌ Không trích xuất được dòng dữ liệu nào.")
            return "❌ Bảng giá hiện đang trống hoặc chưa cập nhật!", None

        # Tìm ảnh biểu đồ
        chart_url = ""
        for img in soup.find_all("img"):
            src = img.get('data-original', img.get('src', ''))
            if "gia-vang" in src or "bieu-do" in src or "do-thi" in src:
                chart_url = src if src.startswith("http") else "https://icdn.24h.com.vn" + src
                print(f"📸 Tìm thấy ảnh biểu đồ: {chart_url}")
                break 

        return message, chart_url
    except Exception as e:
        print(f"❌ Lỗi phát sinh: {str(e)}")
        return f"❌ Lỗi hệ thống: {str(e)}", None

def send_to_telegram(text, image_url):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ LỖI: Thiếu TOKEN hoặc CHAT_ID trong Secrets!")
        return

    print(f"📤 Đang gửi tới ID: {chat_id}...")
    
    # Thử gửi ảnh trước
    if image_url:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    
    try:
        res = requests.post(url, data=payload, timeout=20)
        print(f"📡 Kết quả từ Telegram: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Không thể kết nối tới API Telegram: {e}")

if __name__ == "__main__":
    msg, img = get_gold_data()
    send_to_telegram(msg, img)
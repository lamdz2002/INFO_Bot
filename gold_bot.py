import requests
from bs4 import BeautifulSoup
import os

def get_gold_data():
    url = "https://www.24h.com.vn/gia-vang-hom-nay-c425.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. LẤY BẢNG GIÁ VÀNG
        table = soup.find("table")
        rows = table.find_all("tr")
        
        message = "<b>🌟 CẬP NHẬT GIÁ VÀNG 9H SÁNG 🌟</b>\n"
        message += "<code>----------------------------------</code>\n"
        message += "<code>Loại vàng      | Mua vào | Bán ra</code>\n"
        
        # Duyệt qua các dòng dữ liệu (lấy 6 dòng đầu)
        for row in rows[1:7]: 
            cols = row.find_all("td")
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)[:12]
                buy = cols[1].get_text(strip=True)
                sell = cols[2].get_text(strip=True)
                # Format căn lề cho đẹp
                message += f"🔸 <code>{name:<12} | {buy:>7} | {sell:>7}</code>\n"

        # 2. LẤY ẢNH BIỂU ĐỒ
        chart_url = ""
        for img in soup.find_all("img"):
            src = img.get('src', '')
            if "bieu-do" in src or "gia-vang" in src:
                chart_url = src if src.startswith("http") else "https://icdn.24h.com.vn" + src
                break 

        return message, chart_url
    except Exception as e:
        return f"Lỗi cào dữ liệu: {e}", None

def send_to_telegram(text, image_url):
    # Lấy thông tin từ biến môi trường (Secrets trên GitHub)
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Mẹo: Để test nhanh trên máy tính, bạn có thể uncomment 2 dòng dưới:
    # token = "8671684569:AAGMuZ6ZtUIZszZiSlGNyDkh0Pav5SPLMV8"
    # chat_id = "6733680300"

    if image_url:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        data = {"chat_id": chat_id, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    
    requests.post(url, data=data)

if __name__ == "__main__":
    msg, img = get_gold_data()
    send_to_telegram(msg, img)
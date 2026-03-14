import requests
from bs4 import BeautifulSoup
import os
import re

def decode_nb_price(nb_val):
    try:
        # Giải mã chuỗi hex từ thuộc tính nb của WebGia
        clean_val = re.sub(r'[A-Z]', '', nb_val)
        result = "".join(chr(int(clean_val[i:i+2], 16)) for i in range(0, len(clean_val) - 1, 2))
        return result
    except: return ""

def format_to_k(p_str):
    """Ép giá về nghìn đồng (VD: 18.100.000 -> 18.100)"""
    num = re.sub(r'[^\d]', '', p_str)
    if not num or len(num) < 4: return "---"
    # Chia 1000 để lấy đơn vị nghìn đồng
    return "{:,.0f}".format(int(num) // 1000).replace(",", ".")

def get_gold_data():
    url = "https://webgia.com/gia-vang/sjc/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. LẤY THỜI GIAN CẬP NHẬT
        time_tag = soup.find("h1", class_="h-head")
        update_time = time_tag.small.get_text(strip=True).split(' ')[-1] if time_tag else ""

        # 2. LẤY BẢNG GIÁ VÀNG
        table = soup.find("table", class_="table-radius")
        rows = table.find_all("tr")
        
        message = f"<b>🌟 SJC {update_time} 🌟</b>\n"
        message += "<i>📍 Đơn vị: nghìn đồng/chỉ</i>\n"
        message += "<code>Vàng  | Mua   | Bán</code>\n"
        message += "<code>----------------------</code>\n"
        
        for row in rows[1:10]: 
            cols = row.find_all("td")
            if len(cols) >= 3:
                # Viết tắt tên để đảm bảo hiển thị 1 dòng
                raw_n = cols[0].get_text(strip=True).replace("Vàng ", "").replace("Nữ trang ", "NT ")
                if "1L" in raw_n: name = "SJC 1L"
                elif "5 chỉ" in raw_n: name = "SJC 5c"
                elif "0.5 chỉ" in raw_n: name = "SJC 0.5"
                elif "nhẫn" in raw_n.lower(): name = "Nhẫn99"
                elif "99,99%" in raw_n: name = "NT99.9"
                else: name = raw_n[:6]
                
                b_raw = decode_nb_price(cols[1]["nb"]) if "nb" in cols[1].attrs else cols[1].get_text(strip=True)
                s_raw = decode_nb_price(cols[2]["nb"]) if "nb" in cols[2].attrs else cols[2].get_text(strip=True)
                
                buy, sell = format_to_k(b_raw), format_to_k(s_raw)
                message += f"🔸<code>{name:<6}|{buy:>5}|{sell:>5}</code>\n"

        # 3. THÊM THÔNG TIN TÀI SẢN CÁ NHÂN (Lấy từ Variables)
        # Nếu không tìm thấy biến, mặc định sẽ hiện "0"
        vnd_asset = os.getenv("USER_VND", "0")
        gold_asset = os.getenv("USER_GOLD", "0")
        
        message += "<code>----------------------</code>\n"
        message += f"💰 <b>TÀI SẢN CỦA TÔI:</b>\n"
        message += f" ├ Tiền mẹ đang cầm: <b>{vnd_asset}</b> VNĐ\n"
        message += f" └ Vàng: <b>{gold_asset}</b> chỉ\n"

        # 4. LẤY ẢNH BIỂU ĐỒ
        chart_url = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else ""
        return message, chart_url
    except Exception as e: return f"❌ Lỗi: {str(e)}", None

def send_to_telegram(text, image_url):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    p = {"chat_id": chat_id, "caption": text, "parse_mode": "HTML"}
    if image_url:
        p["photo"] = image_url
        requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", data=p)
    else:
        p["text"] = text
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data=p)

if __name__ == "__main__":
    msg, img = get_gold_data()
    send_to_telegram(msg, img) 
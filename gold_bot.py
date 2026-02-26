import requests
from bs4 import BeautifulSoup
import os
import re

def decode_nb_price(nb_val):
    try:
        clean_val = re.sub(r'[A-Z]', '', nb_val)
        result = ""
        for i in range(0, len(clean_val) - 1, 2):
            result += chr(int(clean_val[i:i+2], 16))
        return result
    except:
        return "-"

def get_gold_data():
    url = "https://webgia.com/gia-vang/sjc/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. LẤY THỜI GIAN
        time_tag = soup.find("h1", class_="h-head")
        update_time = time_tag.small.get_text(strip=True).replace("- Cập nhật lúc ", "") if time_tag else ""

        # 2. LẤY BẢNG GIÁ
        table = soup.find("table", class_="table-radius")
        rows = table.find_all("tr")
        
        # Header ngắn gọn hơn để tránh tràn dòng
        message = f"<b>🌟 GIÁ VÀNG SJC {update_time.split(' ')[1]} 🌟</b>\n"
        message += "<code>Loại vàng   | Mua vào | Bán ra</code>\n"
        message += "<code>----------------------------</code>\n"
        
        for row in rows[1:10]: 
            cols = row.find_all("td")
            if len(cols) >= 3:
                # Rút ngắn tên loại vàng để tiết kiệm diện tích
                name = cols[0].get_text(strip=True).replace("Vàng ", "").replace("Nữ trang ", "NT ")[:10]
                
                # Giải mã giá
                buy_cell, sell_cell = cols[1], cols[2]
                buy = decode_nb_price(buy_cell["nb"]) if "nb" in buy_cell.attrs else buy_cell.get_text(strip=True)
                sell = decode_nb_price(sell_cell["nb"]) if "nb" in sell_cell.attrs else sell_cell.get_text(strip=True)
                
                # Loại bỏ phần triệu cho gọn (ví dụ 18.100.000 -> 18.100)
                # Hoặc giữ nguyên nhưng bỏ bớt khoảng trắng
                buy_short = buy.replace(".000", "").replace("webgiá.com", "---").strip()
                sell_short = sell.replace(".000", "").replace("web giá", "---").strip()

                # Cấu trúc 1 dòng: Emoji + Tên (10 ký tự) + Mua (6 ký tự) + Bán (6 ký tự)
                message += f"🔸 <code>{name:<10} | {buy_short:>6} | {sell_short:>6}</code>\n"

        # 3. LẤY ẢNH BIỂU ĐỒ
        chart_url = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else ""

        return message, chart_url
    except Exception as e:
        return f"❌ Lỗi: {str(e)}", None

def send_to_telegram(text, image_url):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
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
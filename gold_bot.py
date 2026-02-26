import requests
from bs4 import BeautifulSoup
import os
import re

def decode_nb_price(nb_val):
    """Giải mã giá vàng từ thuộc tính 'nb' của WebGia"""
    try:
        # Loại bỏ tất cả các chữ cái viết hoa [cite: 1104]
        clean_val = re.sub(r'[A-Z]', '', nb_val)
        result = ""
        # Chuyển đổi từ chuỗi Hex sang ký tự 
        for i in range(0, len(clean_val) - 1, 2):
            result += chr(int(clean_val[i:i+2], 16))
        return result
    except:
        return "-"

def get_gold_data():
    url = "https://webgia.com/gia-vang/sjc/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. LẤY THỜI GIAN CẬP NHẬT 
        update_time = "Vừa xong"
        time_tag = soup.find("h1", class_="h-head")
        if time_tag and time_tag.small:
            update_time = time_tag.small.get_text(strip=True).replace("- Cập nhật lúc ", "")

        # 2. LẤY BẢNG GIÁ VÀNG [cite: 763]
        table = soup.find("table", class_="table-radius")
        if not table:
            return "❌ Không tìm thấy bảng giá trên WebGia!", None
            
        rows = table.find_all("tr")
        
        message = f"<b>🌟 GIÁ VÀNG SJC MỚI NHẤT 🌟</b>\n"
        message += f"<i>🕒 {update_time}</i>\n"
        message += "<code>-------------------------------</code>\n"
        message += "<code>Loại vàng    | Mua vào | Bán ra</code>\n"
        
        # Chỉ lấy các dòng dữ liệu của khu vực Hồ Chí Minh để tin nhắn ngắn gọn 
        for row in rows[1:10]: 
            cols = row.find_all("td")
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)[:10]
                
                # Kiểm tra xem giá có bị mã hóa trong 'nb' không [cite: 1106]
                buy_cell = cols[1]
                sell_cell = cols[2]
                
                buy = buy_cell.get_text(strip=True)
                if "nb" in buy_cell.attrs:
                    buy = decode_nb_price(buy_cell["nb"])
                
                sell = sell_cell.get_text(strip=True)
                if "nb" in sell_cell.attrs:
                    sell = decode_nb_price(sell_cell["nb"])
                
                # Làm sạch dữ liệu rác (như chữ "webgiá.com" trong ô mã hóa) [cite: 780]
                if "web" in buy.lower() or not any(char.isdigit() for char in buy): buy = "---"
                if "web" in sell.lower() or not any(char.isdigit() for char in sell): sell = "---"

                message += f"🔸 <code>{name:<10} | {buy:>7} | {sell:>7}</code>\n"

        # 3. LẤY ẢNH BIỂU ĐỒ [cite: 9]
        # Sử dụng ảnh đại diện (Open Graph image) vì nó chứa biểu đồ tổng quát nhất
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
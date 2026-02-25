import requests
from bs4 import BeautifulSoup
import os

def get_gold_data():
    # LUÔN lấy dữ liệu mới nhất từ URL này
    url = "https://www.24h.com.vn/gia-vang-hom-nay-c425.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Tìm tất cả các bảng, thường bảng giá vàng là bảng có nhiều dòng nhất
        tables = soup.find_all("table")
        if not tables:
            return "❌ Không tìm thấy bảng giá nào trên web!", None
            
        table = tables[0] # Lấy bảng đầu tiên
        rows = table.find_all("tr")
        
        message = "<b>🌟 GIÁ VÀNG MỚI NHẤT 🌟</b>\n"
        message += f"<i>(Cập nhật từ live web)</i>\n"
        message += "<code>-------------------------------</code>\n"
        message += "<code>Loại vàng    | Mua vào | Bán ra</code>\n"
        
        found_data = False
        for row in rows[1:8]: 
            cols = row.find_all("td")
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)[:10]
                buy = cols[1].get_text(strip=True)
                sell = cols[2].get_text(strip=True)
                if buy and sell:
                    message += f"🔸 <code>{name:<10} | {buy:>7} | {sell:>7}</code>\n"
                    found_data = True

        if not found_data:
            return "❌ Cào được bảng nhưng nội dung trống!", None

        # Tìm biểu đồ
        chart_url = ""
        for img in soup.find_all("img"):
            src = img.get('src', '')
            if "gia-vang" in src or "bieu-do" in src:
                chart_url = src if src.startswith("http") else "https://icdn.24h.com.vn" + src
                break 

        return message, chart_url
    except Exception as e:
        return f"❌ Lỗi hệ thống: {str(e)}", None

def send_to_telegram(text, image_url):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Kiểm tra xem Token/ID có bị trống không
    if not token or not chat_id:
        print("❌ LỖI: Chưa cấu hình Secrets trên GitHub!")
        return

    # Thử gửi ảnh trước
    if image_url:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        data = {"chat_id": chat_id, "photo": image_url, "caption": text, "parse_mode": "HTML"}
        res = requests.post(url, data=data)
        if res.status_code == 200:
            print("✅ Đã gửi tin nhắn kèm ảnh thành công!")
            return

    # Nếu gửi ảnh lỗi hoặc không có ảnh, gửi tin nhắn văn bản
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    res = requests.post(url, data=data)
    print(f"📡 Kết quả gửi tin nhắn: {res.status_code} - {res.text}")

if __name__ == "__main__":
    msg, img = get_gold_data()
    print(f"📝 Nội dung chuẩn bị gửi:\n{msg}") # In ra để xem trong tab Actions
    send_to_telegram(msg, img)
import json
import os
import sys

def prune_cookies():
    # Get account name from argument or default
    account_name = sys.argv[1] if len(sys.argv) > 1 else ""
    input_path = f"cookies_{account_name}.json" if account_name else "cookies.json"
    output_path = f"cookies_{account_name}_minified.json" if account_name else "cookies_minified.json"

    if not os.path.exists(input_path):
        print(f"❌ ไม่พบไฟล์ {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. เก็บเฉพาะ Cookies (ส่วนใหญ่พอแค่นี้ในการ Login)
    # 2. ล้าง localStorage และ sessionStorage ทิ้ง (ส่วนนี้แหละที่ทำให้ไฟล์ใหญ่)
    minified_data = {
        "cookies": data.get("cookies", []),
        "origins": [] # ลบ localStorage ออกทั้งหมด
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(minified_data, f, separators=(',', ':')) # บีบให้ไม่มีช่องว่าง

    original_size = os.path.getsize(input_path) / 1024
    new_size = os.path.getsize(output_path) / 1024
    
    print(f"✨ บีบอัดเรียบร้อยสำหรับบัญชี: {account_name or 'Default'}")
    print(f"📉 ขนาดเดิม: {original_size:.2f} KB")
    print(f"🚀 ขนาดใหม่: {new_size:.2f} KB")
    print(f"\n✅ กรุณาคัดลอกเนื้อหาในไฟล์ '{output_path}' ไปใส่ใน GitHub Secrets แทนของเดิมครับ")

if __name__ == "__main__":
    prune_cookies()

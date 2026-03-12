import asyncio
from playwright.async_api import async_playwright
import os

async def save_cookies():
    async with async_playwright() as p:
        # ใช้โฟลเดอร์สำหรับเก็บข้อมูล Browser เพื่อให้เหมือนคนใช้งานจริง
        user_data_dir = os.path.join(os.getcwd(), "tiktok_user_data")
        
        # สร้าง Browser แบบเปิดหน้าต่าง (Headless=False)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            no_viewport=True,
            args=['--disable-blink-features=AutomationControlled'],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = context.pages[0] if context.pages else await context.new_page()

        print("--- เริ่มต้นการบันทึก Cookies ---")
        print("1. กรุณา Login TikTok ในหน้าต่างที่เปิดขึ้นมา")
        print("2. แนะนำให้ใช้ Phone/Email/Username หรือ Google หาก QR Code ไม่ทำงาน")
        
        try:
            await page.goto("https://www.tiktok.com/login", wait_until="networkidle")

            # รายชื่อ Element ที่บอกว่า Login สำเร็จแล้ว
            selectors = [
                '[data-e2e="profile-icon"]',
                '[data-e2e="nav-inbox"]',
                '[data-e2e="nav-foryou"]',
                '.avatar-anchor'
            ]
            
            success = False
            # รอ Login สูงสุด 4 นาที (เช็คทุก 5 วินาที)
            for i in range(48): 
                try:
                    for selector in selectors:
                        el = await page.query_selector(selector)
                        if el:
                            print(f"\n✅ ตรวจพบการ Login สำเร็จ! (ทาง {selector})")
                            success = True
                            break
                    
                    if success:
                        break
                    
                    await asyncio.sleep(5)
                    if i % 4 == 0:
                        print(f"กำลังรอ Login... ({i*5} วินาทีผ่านไป)")
                except Exception:
                    pass

            if success:
                print("กำลังบันทึกข้อมูล Session...")
                await asyncio.sleep(5) # รอให้ Cookie เซ็ตตัว
                await context.storage_state(path="cookies.json")
                print("✨ บันทึกไฟล์ cookies.json เรียบร้อยแล้ว!")
            else:
                print("❌ หมดเวลาการ Login (Timeout)")

        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
        finally:
            await context.close()
            print("--- ปิด Browser เรียบร้อย ---")

if __name__ == "__main__":
    asyncio.run(save_cookies())

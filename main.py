import asyncio
import os
import sys
import random
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Reconfigure stdout and stderr to UTF-8 to prevent UnicodeEncodeError with emojis on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

async def run_bot():
    # Get account name from argument or default
    account_name = sys.argv[1] if len(sys.argv) > 1 else ""
    
    # Define filenames
    env_file = f".env.{account_name}" if account_name else ".env"
    cookies_path = f"cookies_{account_name}.json" if account_name else "cookies.json"

    # Load specific env if it exists
    if os.path.exists(env_file):
        print(f"📁 Loading configuration from {env_file}")
        load_dotenv(env_file)
    else:
        print(f"📁 Using default .env (or no env if not found)")
        load_dotenv()

    # Configuration
    FRIENDS_TO_STREAK = [f.strip() for f in os.getenv("FRIENDS_TO_STREAK", "").split(",") if f.strip()]
    MESSAGE_POOL = os.getenv("STREAK_MESSAGES", "🔥,Let's go!,Good morning,เดี๋ยวไฟดับนะ!,Check-in,Refill 🔥").split(",")
    
    print(f"Bot starting for account: {account_name or 'Default'}... (Headless: {os.getenv('HEADLESS', 'true')})")

    if not os.path.exists(cookies_path):
        print(f"❌ ไม่พบไฟล์ {cookies_path}")
        return

    async with async_playwright() as p:
        is_headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser = await p.chromium.launch(
            headless=is_headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            storage_state=cookies_path,
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()

        print("🚀 กำลังไปที่หน้า TikTok Inbox...")
        try:
            await page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded", timeout=60000)
            print("รอหน้า Inbox โหลด (10 วินาที)...")
            await asyncio.sleep(10)

            sent_count = 0
            
            for full_name in FRIENDS_TO_STREAK:
                search_name = full_name[:3] if len(full_name) > 3 else full_name
                print(f"\n🔍 [กำลังหา]: {full_name} (คำค้น: {search_name})")
                
                try:
                    found = False
                    for attempt in range(15): 
                        chat_selector = page.get_by_text(search_name, exact=False).locator("visible=true").first
                        
                        if await chat_selector.count() > 0:
                            print(f"✅ พบ '{search_name}' แล้ว กำลังคลิก...")
                            await chat_selector.click()
                            await asyncio.sleep(5)
                            found = True
                            break
                        
                        await page.mouse.move(250, 400)
                        await page.mouse.wheel(0, 500)
                        await asyncio.sleep(1.5)

                    if found:
                        streak_message = random.choice(MESSAGE_POOL)
                        input_field = page.locator('[data-e2e="messenger-edit-input"], div[contenteditable="true"], [placeholder*="message"]').first
                        
                        try:
                            await input_field.wait_for(state="visible", timeout=15000)
                            await input_field.click()
                            
                            await page.keyboard.press("Control+A")
                            await page.keyboard.press("Backspace")
                            await page.keyboard.type(streak_message, delay=random.randint(50, 150))
                            await asyncio.sleep(1.5)
                            
                            await page.keyboard.press("Enter")
                            send_icon = page.locator('[data-e2e="messenger-send-icon"], button[aria-label*="Send"]').first
                            if await send_icon.is_visible(): await send_icon.click()
                            
                            await asyncio.sleep(4)
                            
                            if (await input_field.inner_text()).strip() == "":
                                print(f"✅ ยืนยันการส่งให้ {full_name} สำเร็จ")
                                sent_count += 1
                            else:
                                print(f"❌ ส่งล้มเหลว ข้อความยังค้างอยู่สำหรับ {full_name}")
                            
                            await asyncio.sleep(random.uniform(5, 8))
                        except Exception as e:
                            print(f"⚠️ พลาดที่ขั้นตอนการส่งให้ {full_name}: {e}")
                    else:
                        print(f"❌ หาแชทของ {full_name} ไม่เจอหลังจากเลื่อน 15 ครั้ง")
                        
                except Exception as e:
                    print(f"❌ พลาด: {e}")

            print(f"\n🏁 ภารกิจเสร็จสิ้น! ส่งสำเร็จจริงทั้งหมด {sent_count} คน")

        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            await page.screenshot(path=f"error_{account_name or 'default'}.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot())

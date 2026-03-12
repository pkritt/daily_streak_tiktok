import asyncio
import os
import random
import time
import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FRIENDS_TO_STREAK = [f.strip() for f in os.getenv("FRIENDS_TO_STREAK", "").split(",") if f.strip()]
MESSAGE_POOL = os.getenv("STREAK_MESSAGES", "🔥,Let's go!,Good morning,เดี๋ยวไฟดับนะ!,Check-in").split(",")
COOKIES_PATH = "cookies.json"
LINE_TOKEN = os.getenv("LINE_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_notification(message):
    """Sends notification to LINE or Telegram."""
    if LINE_TOKEN:
        try:
            url = 'https://notify-api.line.me/api/notify'
            headers = {'Authorization': f'Bearer {LINE_TOKEN}'}
            requests.post(url, headers=headers, data={'message': message}, timeout=10)
        except Exception as e:
            print(f"Failed to send LINE Notify: {e}")
            
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': message}, timeout=10)
        except Exception as e:
            print(f"Failed to send Telegram: {e}")

async def run_bot():
    # 1. Random Start Delay (Offset scheduling)
    # Only if not in CI (GitHub Actions already has some jitter, but we can add 1-15 mins)
    start_delay = random.randint(1, 900) # 1 to 15 minutes
    print(f"Bot starting... waiting {start_delay} seconds for human-like behavior.")
    await asyncio.sleep(start_delay)

    if not os.path.exists(COOKIES_PATH):
        error_msg = f"❌ Error: {COOKIES_PATH} not found. Please run save_cookies.py first."
        print(error_msg)
        send_notification(error_msg)
        return

    async with async_playwright() as p:
        # Launch browser with stealth
        # Headless for GitHub Actions, can be false for home server testing
        is_headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser = await p.chromium.launch(headless=is_headless)
        
        # Load the saved session state
        context = await browser.new_context(
            storage_state=COOKIES_PATH,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        await stealth_async(page)

        print("Navigating to TikTok Messages...")
        try:
            await page.goto("https://www.tiktok.com/messages", wait_until="networkidle", timeout=60000)
            
            # Wait for message items to load
            try:
                await page.wait_for_selector('[data-e2e="messenger-list-item"], [data-e2e="chat-item"]', timeout=45000)
            except:
                error_msg = "⚠️ Timed out waiting for message list. The session might have expired or a CAPTCHA appeared."
                print(error_msg)
                if os.getenv("CI") or not is_headless:
                    await page.screenshot(path="error_screenshot.png")
                send_notification(error_msg)
                return
            
            # Get all conversation items
            conversations = await page.query_selector_all('[data-e2e="messenger-list-item"], [data-e2e="chat-item"]')
            print(f"Found {len(conversations)} conversations.")

            count = 0
            for conversation in conversations:
                # Human-like delay before clicking each conversation
                await asyncio.sleep(random.uniform(2, 5))

                # Get friend's name
                name_el = await conversation.query_selector('[data-e2e="chat-item-nickname"], span') 
                name = await name_el.inner_text() if name_el else "Unknown"
                
                # Filter by friends list if provided
                if FRIENDS_TO_STREAK and name not in FRIENDS_TO_STREAK:
                    continue
                
                print(f"Processing fire for: {name}")
                
                # 2. Click conversation
                await conversation.click()
                await asyncio.sleep(random.uniform(3, 7)) # Delay after click
                
                # 3. Message Pool & Type Simulation
                streak_message = random.choice(MESSAGE_POOL)
                input_field = page.locator('[data-e2e="messenger-edit-input"]')
                await input_field.wait_for(state="visible")
                
                # Simulate human typing
                await input_field.click() # Ensure focused
                for char in streak_message:
                    await page.keyboard.press(char)
                    await asyncio.sleep(random.uniform(0.1, 0.4)) # Random delay between keystrokes
                
                await asyncio.sleep(random.uniform(1, 2))
                
                # 4. Send message
                send_button = page.locator('[data-e2e="messenger-send-icon"]')
                await send_button.click()
                
                print(f"Successfully sent '{streak_message}' to {name}.")
                count += 1
                
                # Longer delay between different friends
                await asyncio.sleep(random.uniform(10, 20))
                
                # Safety limit if no friends list is provided
                if not FRIENDS_TO_STREAK and count >= 5:
                    break

            success_msg = f"✅ Done! Refilled fire for {count} friends."
            print(success_msg)
            # Only notify if we actually did something (or if you want daily report)
            # send_notification(success_msg)
            
        except Exception as e:
            error_msg = f"❌ An error occurred in TikTok Bot: {e}"
            print(error_msg)
            if os.getenv("CI") or not is_headless:
                await page.screenshot(path="error_screenshot.png")
            send_notification(error_msg)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot())

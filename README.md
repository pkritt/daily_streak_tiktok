# TikTok Daily Streak Bot 🔥

Automate your TikTok "Refill Fire" (Daily Streak) interactions using Playwright and GitHub Actions.

## Setup Instructions

### 1. Local Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Run the cookie saver script:
   ```bash
   python save_cookies.py
   ```
4. A browser window will open. Log in to your TikTok account manually.
5. Once logged in, the script will detect the session and save it to `cookies.json`.

### 2. GitHub Actions Setup
1. Go to your GitHub Repository **Settings > Secrets and variables > Actions**.
2. **Secrets**:
   - Create a new secret called `TIKTOK_COOKIES`.
   - Convert your `cookies.json` to base64:
     - Windows (PowerShell): `[Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies.json"))`
     - Linux/Mac: `base64 -i cookies.json`
   - Paste the base64 string into the `TIKTOK_COOKIES` secret.
3. **Variables**:
   - `FRIENDS_TO_STREAK`: Comma-separated list of friend names.
   - `STREAK_MESSAGES`: Comma-separated list of messages (e.g., `🔥,Good luck,Check-in`).
   - `LINE_TOKEN`: Your LINE Notify token for error alerts.
   - `TELEGRAM_TOKEN` & `TELEGRAM_CHAT_ID`: Your Telegram bot details.

### 3. Home Server Setup (Raspberry Pi / PC)
If you want to avoid GitHub's IP range (which TikTok might block):
1. Install Python and dependencies on your local machine/server.
2. Set up a Cron job (Linux) or Task Scheduler (Windows).
   - **Linux (crontab -e)**: `0 8 * * * cd /path/to/project && python3 main.py`
3. Ensure `cookies.json` is in the project directory.

## Advanced Features (Anti-Detection)
- **Random Offset**: The bot randomly waits 1-15 minutes before starting.
- **Type Simulation**: Characters are typed one by one with random delays (0.1s - 0.4s).
- **Message Pool**: Randomly selects a message from your `STREAK_MESSAGES` list to avoid being flagged as spam.
- **Human Delays**: Random pauses between clicks and between different friends.
- **Stealth Mode**: Uses `playwright-stealth` to hide automation signals.

## Troubleshooting
If the bot fails:
1. Check the `error_screenshot.png` (in GitHub Actions Artifacts or local folder).
2. If you see a login screen or CAPTCHA, your `cookies.json` has expired. Run `python save_cookies.py` again.

## Security Warning
- **Never commit `cookies.json` or `.env` to your repository.**
- Your session cookies allow anyone with them to access your account. Treat them like a password.

## Disclaimer
This project is for educational purposes. Use it at your own risk. Automating TikTok may violate their Terms of Service.

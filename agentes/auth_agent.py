import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

async def login(page):
    '''
    Handles the authentication flow for Totvs Web.
    '''
    user = os.getenv('TOTVS_USER')
    password = os.getenv('TOTVS_PASSWORD')
    url = os.getenv('TOTVS_URL')

    if not all([user, password, url]):
        print('Error: TOTVS_USER, TOTVS_PASSWORD or TOTVS_URL not found in .env')
        return False

    print(f'Navigating to {url}...')
    await page.goto(url)

    # PT-BR Selectors (Assumed based on common Totvs patterns, to be validated)
    # Using specific selectors if possible, or generic ones
    try:
        print('Filling credentials...')
        # Wait for the login field (adjust selectors based on real UI)
        await page.wait_for_selector('input[name="user"]', timeout=10000)
        await page.fill('input[name="user"]', user)
        await page.fill('input[name="password"]', password)
        
        # Click the login button (PT-BR: Entrar / Login)
        print('Clicking Login button...')
        await page.click('button:has-text("Entrar")')
        
        # Wait for navigation or a success indicator
        await page.wait_for_load_state('networkidle')
        
        # Check for success (e.g., presence of a menu or specific element)
        # For now, we take a screenshot to verify
        screenshot_path = os.path.join(os.getenv('DEBUG_SCREENSHOT_PATH', './logs/screenshots/'), 'login_result.png')
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        await page.screenshot(path=screenshot_path)
        print(f'Login attempt finished. Screenshot saved to {screenshot_path}')
        
        return True
    except Exception as e:
        print(f'An error occurred during login: {e}')
        # Take a screenshot even on error for debugging
        screenshot_path = os.path.join(os.getenv('DEBUG_SCREENSHOT_PATH', './logs/screenshots/'), 'login_error.png')
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        await page.screenshot(path=screenshot_path)
        print(f'Error screenshot saved to {screenshot_path}')
        return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        success = await login(page)
        if success:
            print('Login script executed successfully.')
        else:
            print('Login script failed.')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

"""
Setup script to load cookies and storage into the persistent Chrome profile.
Run this once to set up your Dropbox session, then use download_dropbox.py for downloads.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from cookie_loader import load_json_cookies, load_local_storage, load_session_storage


def main():
    print("="*60)
    print("Dropbox Session Setup")
    print("="*60)
    print()
    
    # Set up Chrome options with the same profile as download_dropbox.py
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Load user agent from file if it exists
    try:
        with open("useragent.txt", "r") as f:
            user_agent = f.read().strip()
            chrome_options.add_argument(f"--user-agent={user_agent}")
            print(f"✓ Loaded user agent from useragent.txt")
    except FileNotFoundError:
        print("⚠ useragent.txt not found, using default user agent")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        )
    
    # Enable remote debugging on port 9222 for DevTools MCP access
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Use the same user data directory as download_dropbox.py to persist session
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-debug")

    # Initialize the driver
    print("Starting Chrome browser...")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Visit Dropbox domain first
        print("Visiting Dropbox domain...")
        driver.get("https://www.dropbox.com")
        time.sleep(2)

        # Load all storage types
        print("\nLoading session data...")
        print("-" * 60)
        
        print("Loading cookies from cookies.txt...")
        load_json_cookies(driver, "cookies.txt")
        
        print("Loading local storage from localstorage.json...")
        load_local_storage(driver, "localstorage.json")
        
        print("Loading session storage from sessionstorage.json...")
        load_session_storage(driver, "sessionstorage.json")

        # Refresh to apply all storage changes
        print("\nRefreshing page to apply all changes...")
        driver.refresh()
        time.sleep(3)

        print("\n" + "="*60)
        print("Session setup complete!")
        print("="*60)
        print("\nYour Dropbox session has been saved to the Chrome profile.")
        print("You can now use download_dropbox.py without loading cookies each time.")
        print("\nThe browser will stay open for you to verify the login.")
        print("Press Enter when you're done to close the browser...")
        
        input()

    finally:
        driver.quit()
        print("\nBrowser closed. Session has been saved!")


if __name__ == "__main__":
    main()

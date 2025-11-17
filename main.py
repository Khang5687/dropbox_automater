url = "https://www.dropbox.com/scl/fo/p3za42p2itpgrsbux8gr5/AM3_CJTIrUZLERQiBKWHUIk?rlkey=gchwni1c2z79e2cx3d44tsazv&st=b9y4jc6e&dl=0"

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


def load_netscape_cookies(driver, cookie_file):
    """Load cookies from Netscape format file into Selenium driver"""
    with open(cookie_file, "r") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse Netscape cookie format
            # Format: domain flag path secure expiration name value
            try:
                parts = line.split("\t")
                if len(parts) == 7:
                    domain, flag, path, secure, expiration, name, value = parts

                    cookie_dict = {
                        "name": name,
                        "value": value,
                        "domain": domain,
                        "path": path,
                        "secure": secure == "TRUE",
                        "expiry": int(expiration) if expiration.isdigit() else None,
                    }

                    # Remove expiry if it's None
                    if cookie_dict["expiry"] is None:
                        del cookie_dict["expiry"]

                    driver.add_cookie(cookie_dict)
            except Exception as e:
                print(f"Error parsing cookie line: {line[:50]}... - {e}")
                continue


def main():
    # Set up Chrome options for remote debugging
    # This enables Chrome DevTools Protocol so MCP can access the browser
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Enable remote debugging on port 9222 for DevTools MCP access
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Optional: start with a specific user data directory to persist session
    # chrome_options.add_argument("--user-data-dir=/tmp/chrome-debug")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # First, visit the domain to establish a session
        driver.get(
            "https://www.dropbox.com/scl/fo/p3za42p2itpgrsbux8gr5/AM3_CJTIrUZLERQiBKWHUIk?rlkey=gchwni1c2z79e2cx3d44tsazv&st=b9y4jc6e&dl=0"
        )
        time.sleep(2)

        # Load cookies from the Netscape format file
        print("Loading cookies...")
        load_netscape_cookies(driver, "cookies.txt")

        # Now navigate to the target URL
        print(f"Navigating to: {url}")
        driver.get(url)

        # Wait for page to load
        time.sleep(5)

        # Print page title and current URL
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Print DevTools connection info
        print("\n" + "="*60)
        print("Chrome DevTools is now accessible!")
        print("You can now use the DevTools MCP tools in VS Code to:")
        print("  - Take screenshots")
        print("  - Inspect elements")
        print("  - View console messages")
        print("  - Monitor network requests")
        print("  - And more!")
        print("="*60 + "\n")

        # Keep browser open for inspection (remove in production)
        input("Press Enter to close the browser...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()

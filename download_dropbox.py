from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
from pathlib import Path
import os
import argparse

url = "https://www.dropbox.com/scl/fo/p3za42p2itpgrsbux8gr5/AM3_CJTIrUZLERQiBKWHUIk?rlkey=gchwni1c2z79e2cx3d44tsazv&st=b9y4jc6e&dl=0"

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Download first file from Dropbox shared folder')
    parser.add_argument('--url', action='store_true', 
                       help='Use URL-based download instead of clicking the download button')
    args = parser.parse_args()
    
    # Set up Chrome options for remote debugging
    # This enables Chrome DevTools Protocol so MCP can access the browser
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "--user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'"
    )
    
    # Enable remote debugging on port 9222 for DevTools MCP access
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Optional: start with a specific user data directory to persist session
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-debug")
    
    # Configure download directory and preferences
    download_dir = Path("downloads").resolve()
    download_dir.mkdir(exist_ok=True)
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    })

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate directly to the target URL (session is persisted in profile)
        print(f"Navigating to: {url}")
        driver.get(url)

        # Wait for the grid to be present
        print("Waiting for Dropbox grid to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="sl-grid-body"]'))
        )
        
        # Handle cookie consent banner if present
        try:
            print("Checking for cookie consent banner...")
            consent_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="accept_all_cookies_button"]'))
            )
            consent_btn.click()
            print("Cookie consent accepted")
            time.sleep(1)
        except TimeoutException:
            print("No cookie banner detected")
        
        # Locate the first file card
        print("Locating the first file in the grid...")
        grid = driver.find_element(By.CSS_SELECTOR, '[data-testid="sl-grid-body"]')
        
        # Wait for at least one card to appear
        WebDriverWait(driver, 10).until(
            lambda d: len(grid.find_elements(By.CSS_SELECTOR, 'li._sl-card_to1nz_25')) > 0
        )
        
        first_card = grid.find_elements(By.CSS_SELECTOR, 'li._sl-card_to1nz_25')[0]
        
        # Get file name and link for logging
        try:
            file_link = first_card.find_element(By.CSS_SELECTOR, '[data-testid="grid-link"]')
            file_name = file_link.text
            preview_url = file_link.get_attribute('href')
            print(f"First file found: {file_name}")
        except:
            file_name = "unknown"
            preview_url = None
            print("First file found (name could not be retrieved)")
        
        # Download using URL-based method or button click
        if args.url and preview_url:
            # URL-based download: replace dl=0 with dl=1
            print("Using URL-based download method...")
            download_url = preview_url.replace('dl=0', 'dl=1')
            print(f"Navigating to download URL: {download_url}")
            driver.get(download_url)
            print(f"Download initiated for: {file_name}")
        else:
            # Button-click method (default)
            print("Using button-click download method...")
            
            # Hover over the card to reveal download controls
            print("Hovering over file card to reveal download button...")
            ActionChains(driver).move_to_element(first_card).pause(0.5).perform()
            
            # Wait for and click the download button
            print("Clicking download button...")
            try:
                download_btn = WebDriverWait(first_card, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, './/button[.//svg[@aria-label="Download"]]')
                    )
                )
                download_btn.click()
            except ElementClickInterceptedException:
                # Fallback to JavaScript click if regular click is intercepted
                print("Regular click intercepted, using JavaScript click...")
                download_btn = first_card.find_element(By.XPATH, './/button[.//svg[@aria-label="Download"]]')
                driver.execute_script("arguments[0].click();", download_btn)
            
            print(f"Download initiated for: {file_name}")
        
        # Wait for download to complete
        print("Waiting for download to complete...")
        download_dir = Path("downloads").resolve()
        timeout = 5000
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if any .crdownload files exist (Chrome's in-progress download extension)
            crdownload_files = list(download_dir.glob("*.crdownload"))
            if crdownload_files:
                print("Download in progress...")
                time.sleep(1)
                continue
            
            # Check if any files were downloaded
            downloaded_files = [f for f in download_dir.iterdir() if f.is_file()]
            if downloaded_files:
                print(f"\n{'='*60}")
                print(f"Download complete!")
                print(f"File saved to: {downloaded_files[-1]}")
                print(f"{'='*60}\n")
                break
            
            time.sleep(1)
        else:
            print("Download timeout - file may still be downloading")
        
        # Keep browser open for inspection
        input("Press Enter to close the browser...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()

# Dropbox Shared Folder – First File Download Research

## Goal
Automate the Dropbox shared-folder UI so Selenium consistently downloads exactly the first file displayed in the folder grid, regardless of file name or type.

## Page Observations (via Chrome DevTools)
- Shared-folder body uses `div[data-testid="sl-grid"]` containing `ol[data-testid="sl-grid-body"]`. Each file entry is a `<li>` (`class="_sl-card_to1nz_25"`). DOM order already matches the UI order, so `li:first-child` is the first file the user sees.
- Inside each card:
  - Thumbnail + hover overlay live in `div[data-testid="sl-card-media"]`.
  - File name link: `a[data-testid="grid-link"]` with text, pointing to a preview URL such as `.../AKu5-xhfDagq2Rm-PJpfTdc/GS12-S-C_1.jpg?dl=0`. Replacing `dl=0` with `dl=1` yields the direct download endpoint.
  - Two icon buttons exist in the hover overlay: Copy + Download. The button that triggers the file download contains an `<svg aria-label="Download">`.
- The hover overlay (`div.dig-Card-Actions`) starts with `style="opacity: 0;"`. Dropbox raises opacity to `1` after a pointer hover. Without hovering, Selenium clicks are ignored because the buttons are visually hidden.
- A privacy/cookie banner (`div[data-testid="ccpa_consent_banner"]`) appears on page load and blocks interactions until a button such as `[data-testid="accept_all_cookies_button"]` or `[data-testid="decline_cookies_button"]` is clicked.

## Automation Strategy
1. **Prepare the driver**
   - Configure Chrome download preferences so files save without a prompt:
     ```python
     chrome_options.add_experimental_option("prefs", {
         "download.default_directory": str(Path("downloads").resolve()),
         "download.prompt_for_download": False,
         "safebrowsing.enabled": True,
     })
     ```
   - Optional: reuse cookies (`cookies.txt`) before visiting the folder to avoid repeated consent dialogs.

2. **Navigate & clear blockers**
   - `driver.get(shared_link)` and wait until `presence_of_element_located((By.CSS_SELECTOR, '[data-testid="sl-grid-body"]'))`.
   - Handle the cookie banner if present:
     ```python
     try:
         consent = WebDriverWait(driver, 5).until(
             EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="accept_all_cookies_button"]'))
         )
         consent.click()
     except TimeoutException:
         pass  # banner did not render
     ```

3. **Locate the first card**
   - Grab the first `<li>` under the grid body:
     ```python
     grid = driver.find_element(By.CSS_SELECTOR, '[data-testid="sl-grid-body"]')
     first_card = WebDriverWait(driver, 10).until(
         lambda d: grid.find_elements(By.CSS_SELECTOR, 'li._sl-card_to1nz_25')[0]
     )
     ```
   - Because Dropbox lazily populates the list, guard against empty results with a loop + timeout.

4. **Reveal the inline Download control**
   - Hover over `first_card` to force the overlay opacity to 1:
     ```python
     ActionChains(driver).move_to_element(first_card).pause(0.5).perform()
     ```
   - Wait for the Download icon button inside the hovered card to become clickable. XPath is the most stable because the button’s class names are obfuscated but the nested SVG carries `aria-label="Download"`:
     ```python
     download_btn = WebDriverWait(first_card, 10).until(
         EC.element_to_be_clickable(
             (By.XPATH, './/button[.//svg[@aria-label="Download"]]'))
     )
     download_btn.click()
     ```
   - If `ElementClickInterceptedException` occurs (rare when overlay fades in slowly), fall back to executing `driver.execute_script("arguments[0].click();", download_btn)` after the hover pause.

5. **Verify download completion**
   - Chrome reports finished downloads by creating files in `download.default_directory`. Poll for the expected file (or for a `.crdownload` file to disappear) before ending the session.
   - Because we always click the first card, the code never hard-codes the file name. For validation during development you can assert that the downloaded filename matches the anchor text retrieved via `first_card.find_element(By.CSS_SELECTOR, '[data-testid="grid-link"]').text`.

## Alternative (URL-based) Download
If interacting with the hover overlay is flaky in headless runs, derive the download URL from the first card instead:
```python
first_link = first_card.find_element(By.CSS_SELECTOR, '[data-testid="grid-link"]')
download_url = first_link.get_attribute('href').replace('dl=0', 'dl=1')
driver.get(download_url)  # or requests.get(download_url, cookies=session_cookies)
```
Dropbox responds with the binary payload directly for files, so the browser saves it automatically. This approach still uses Selenium to identify “first file” via DOM order but skips the overlay buttons entirely.

## Testing via `main.py`
To test quickly:
1. Load cookies (already implemented in `main.py`) so the folder opens without extra auth.
2. After the current wait block, insert the logic from steps 2–5 above, and point the download directory to a temp folder inside the repo (e.g., `./downloads`).
3. Run `python main.py`, confirm that only a single file appears in your downloads, and clean the directory between runs.

These findings should give you enough structure to implement a robust Selenium routine that always pulls whichever file is displayed first in any Dropbox shared folder.

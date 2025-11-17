# How to Use Dropbox Automater

This guide will help you set up and use the Dropbox automater to download files from Dropbox shared folders.

## Prerequisites

- Python 3.x installed
- Chrome browser installed
- ChromeDriver installed and in your PATH

## Setup Steps

### 1. Install Required Python Packages

```bash
pip install selenium
```

### 2. Export Your Browser Session Data

You need to export three types of data from your logged-in Chrome browser session:

#### A. Export Cookies

1. Install the **EditThisCookie** extension:
   - Visit: https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol
   - Click "Add to Chrome" to install

2. Log into Dropbox in your Chrome browser (if not already logged in)

3. While on the Dropbox page, click the EditThisCookie extension icon

4. Click the "Export" button (looks like a document icon)

5. Save the exported data to a file named `cookies.txt` in this directory

#### B. Export Local Storage

1. Open Chrome DevTools (press `F12` or right-click → Inspect)

2. Go to the **Console** tab

3. Copy and paste this command and press Enter:

```javascript
copy(JSON.stringify(localStorage))
```

4. Paste the clipboard content into a file named `localstorage.json` in this directory

#### C. Export Session Storage

1. In the same Chrome DevTools Console tab, run:

```javascript
copy(JSON.stringify(sessionStorage))
```

2. Paste the clipboard content into a file named `sessionstorage.json` in this directory

#### D. Export User Agent

1. In the same Chrome DevTools Console tab, run:

```javascript
navigator.userAgent
```

2. Copy the output string (including the quotes) and paste it into a file named `useragent.txt` in this directory

## Running the Script

### Basic Usage

To download the first file from a Dropbox shared folder:

```bash
python download_dropbox.py
```

By default, this uses the button-click method to download files.

### URL-Based Download Method

To use the URL-based download method instead:

```bash
python download_dropbox.py --url
```

### Configuration

Edit the `url` variable in `download_dropbox.py` to point to your target Dropbox shared folder:

```python
url = "https://www.dropbox.com/scl/fo/..."
```

## File Structure

After setup, your directory should contain:

```
dropbox_automater/
├── download_dropbox.py      # Main script
├── cookie_loader.py          # Cookie/storage loading utilities
├── cookies.txt               # Your exported cookies (JSON format)
├── localstorage.json         # Your exported localStorage
├── sessionstorage.json       # Your exported sessionStorage
├── useragent.txt             # Your browser's user agent string
├── downloads/                # Downloaded files will be saved here
└── HOW_TO_USE.md            # This file
```

## Troubleshooting

### "unable to set cookie" Errors

- Make sure you're visiting Dropbox in your regular Chrome browser before exporting
- Ensure all three storage files (cookies.txt, localstorage.json, sessionstorage.json) are properly exported
- Try re-exporting your session data if cookies have expired

### Download Button Not Found

- Try using the `--url` flag for URL-based downloads
- Make sure you're logged into Dropbox and have access to the shared folder
- Check that the shared folder URL is correct and accessible

### Session Expires Quickly

- Re-export your session data (cookies, localStorage, sessionStorage)
- Make sure your browser's user agent matches what's configured in the script
- Some security tokens may have short expiration times

## Notes

- The script will download files to the `downloads/` directory
- Session data (cookies, localStorage, sessionStorage) may expire after some time and need to be re-exported
- Keep your session data files private as they contain authentication tokens
- The script currently downloads the first file in the grid view

## Security Warning

⚠️ **Important**: The `cookies.txt`, `localstorage.json`, and `sessionstorage.json` files contain sensitive authentication data. Do NOT share these files or commit them to version control. Add them to your `.gitignore` file.

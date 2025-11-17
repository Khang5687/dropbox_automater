# How to Use Dropbox Automater

This guide will help you set up and use the Dropbox automater to download files from Dropbox shared folders.

## Prerequisites

- Python 3.x installed
- Chrome browser installed
- ChromeDriver installed and in your PATH

## Quick Start

### 1. Install Required Python Packages

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install selenium pandas openpyxl
```

### 2. Create Configuration Files

Run the setup script to create empty configuration files:

```bash
./create_var.sh
```

This will create:
- `cookies.txt`
- `localstorage.json`
- `sessionstorage.json`
- `useragent.txt`

### 3. Export Your Browser Session Data

You need to export three types of data from your logged-in Chrome browser session:

#### A. Export Cookies

1. Install the **EditThisCookie** extension:
   - Visit: https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol
   - Click "Add to Chrome" to install

2. Log into Dropbox in your Chrome browser (if not already logged in)

3. While on the Dropbox page, click the EditThisCookie extension icon

4. Click the "Export" button (looks like a document icon)

5. Replace the contents of `cookies.txt` with the exported data

#### B. Export Local Storage

1. Open Chrome DevTools (press `F12` or right-click → Inspect)

2. Go to the **Console** tab

3. Copy and paste this command and press Enter:

```javascript
copy(JSON.stringify(localStorage))
```

4. Replace the contents of `localstorage.json` with the clipboard content

#### C. Export Session Storage

1. In the same Chrome DevTools Console tab, run:

```javascript
copy(JSON.stringify(sessionStorage))
```

2. Replace the contents of `sessionstorage.json` with the clipboard content

#### D. Export User Agent

1. In the same Chrome DevTools Console tab, run:

```javascript
navigator.userAgent
```

2. Copy the output string (without quotes) and replace the contents of `useragent.txt`

### 4. One-Time Session Setup

Run the session setup script to load your session data into the persistent Chrome profile:

```bash
python setup_session.py
```

This will:
- Load all your cookies, localStorage, and sessionStorage into Chrome
- Save the session to a persistent profile
- Keep the browser open for you to verify you're logged in
- You only need to do this once (or when your session expires)

### 5. Batch Download Files from Excel

The main script allows you to batch download images from multiple Dropbox folders using an Excel file:

#### Excel File Format

Create an Excel file (.xlsx) with two columns:
- **Column 1: UPC** - The product code to use as filename
- **Column 2: IMAGE_LINK** - The Dropbox shared folder URL

Example:
```
| UPC        | IMAGE_LINK                                           |
|------------|------------------------------------------------------|
| 123456789  | https://www.dropbox.com/scl/fo/abc123...             |
| 987654321  | https://www.dropbox.com/scl/fo/xyz789...             |
```

#### Basic Usage

```bash
python main.py /path/to/Book1.xlsx output
```

This will:
- Read the Excel file
- Download the first image from each Dropbox folder
- Rename each file to its UPC code (keeping the original extension)
- Save to the `output/` directory
- Skip files that already exist (won't overwrite)

#### Parallel Downloads

Use multiple threads to download faster:

```bash
python main.py /path/to/Book1.xlsx output --threads 4
```

#### Debug Mode

Enable verbose output for troubleshooting:

```bash
python main.py /path/to/Book1.xlsx output --debug
```

#### Output

The script will show:
- Progress for each download
- ✓ Successfully downloaded files
- ⊘ Skipped files (already exist)
- ✗ Failed downloads
- Summary statistics at the end
- A log file of failed downloads (if any)

### 6. Download Single File (Testing)

For testing or downloading a single file:

```bash
python download_dropbox.py
```

Options:
- `--debug` - Enable verbose debug output
- `--alt` - Use button-click method instead of URL-based download (default)
- `--output DIR` - Specify output directory (default: downloads)

## File Structure

After setup, your directory should contain:

```
dropbox_automater/
├── download_dropbox.py      # Main download script
├── setup_session.py          # One-time session setup script
├── cookie_loader.py          # Cookie/storage loading utilities
├── create_var.sh             # Script to create empty config files
├── cookies.txt               # Your exported cookies (JSON format)
├── localstorage.json         # Your exported localStorage
├── sessionstorage.json       # Your exported sessionStorage
├── useragent.txt             # Your browser's user agent string
├── downloads/                # Downloaded files will be saved here
└── HOW_TO_USE.md            # This file
```

## Workflow Summary

1. **First time setup:**
   - Run `./create_var.sh` to create config files
   - Export your session data from Chrome (cookies, localStorage, sessionStorage, userAgent)
   - Run `python setup_session.py` to save your session to the Chrome profile

2. **Daily usage:**
   - Just run `python download_dropbox.py` to download files
   - No need to load cookies every time - they're saved in the profile!

3. **When session expires:**
   - Re-export your session data from Chrome
   - Run `python setup_session.py` again to update the saved session

## Troubleshooting

### "unable to set cookie" Errors

- Make sure you're visiting Dropbox in your regular Chrome browser before exporting
- Ensure all three storage files (cookies.txt, localstorage.json, sessionstorage.json) are properly exported
- Run `python setup_session.py` again to reload the session

### Download Button Not Found

- Try using the `--url` flag for URL-based downloads
- Make sure you ran `python setup_session.py` first to set up your session
- Verify you're logged into Dropbox by running `setup_session.py` and checking the browser
- Check that the shared folder URL is correct and accessible

### Session Expires / Not Logged In

- Re-export your session data (cookies, localStorage, sessionStorage, userAgent)
- Run `python setup_session.py` again to update the saved session
- Some security tokens may expire after a few days/weeks

### Chrome Profile Issues

- If you get conflicts with an existing Chrome instance, close all Chrome windows first
- Or change the `--user-data-dir` path in both `setup_session.py` and `download_dropbox.py` to a different location

## Notes

- The script will download files to the `downloads/` directory
- Session is saved in `/tmp/chrome-debug` profile and persists between runs
- You only need to run `setup_session.py` once, or when your session expires
- The script currently downloads the first file in the grid view
- Both scripts use the same Chrome profile, so cookies are shared between them

## Security Warning

⚠️ **Important**: The `cookies.txt`, `localstorage.json`, `sessionstorage.json`, and `useragent.txt` files contain sensitive authentication data. Do NOT share these files or commit them to version control. They are already added to `.dockerignore` for your protection.

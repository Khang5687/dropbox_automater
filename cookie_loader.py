"""Cookie loading utilities for Selenium WebDriver"""

import json


def load_json_cookies(driver, cookie_file):
    """Load cookies from JSON format file into Selenium driver"""
    with open(cookie_file, "r") as f:
        cookies = json.load(f)
    
    for cookie in cookies:
        try:
            # Build cookie dict with required fields
            cookie_dict = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", False),
            }
            
            # Add optional fields if present
            if "expirationDate" in cookie and cookie["expirationDate"]:
                # Convert to int, handling float timestamps
                cookie_dict["expiry"] = int(cookie["expirationDate"])
            
            if "httpOnly" in cookie:
                cookie_dict["httpOnly"] = cookie["httpOnly"]
            
            if "sameSite" in cookie and cookie["sameSite"]:
                # Selenium accepts: 'Strict', 'Lax', or 'None'
                same_site = cookie["sameSite"]
                if same_site == "no_restriction":
                    cookie_dict["sameSite"] = "None"
                elif same_site in ["strict", "lax"]:
                    cookie_dict["sameSite"] = same_site.capitalize()
            
            driver.add_cookie(cookie_dict)
            
        except Exception as e:
            print(f"Error loading cookie '{cookie.get('name', 'unknown')}': {e}")
            continue


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

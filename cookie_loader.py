"""Cookie and storage loading utilities for Selenium WebDriver"""

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
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", False),
            }
            
            # __Host- and __Secure- prefixed cookies have special requirements
            # __Host- cookies must NOT have a domain attribute
            # For other cookies, include domain if not hostOnly
            if cookie["name"].startswith("__Host-"):
                # Do not add domain for __Host- cookies
                pass
            elif cookie.get("hostOnly", False):
                # For hostOnly cookies, don't set domain (let browser infer it)
                pass
            else:
                # Regular cookies can have domain
                cookie_dict["domain"] = cookie["domain"]
            
            # Add optional fields if present
            if "expirationDate" in cookie and cookie["expirationDate"]:
                # Convert to int, handling float timestamps
                cookie_dict["expiry"] = int(cookie["expirationDate"])
            
            if "httpOnly" in cookie:
                cookie_dict["httpOnly"] = cookie["httpOnly"]
            
            # Remove sameSite to avoid compatibility issues
            # Selenium can be picky about sameSite values
            
            driver.add_cookie(cookie_dict)
            
        except Exception as e:
            print(f"Error loading cookie '{cookie.get('name', 'unknown')}': {e}")
            continue


def load_local_storage(driver, storage_file):
    """Load local storage from JSON file into Selenium driver"""
    try:
        with open(storage_file, "r") as f:
            local_storage = json.load(f)
        
        for key, value in local_storage.items():
            # Escape single quotes in key and value to prevent JS injection issues
            safe_key = key.replace("'", "\\'")
            safe_value = str(value).replace("'", "\\'")
            driver.execute_script(f"window.localStorage.setItem('{safe_key}', '{safe_value}');")
        
        print(f"Loaded {len(local_storage)} local storage items")
    except FileNotFoundError:
        print(f"Local storage file not found: {storage_file}")
    except Exception as e:
        print(f"Error loading local storage: {e}")


def load_session_storage(driver, storage_file):
    """Load session storage from JSON file into Selenium driver"""
    try:
        with open(storage_file, "r") as f:
            session_storage = json.load(f)
        
        for key, value in session_storage.items():
            # Escape single quotes in key and value to prevent JS injection issues
            safe_key = key.replace("'", "\\'")
            safe_value = str(value).replace("'", "\\'")
            driver.execute_script(f"window.sessionStorage.setItem('{safe_key}', '{safe_value}');")
        
        print(f"Loaded {len(session_storage)} session storage items")
    except FileNotFoundError:
        print(f"Session storage file not found: {storage_file}")
    except Exception as e:
        print(f"Error loading session storage: {e}")

"""
Helper utilities for Selenium tests
Provides common functions for login, waits, form filling, and file operations
"""
import os
import time
from io import BytesIO
from PIL import Image
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException  # type: ignore
from selenium.webdriver.support.ui import Select  # type: ignore


def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for an element to be present and visible
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"❌ Timeout waiting for element: {by}={value}")
        return None


def wait_for_clickable(driver, by, value, timeout=10):
    """
    Wait for an element to be clickable
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        print(f"❌ Timeout waiting for clickable element: {by}={value}")
        return None


def wait_for_url_contains(driver, url_part, timeout=10):
    """
    Wait for URL to contain specific text
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.url_contains(url_part)
        )
        return True
    except TimeoutException:
        print(f"❌ Timeout waiting for URL to contain: {url_part}")
        return False


def wait_for_text_in_element(driver, by, value, text, timeout=10):
    """
    Wait for specific text to appear in an element
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element((by, value), text)
        )
        return True
    except TimeoutException:
        print(f"❌ Timeout waiting for text '{text}' in element: {by}={value}")
        return False


def safe_click(driver, by, value, timeout=10):
    """
    Safely click an element with retry logic
    """
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            element = wait_for_clickable(driver, by, value, timeout)
            if element:
                element.click()
                return True
        except StaleElementReferenceException:
            if attempt < max_attempts - 1:
                time.sleep(0.5)
                continue
            else:
                print(f"❌ Stale element after {max_attempts} attempts")
                return False
    return False


def fill_form_field(driver, field_name, value, by=By.NAME):
    """
    Fill a form field by name or other locator.
    Supports normal text, textarea, and type="date" fields.
    """
    try:
        field = wait_for_element(driver, by, field_name)
        if field:
            field_type = field.get_attribute("type")
            
            if field_type == "date":
                # For date fields, set value via JS to avoid browser issues
                driver.execute_script("arguments[0].value = arguments[1];", field, value)
            else:
                field.clear()
                field.send_keys(value)
            
            return True
        return False
    except Exception as e:
        print(f"❌ Error filling field {field_name}: {e}")
        return False



def select_dropdown(driver, field_name, value_or_text, by_value=True):
    """
    Select an option from a dropdown
    """
    try:
        dropdown_element = wait_for_element(driver, By.NAME, field_name)
        if dropdown_element:
            select = Select(dropdown_element)
            if by_value:
                select.select_by_value(value_or_text)
            else:
                select.select_by_visible_text(value_or_text)
            return True
        return False
    except Exception as e:
        print(f"❌ Error selecting dropdown {field_name}: {e}")
        return False


def open_signup_modal(driver):
    """
    Open signup modal with multiple fallback methods
    """
    try:
        # Try multiple selectors for signup button
        signup_selectors = [
            "a[onclick*='openSignupModal']",
            "a[onclick*='signup']",
            "button[onclick*='signup']",
            "a[href*='signup']",
            ".signup-btn",
            "#signup-btn",
            "a.btn-primary",
            "button.btn-primary",
            "a:contains('Sign Up')",
            "button:contains('Sign Up')"
        ]
        
        signup_btn = None
        for selector in signup_selectors:
            try:
                signup_btn = wait_for_element(driver, By.CSS_SELECTOR, selector, timeout=2)
                if signup_btn and signup_btn.is_displayed():
                    break
            except:
                continue
        
        # Try by link text as fallback
        if not signup_btn:
            try:
                signup_btn = wait_for_element(driver, By.LINK_TEXT, "Sign Up", timeout=2)
            except:
                pass
        
        if not signup_btn:
            try:
                signup_btn = wait_for_element(driver, By.PARTIAL_LINK_TEXT, "Sign", timeout=2)
            except:
                pass
        
        if signup_btn and signup_btn.is_displayed():
            # Scroll to element
            driver.execute_script("arguments[0].scrollIntoView(true);", signup_btn)
            time.sleep(1)
            signup_btn.click()
            time.sleep(2)
            return True
        
        print("❌ Signup button not found")
        return False
    except Exception as e:
        print(f"❌ Error opening signup modal: {e}")
        return False


def open_login_modal(driver):
    """
    Open login modal with multiple fallback methods
    """
    try:
        # Try multiple selectors for login button
        login_selectors = [
            "a[onclick*='openModal']",
            "a[onclick*='login']",
            "button[onclick*='login']",
            "a[href*='login']",
            ".login-btn",
            "#login-btn",
            "a.btn-primary",
            "button.btn-primary",
            "a:contains('Login')",
            "button:contains('Login')"
        ]
        
        login_btn = None
        for selector in login_selectors:
            try:
                login_btn = wait_for_element(driver, By.CSS_SELECTOR, selector, timeout=2)
                if login_btn and login_btn.is_displayed():
                    break
            except:
                continue
        
        # Try by link text as fallback
        if not login_btn:
            try:
                login_btn = wait_for_element(driver, By.LINK_TEXT, "Login", timeout=2)
            except:
                pass
        
        if login_btn and login_btn.is_displayed():
            # Scroll to element
            driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
            time.sleep(1)
            login_btn.click()
            time.sleep(2)
            return True
        
        print("❌ Login button not found")
        return False
    except Exception as e:
        print(f"❌ Error opening login modal: {e}")
        return False


def login_user(driver, live_server, username, password):
    """
    Login a user through the modal on homepage
    Returns True if successful, False otherwise
    """
    try:
        # Go to homepage
        driver.get(live_server.url)
        time.sleep(3)

        # Open login modal
        if not open_login_modal(driver):
            return False
        
        # Fill credentials
        fill_form_field(driver, "username", username)
        fill_form_field(driver, "password", password)
        
        # Submit form
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(3)
            return True
        
        return False
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False


def logout_user(driver):
    """
    Logout the current user
    """
    try:
        # Try multiple selectors for logout button
        logout_selectors = [
            "a[href*='logout']",
            "a:contains('Logout')",
            "button:contains('Logout')",
            ".logout-btn",
            "#logout-btn",
            "a[onclick*='logout']"
        ]
        
        logout_link = None
        for selector in logout_selectors:
            try:
                logout_link = wait_for_element(driver, By.CSS_SELECTOR, selector, timeout=3)
                if logout_link:
                    break
            except:
                continue
        
        # Try by link text as fallback
        if not logout_link:
            logout_link = wait_for_element(driver, By.LINK_TEXT, "Logout", timeout=3)
        
        if not logout_link:
            logout_link = wait_for_element(driver, By.PARTIAL_LINK_TEXT, "logout", timeout=3)
        
        if logout_link:
            logout_link.click()
            time.sleep(2)
            return True
        return False
    except Exception as e:
        print(f"❌ Logout failed: {e}")
        return False


def create_test_image(filename="test_image.jpg", size=(800, 600), color=(100, 150, 200)):
    """
    Create a test image file and return its path
    """
    try:
        # Create tests/temp directory if it doesn't exist
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        filepath = os.path.join(temp_dir, filename)
        
        # Create image
        img = Image.new('RGB', size, color)
        img.save(filepath, 'JPEG')
        
        return filepath
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
        return None


def create_test_document(filename="test_doc.pdf"):
    """
    Create a simple test PDF document
    """
    try:
        from reportlab.pdfgen import canvas
        
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        filepath = os.path.join(temp_dir, filename)
        
        # Create simple PDF
        c = canvas.Canvas(filepath)
        c.drawString(100, 750, "Test Document")
        c.drawString(100, 730, "This is a test document for NGO registration")
        c.save()
        
        return filepath
    except Exception as e:
        print(f"❌ Error creating test document: {e}")
        # Fallback: create a simple text file
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        filepath = os.path.join(temp_dir, filename.replace('.pdf', '.txt'))
        with open(filepath, 'w') as f:
            f.write("Test Document\nThis is a test document for NGO registration")
        return filepath


def upload_file(driver, field_name, file_path):
    """
    Upload a file to an input field
    """
    try:
        file_input = driver.find_element(By.NAME, field_name)
        file_input.send_keys(os.path.abspath(file_path))
        return True
    except Exception as e:
        print(f"❌ Error uploading file to {field_name}: {e}")
        return False


def take_screenshot(driver, name="screenshot"):
    """
    Take a screenshot for debugging
    """
    try:
        screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        filepath = os.path.join(screenshots_dir, f"{name}_{int(time.time())}.png")
        driver.save_screenshot(filepath)
        print(f"📸 Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        return None


def scroll_to_element(driver, element):
    """
    Scroll to make an element visible
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"❌ Error scrolling to element: {e}")
        return False


def is_element_present(driver, by, value):
    """
    Check if an element is present on the page
    """
    try:
        driver.find_element(by, value)
        return True
    except:
        return False


def get_element_text(driver, by, value):
    """
    Get text from an element
    """
    try:
        element = wait_for_element(driver, by, value)
        if element:
            return element.text
        return None
    except Exception as e:
        print(f"❌ Error getting text from element: {e}")
        return None


def wait_for_page_load(driver, timeout=10):
    """
    Wait for page to fully load
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        return True
    except TimeoutException:
        print("❌ Page load timeout")
        return False


def cleanup_temp_files():
    """
    Clean up temporary test files
    """
    try:
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        return True
    except Exception as e:
        print(f"❌ Error cleaning up temp files: {e}")
        return False


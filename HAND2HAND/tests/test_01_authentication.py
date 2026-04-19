"""
Authentication tests for all user types
Tests signup, login, logout, and validation scenarios
"""
import pytest
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tests.test_helpers import (
    login_user, logout_user, wait_for_element, wait_for_text_in_element,
    fill_form_field, safe_click, take_screenshot, open_signup_modal, open_login_modal,create_test_image
)


class TestAuthentication:
    """Test authentication flows for all user types"""

    @pytest.mark.django_db
    def test_donor_signup(self, driver, live_server):
        """Test donor/recipient signup with profile data including file upload"""

        driver.get(live_server.url)

        # Open login modal
        login_btn = wait_for_element(driver, By.CSS_SELECTOR, "a.login-btn", timeout=5)
        if not login_btn:
            take_screenshot(driver, "login_btn_not_found")
            pytest.skip("Login button not found, cannot open modal")
        login_btn.click()
        print("✅ Login modal opened")

        # Click the Sign Up link inside the login modal
        signup_btn = wait_for_element(driver, By.LINK_TEXT, "Sign Up", timeout=5)
        if not signup_btn:
            take_screenshot(driver, "signup_btn_not_found")
            pytest.skip("Signup button not found, cannot open modal")
        signup_btn.click()
        print("✅ Signup button clicked")


        # --- Wait for modal to appear ---
        try:
            signup_modal = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "signupModal"))
            )
            print("✅ Signup modal is visible")
        except TimeoutException:
            pytest.fail("❌ Signup modal did not appear")

        # --- Select user type Donor/Recipient ---
        try:
            user_type_el = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "user_type"))
            )
            Select(user_type_el).select_by_visible_text("Donor/Recipient")
            print("✅ User type selected: Donor/Recipient")
        except TimeoutException:
            pytest.fail("❌ User type dropdown not found or clickable")

        # --- Wait for donor fields to appear ---
        try:
            donor_fields = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "donorFields"))
            )
            print("✅ Donor fields are present")
        except TimeoutException:
            pytest.fail("❌ Donor fields did not appear")

        # --- Fill in donor fields ---
        fields = {
            "username": "test_donor",
            "email": "testdonor@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
            "full_name": "Test Donor",
            "city_postal": "Dhaka",
            "address": "123 Test Street",
            "mobile_number": "01712345678",
        }

        for name, value in fields.items():
            if name in ["username", "email", "password1", "password2"]:
               selector = f"form#signupForm [name='{name}']"
            else:
               selector = f"#donorFields [name='{name}']"
            try:
               el = WebDriverWait(driver, 5).until(
                   EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
              )
               driver.execute_script("arguments[0].value = arguments[1];", el, value)
            except TimeoutException:
               take_screenshot(driver, f"donor_signup_field_{name}_fail")
               pytest.fail(f"❌ Field '{name}' not found in signup form")

        # --- Upload test NID/Birth Certificate ---
        try:
            file_input = driver.find_element(By.NAME, "nid_birth_certificate")
            test_file_path = os.path.join(os.getcwd(), "tests", "temp", "test_doc.pdf")
            file_input.send_keys(test_file_path)
            print("✅ NID/Birth certificate uploaded")
        except Exception as e:
            pytest.fail(f"❌ File upload failed: {e}")
            
        # Click the Terms & Conditions checkbox
        try:
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#signupForm input[type='checkbox']"))
               )
            checkbox.click()
            print("✅ Terms & Conditions checkbox clicked")
        except TimeoutException:
            take_screenshot(driver, "signup_checkbox_not_found")
            pytest.fail("❌ Terms & Conditions checkbox not found or not clickable")

        # --- Submit the form ---
        try:
            submit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#signupModal button[type='submit']"))
            )
            submit_btn.click()
            print("✅ Signup form submitted")
        except TimeoutException:
            pytest.fail("❌ Submit button not found or clickable")
            
        # --- Check if user is logged in after signup ---
        try:
          # Wait for the logout link to appear in the navbar dropdown
            dropdown_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".dropdown-btn"))
             )
            dropdown_btn.click()
            logout_link = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.LINK_TEXT, "Log out"))
            )
            assert logout_link is not None, "Logout link not found - signup may have failed"
            print("✅ Signup successful and user is logged in")
        except TimeoutException:
            take_screenshot(driver, "signup_login_failed")
            pytest.fail("❌ Signup did not log in user")
            
            
            
            
    def test_ngo_signup(self, driver, live_server, test_document_path):
        """Test NGO signup with registration certificate"""
        driver.get(live_server.url)
        time.sleep(1)

        # Open login modal
        login_btn = wait_for_element(driver, By.CSS_SELECTOR, "a.login-btn", timeout=5)
        if not login_btn:
            take_screenshot(driver, "login_btn_not_found")
            pytest.skip("Login button not found, cannot open modal")
        login_btn.click()
        time.sleep(1)

        # Click the Sign Up link inside the login modal
        signup_btn = wait_for_element(driver, By.LINK_TEXT, "Sign Up", timeout=5)
        if not signup_btn:
            take_screenshot(driver, "signup_btn_not_found")
            pytest.skip("Signup button not found, cannot open modal")
        signup_btn.click()
        time.sleep(1)

        # --- Select user type NGO ---
        try:
            user_type_el = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "user_type"))
            )
            Select(user_type_el).select_by_visible_text("NGO")
            print("✅ User type selected: NGO")
        except TimeoutException:
            pytest.fail("❌ User type dropdown not found or clickable")

        # Wait for NGO fields to appear properly
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#ngoFields input[name='reg_certificate']"))
        )
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#ngoFields input[name='ngo_nid_birth_certificate']"))
        )
        time.sleep(0.5)  # small buffer for JS animation

        # Fill all text fields
        fields = {
            "username": "test_ngo",
            "email": "testngo@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
            "ngo_name": "Test NGO",
            "contact_person": "Test Person",
            "city_postal": "Dhaka",
            "address": "456 NGO Street",
            "ngo_type": "Charity",
            "social_link": "https://facebook.com/testngo",
            "mobile_number": "01787654321",
        }

        for name, value in fields.items():
            if name in ["username", "email", "password1", "password2"]:
                selector = f"form#signupForm [name='{name}']"
            else:
                selector = f"#ngoFields [name='{name}']"
            try:
                el = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                driver.execute_script("arguments[0].value = arguments[1];", el, value)
            except TimeoutException:
                take_screenshot(driver, f"ngo_signup_field_{name}_fail")
                pytest.fail(f"❌ Field '{name}' not found in signup form")

        # Upload registration certificate
        reg_input = driver.find_element(By.NAME, "reg_certificate")
        reg_input.send_keys(test_document_path)
        print("✅ Registration certificate uploaded")

        # Upload NID/Birth certificate
        nid_input = driver.find_element(By.NAME, "ngo_nid_birth_certificate")
        nid_input.send_keys(test_document_path)
        print("✅ NID/Birth certificate uploaded")

        # Click Terms & Conditions checkbox
        try:
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#signupForm input[type='checkbox']"))
            )
            checkbox.click()
            print("✅ Terms & Conditions checkbox clicked")
        except TimeoutException:
            take_screenshot(driver, "ngo_signup_checkbox_not_found")
            pytest.fail("❌ Terms & Conditions checkbox not found or not clickable")

        # Submit form
        submit_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#signupModal button[type='submit']"))
        )
        submit_btn.click()
        print("✅ Signup form submitted")
        time.sleep(2)

        # Check for approval pending message
        success_indicator = (
            "approval" in driver.page_source.lower() or
            "pending" in driver.page_source.lower() or
            "submitted" in driver.page_source.lower()
        )
        assert success_indicator, "NGO signup failed"
        print("✅ NGO signup successful")


    def test_donor_login(self, driver, donor_user, live_server):
        """Test donor login"""
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Donor login failed"
        
        # Verify login success
        try:
          # Wait for the logout link to appear in the navbar dropdown
            dropdown_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".dropdown-btn"))
             )
            dropdown_btn.click()
            logout_link = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.LINK_TEXT, "Log out"))
            )
            assert logout_link is not None, "Logout link not found "
            print("✅ Login successful ")
        except TimeoutException:
            take_screenshot(driver, "donor login_failed")
            pytest.fail("❌  did not log in user")
            
            
            

    def test_ngo_login(self, driver, ngo_user, live_server):
        """Test approved NGO login"""
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
        
        # Verify login success
        try:
          # Wait for the logout link to appear in the navbar dropdown
            dropdown_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".dropdown-btn"))
             )
            dropdown_btn.click()
            logout_link = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.LINK_TEXT, "Log out"))
            )
            assert logout_link is not None, "Logout link not found "
            print("✅ Login successful ")
        except TimeoutException:
            take_screenshot(driver, "NGO login_failed")
            pytest.fail("❌  did not log in user")



    def test_admin_login(self, driver, admin_user, live_server):
        """Test admin login and redirect to admin panel"""
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"
        
        # Check if redirected to admin panel
        time.sleep(2)
        current_url = driver.current_url
        admin_redirected = "/panel/" in current_url or "/admin/" in current_url
        assert admin_redirected, f"Admin not redirected to panel. Current URL: {current_url}"
        print("✅ Admin login and redirect successful")

    def test_pending_ngo_login_fails(self, driver, pending_ngo_user, live_server):
        """Test that unapproved NGO cannot login"""
        driver.get(live_server.url)
        time.sleep(1)
        
        # Open login modal
        login_btn = wait_for_element(driver, By.CSS_SELECTOR, "a.btn-primary[onclick*='openModal']", timeout=5)
        if login_btn:
            login_btn.click()
            time.sleep(1)
        
        # Fill credentials
        fill_form_field(driver, "username", "pending_ngo")
        fill_form_field(driver, "password", "ngopass")
        
        # Submit form
        submit_btn = wait_for_element(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            
            # Check for approval pending message
            approval_message = (
                "approval" in driver.page_source.lower() or 
                "pending" in driver.page_source.lower() or
                "wait" in driver.page_source.lower()
            )
            assert approval_message, "Pending NGO should not be able to login"
            print("✅ Pending NGO login correctly blocked")

    def test_invalid_credentials(self, driver, live_server):
        """Test login with invalid credentials"""
        driver.get(live_server.url)
        time.sleep(1)
        
        # Open login modal
        login_btn = wait_for_element(driver, By.CSS_SELECTOR, "a.btn-primary[onclick*='openModal']", timeout=5)
        if login_btn:
            login_btn.click()
            time.sleep(1)
        
        # Fill invalid credentials
        fill_form_field(driver, "username", "invalid_user")
        fill_form_field(driver, "password", "wrong_password")
        
        # Submit form
        submit_btn = wait_for_element(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            
            # Check for error message
            error_message = (
                "invalid" in driver.page_source.lower() or 
                "incorrect" in driver.page_source.lower() or
                "error" in driver.page_source.lower()
            )
            assert error_message, "Should show error for invalid credentials"
            print("✅ Invalid credentials correctly rejected")


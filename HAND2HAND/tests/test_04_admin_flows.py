"""
Admin flow tests
Tests admin panel access, approval workflows, and management features
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.test_helpers import (
    login_user, fill_form_field, wait_for_clickable, wait_for_element
)


class TestAdminFlows:
    """Refactored admin workflows in 9 mega-functions"""

    def test_admin_dashboard_and_statistics(self, driver, admin_user, live_server):
        """Login and check admin dashboard & statistics pages"""
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"

        # Dashboard
        driver.get(f"{live_server.url}/panel/")
        time.sleep(1)
        assert "/panel/" in driver.current_url, "Admin not redirected to dashboard"
        assert "dashboard" in driver.page_source.lower() or "total" in driver.page_source.lower()
        print("✅ Admin dashboard verified")

        # System statistics
        driver.get(f"{live_server.url}/panel/stats/")
        time.sleep(1)
        assert "statistic" in driver.page_source.lower() or "chart" in driver.page_source.lower()
        print("✅ System statistics verified")

    def test_approve_ngo(self, driver, admin_user, live_server, pending_ngo_user):
        """Test approving an NGO"""
        # Login as admin
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"
        
        # Navigate to NGO approval list
        driver.get(f"{live_server.url}/panel/approval/ngos/")
        time.sleep(1)
        
        # Click approve button
        approve_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "a[href*='approve'], button[onclick*='approve']")
        if not approve_btn:
            approve_btn = wait_for_element(driver, By.LINK_TEXT, "Approve")
        
        if approve_btn:
            approve_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "approved" in driver.page_source.lower()
            )
            assert success_indicator, "NGO approval failed"
            print("✅ NGO approved successfully")

    def test_reject_ngo(self, driver, admin_user, live_server, pending_ngo_user):
        """Test rejecting an NGO"""
        # Login as admin
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"
        
        # Navigate to NGO approval list
        driver.get(f"{live_server.url}/panel/approval/ngos/")
        time.sleep(1)
        
        # Click reject button
        reject_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "a[href*='reject'], button[onclick*='reject']")
        if not reject_btn:
            reject_btn = wait_for_element(driver, By.LINK_TEXT, "Reject")
        
        if reject_btn:
            reject_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "rejected" in driver.page_source.lower()
            )
            assert success_indicator, "NGO rejection failed"
            print("✅ NGO rejected successfully")

    
    def test_approve_campaign(self, driver, admin_user, live_server, sample_campaigns):
        """Test approving a campaign"""
        # Login as admin
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"
        
        # Navigate to campaign approval list
        driver.get(f"{live_server.url}/panel/approval/campaigns/")
        time.sleep(1)
        
        # Click approve button
        approve_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "a[href*='approve'], button[onclick*='approve']")
        if not approve_btn:
            approve_btn = wait_for_element(driver, By.LINK_TEXT, "Approve")
        
        if approve_btn:
            approve_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "approved" in driver.page_source.lower()
            )
            assert success_indicator, "Campaign approval failed"
            print("✅ Campaign approved successfully")

    

    def test_reject_campaign(self, driver, admin_user, live_server, sample_campaigns):
        """Test rejecting a campaign"""
        # Login as admin
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"
    
        # Navigate to campaign approval list
        driver.get(f"{live_server.url}/panel/approval/campaigns/")
        time.sleep(1)
    
        # Click reject button
        reject_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "a[href*='reject'], button[onclick*='reject']")
        if not reject_btn:
            reject_btn = wait_for_element(driver, By.LINK_TEXT, "Reject")
    
        if reject_btn:
            reject_btn.click()
            time.sleep(1)  # Alert load hote wait

            # Handle confirmation alert
            try:
                alert = Alert(driver)
                alert.accept()  # Click OK
                time.sleep(1)   # page response wait
            except:
                print("⚠️ No alert appeared")
        
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "rejected" in driver.page_source.lower()
            )
            assert success_indicator, "Campaign rejection failed"
            print("✅ Campaign rejected successfully")



    def test_approve_donation_request(self, driver, admin_user, live_server, sample_requests):
        """Test approving a donation request"""
        # Login as admin
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"
        
        # Navigate to donation request approval list
        driver.get(f"{live_server.url}/panel/approval/donation-requests/")
        time.sleep(1)
        
        # Click approve button
        approve_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "a[href*='approve'], button[onclick*='approve']")
        if not approve_btn:
            approve_btn = wait_for_element(driver, By.LINK_TEXT, "Approve")
        
        if approve_btn:
            approve_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "approved" in driver.page_source.lower()
            )
            assert success_indicator, "Request approval failed"
            print("✅ Donation request approved successfully")

    def test_reject_donation_request(self, driver, admin_user, live_server, sample_requests):
        """Test rejecting a donation request"""
        # Login as admin
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"
    
        # Navigate to donation request approval list
        driver.get(f"{live_server.url}/panel/approval/donation-requests/")
        time.sleep(1)
    
        # Click reject button
        reject_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "a[href*='reject'], button[onclick*='reject']")
        if not reject_btn:
            reject_btn = wait_for_element(driver, By.LINK_TEXT, "Reject")
    
        if reject_btn:
            reject_btn.click()
            time.sleep(1)  # Alert thakte wait

            # Handle confirmation alert
            try:
                alert = Alert(driver)
                alert.accept()  # Click "OK" on alert
                time.sleep(1)   # Page update wait
            except:
                print("⚠️ No alert appeared")

            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "rejected" in driver.page_source.lower()
            )
            assert success_indicator, "Request rejection failed"
            print("✅ Donation request rejected successfully")


    def test_user_management(self, driver, admin_user, live_server, donor_user2):
        """Manage users: view, delete"""
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"

        driver.get(f"{live_server.url}/panel/users/")
        time.sleep(1)
        assert "user" in driver.page_source.lower()
        print("✅ User management page displayed")

        # Delete a specific user
        rows = driver.find_elements(By.CSS_SELECTOR, "table.data-table tbody tr")
        delete_btn = None
        for row in rows:
            if donor_user2.username in row.text:
                delete_btn = row.find_element(By.CSS_SELECTOR, "a.btn-danger")
                break
        if delete_btn:
            driver.execute_script("arguments[0].scrollIntoView(true);", delete_btn)
            driver.execute_script("window.scrollBy(0, -150);")
            delete_btn.click()
            Alert(driver).accept()
            time.sleep(1)
            rows_after = driver.find_elements(By.CSS_SELECTOR, "table.data-table tbody tr")
            assert all(donor_user2.username not in r.text for r in rows_after)
            print("✅ User deleted successfully")

    def test_campaigns_donations_categories_management(self, driver, admin_user, live_server, sample_campaigns, sample_donations, categories):
        """Manage campaigns, donations, and categories (CRUD for categories)"""
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"

        # Campaigns
        driver.get(f"{live_server.url}/panel/campaigns/")
        time.sleep(1)
        assert "campaign" in driver.page_source.lower()
        print("✅ Campaign management page displayed")

        # Donations
        driver.get(f"{live_server.url}/panel/donations/")
        time.sleep(1)
        assert "donation" in driver.page_source.lower()
        print("✅ Donation management page displayed")

        # Categories CRUD
        driver.get(f"{live_server.url}/panel/categories/")
        time.sleep(1)
        assert "category" in driver.page_source.lower()
        print("✅ Category management page displayed")

        # Create category
        driver.get(f"{live_server.url}/panel/categories/create/")
        time.sleep(1)
        fill_form_field(driver, "name", "Test Category")
        fill_form_field(driver, "description", "This is a test category")
        fill_form_field(driver, "icon", "fa-solid fa-flask")
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            assert "successfully" in driver.page_source.lower() or "created" in driver.page_source.lower()
            print("✅ Category created")

        # Edit first category
        category = categories[0]
        driver.get(f"{live_server.url}/panel/categories/{category.id}/edit/")
        time.sleep(1)
        fill_form_field(driver, "name", "Updated Education Category")
        fill_form_field(driver, "description", "Updated description for education category")
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            assert "successfully" in driver.page_source.lower() or "updated" in driver.page_source.lower()
            print("✅ Category updated")

        # Delete last category
        category = categories[-1]
        driver.get(f"{live_server.url}/panel/categories/{category.id}/delete/")
        time.sleep(1)
        confirm_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if confirm_btn:
            confirm_btn.click()
            time.sleep(1)
            assert "successfully" in driver.page_source.lower() or "deleted" in driver.page_source.lower()
            print("✅ Category deleted")

    def test_admin_profile_and_password(self, driver, admin_user, live_server):
        """Admin profile: view, update info, change password"""
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"

        driver.get(f"{live_server.url}/panel/profile/")
        time.sleep(1)
        assert "profile" in driver.page_source.lower()
        print("✅ Admin profile page displayed")

        # Update profile info
        fill_form_field(driver, "name", "Updated Admin Name")
        fill_form_field(driver, "email", "updatedadmin@example.com")
        update_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if update_btn:
            update_btn.click()
            time.sleep(2)
            assert "successfully" in driver.page_source.lower() or "updated" in driver.page_source.lower()
            print("✅ Admin profile updated")

        # Change password
        fill_form_field(driver, "old_password", "adminpass")
        fill_form_field(driver, "new_password1", "newadminpass123")
        fill_form_field(driver, "new_password2", "newadminpass123")
        password_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if password_btn:
            password_btn.click()
            time.sleep(2)
            assert "successfully" in driver.page_source.lower() or "updated" in driver.page_source.lower()
            print("✅ Admin password changed")

    def test_rewards_claims_reviews_contact(self, driver, admin_user, live_server, rewards):
        """Manage rewards, donation claims, reviews, contact messages"""
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"

        # Rewards
        driver.get(f"{live_server.url}/panel/rewards/")
        time.sleep(1)
        assert "reward" in driver.page_source.lower()
        print("✅ Rewards management displayed")

        # Donation claims
        driver.get(f"{live_server.url}/panel/donation-claims/")
        time.sleep(1)
        assert "claim" in driver.page_source.lower()
        print("✅ Claims management displayed")

        # Reviews
        driver.get(f"{live_server.url}/panel/reviews/")
        time.sleep(1)
        assert "review" in driver.page_source.lower()
        print("✅ Reviews management displayed")

        # Contact messages
        driver.get(f"{live_server.url}/panel/contact-messages/")
        time.sleep(1)
        assert "contact" in driver.page_source.lower() or "message" in driver.page_source.lower()
        print("✅ Contact messages displayed")

    def test_create_admin_user(self, driver, admin_user, live_server):
        """Create a new admin"""
        success = login_user(driver, live_server, "admin1", "adminpass")
        assert success, "Admin login failed"

        driver.get(f"{live_server.url}/panel/admins/create/")
        time.sleep(1)
        fill_form_field(driver, "username", "new_admin")
        fill_form_field(driver, "email", "newadmin@example.com")
        fill_form_field(driver, "password", "adminpass123")
        fill_form_field(driver, "confirm_password", "adminpass123")
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            assert "successfully" in driver.page_source.lower() or "created" in driver.page_source.lower()
            print("✅ New admin created")

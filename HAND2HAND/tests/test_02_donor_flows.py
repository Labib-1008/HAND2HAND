"""
Donor/Recipient flow tests
Tests donation creation, claiming, requests, reviews, and profile management
"""
import pytest
import time
from selenium.webdriver.common.by import By
from tests.test_helpers import (
    login_user, logout_user, wait_for_element, wait_for_clickable,
    fill_form_field, safe_click, upload_file, select_dropdown,
    wait_for_url_contains, wait_for_text_in_element, take_screenshot, wait_for_page_load
)





class TestDonorFlows:
    """Test complete donor/recipient workflows"""

    def test_create_donation_item(self, driver, donor_user, live_server, categories, test_image_path):
        """Test creating a donation item with image and category"""
        # Login as donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"
        
        # Navigate to donate page
        driver.get(f"{live_server.url}/donate/")
        time.sleep(1)
        
        # Fill donation form
        fill_form_field(driver, "title", "Test Donation Item")
        fill_form_field(driver, "description", "This is a test donation item for testing purposes")
        
        # Select category
        select_dropdown(driver, "category", str(categories[0].id), by_value=True)
        
        fill_form_field(driver, "quantity", "5")
        fill_form_field(driver, "location", "Dhaka")
        select_dropdown(driver, "urgency", "medium", by_value=False)
        
        # Upload image
        if test_image_path:
            upload_file(driver, "image", test_image_path)
        
        # Submit form
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            
            # Check for success message or redirect
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "/explore/" in driver.current_url or
                "donation" in driver.page_source.lower()
            )
            assert success_indicator, "Donation creation failed"
            print("✅ Donation item created successfully")

    def test_browse_donations_with_filters(self, driver, donor_user2, live_server, sample_donations):
        """Test browsing donations with category and location filters"""
        # Login as second donor
        success = login_user(driver, live_server, "donor2", "donorpass2")
        assert success, "Login failed"
        
        # Navigate to explore page
        driver.get(f"{live_server.url}/explore/")
        time.sleep(1)
        
        # Check if donations are displayed
        donation_cards = driver.find_elements(By.CSS_SELECTOR, ".donation-card, .card, [class*='donation']")
        assert len(donation_cards) > 0, "No donations found on explore page"
        
        # Test category filter
        category_filter = wait_for_element(driver, By.NAME, "category")
        if category_filter:
            from selenium.webdriver.support.ui import Select
            select = Select(category_filter)
            select.select_by_visible_text("Education")
            
            # Submit filter
            filter_btn = wait_for_element(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            if filter_btn:
                filter_btn.click()
                time.sleep(2)
        
        # Test search
        search_field = wait_for_element(driver, By.NAME, "q")
        if search_field:
            search_field.clear()
            search_field.send_keys("textbook")
            
            search_btn = wait_for_element(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            if search_btn:
                search_btn.click()
                time.sleep(2)
        
        print("✅ Donation browsing and filtering successful")


    def test_claim_donation(self, driver, donor_user2, live_server, sample_donations, db):
        """Test claiming a donation with proper waits and verification"""

        from donations.models import DonationClaim  # Claim model

        # Login as donor2
        assert login_user(driver, live_server, "donor2", "donorpass2"), "Login failed"

        # Pick a donation that donor2 does NOT own and is available
        donation = None
        for d in sample_donations:
          if d.donor != donor_user2 and d.is_available:
            donation = d
            break
        assert donation, "No suitable donation found for claiming test"

        # Navigate to donation detail page
        driver.get(f"{live_server.url}/donation/{donation.id}/")
        wait_for_page_load(driver)

        # Wait for and click the claim button
        claim_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "a.btn-claim")
        assert claim_btn, "Claim button not found on donation detail page"
        claim_btn.click()
        wait_for_page_load(driver)

        # Fill claim form
        fill_form_field(driver, "message", "I need this donation for testing purposes.")
        fill_form_field(driver, "contact_number", "01787654321")

        # Submit claim
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        assert submit_btn, "Submit button not found on claim form"
        submit_btn.click()
        wait_for_page_load(driver)
        # Submit korar por add koro
        driver.save_screenshot("after_submit.png")  # Screenshot save hobe
        print(driver.page_source)  # Dekhbe ki message asche, kon page e jacche


        # Verify claim is created in DB
        claim_exists = DonationClaim.objects.filter(
            donation_item=donation, claimant=donor_user2
        ).exists()
        assert claim_exists, "Donation claim was not created in database"

        print("✅ Donation claim submitted successfully")

    def test_create_request_item(self, driver, donor_user2, live_server, categories, test_image_path):
        """Test creating a request item"""
        # Login as donor
        assert login_user(driver, live_server, "donor2", "donorpass2"), "Login failed"

        # Navigate to request page
        driver.get(f"{live_server.url}/request-item/")
        wait_for_page_load(driver)

        # Fill request form
        fill_form_field(driver, "title", "Need School Supplies")
        fill_form_field(driver, "description", "Urgent need for notebooks, pens, and pencils for underprivileged children")
        select_dropdown(driver, "category", str(categories[0].id), by_value=True)
        fill_form_field(driver, "quantity", "50")
        fill_form_field(driver, "delivery_location", "Dhaka")
        fill_form_field(driver, "contact_number", "01787654321")
        select_dropdown(driver, "urgency", "high", by_value=True)

        # Needed before date
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        fill_form_field(driver, "needed_before", future_date)

        # Upload image (optional)
        if test_image_path:
            assert upload_file(driver, "image", test_image_path), "Image upload failed"

        # Submit form
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        assert submit_btn, "Submit button not found"
        submit_btn.click()
        wait_for_page_load(driver)

        # Debug print page source
        print(driver.page_source)

        # Check success message
        success_indicator = any(
        keyword in driver.page_source.lower() for keyword in ["successfully", "submitted", "approval"]
     )
        assert success_indicator, "Request creation failed"
        print("✅ Request item created successfully")



    def test_view_my_requests(self, driver, donor_user2, live_server, sample_requests):
        """Test viewing own requests"""
        # Login as second donor
        success = login_user(driver, live_server, "donor2", "donorpass2")
        assert success, "Login failed"
        
        # Navigate to my requests page
        driver.get(f"{live_server.url}/my-requests/")
        time.sleep(1)
        
        # Check if requests are displayed
        request_items = driver.find_elements(By.CSS_SELECTOR, ".request-item, .card, [class*='request']")
        assert len(request_items) > 0, "No requests found on my requests page"
        
        # Check for request details
        assert "Need School Supplies" in driver.page_source, "Expected request not found"
        print("✅ My requests page displayed correctly")

    def test_browse_approved_requests(self, driver, donor_user, live_server, sample_requests):
        """Test browsing approved requests from other users"""
        # Login as first donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"
        
        # Navigate to donate to requests page
        driver.get(f"{live_server.url}/donate-to-requests/")
        time.sleep(1)
        
        # Check if approved requests are displayed
        request_cards = driver.find_elements(By.CSS_SELECTOR, ".request-card, .card, [class*='request']")
        assert len(request_cards) > 0, "No approved requests found"
        
        # Check for approved request
        assert "Need School Supplies" in driver.page_source, "Approved request not found"
        print("✅ Approved requests browsing successful")

    def test_donate_to_request(self, driver, donor_user, live_server, sample_requests, test_image_path):
        """Test donating to a specific request"""
        # Login as first donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"
        
        # Navigate to donate to specific request
        request = sample_requests[0]  # Approved request
        driver.get(f"{live_server.url}/donate-request/{request.id}/")
        time.sleep(1)
        
        # Fill donation form
        fill_form_field(driver, "title", "Donated School Supplies")
        fill_form_field(driver, "description", "Notebooks, pens, and pencils for the school")
        fill_form_field(driver, "quantity", "25")
        
        # Upload image
        if test_image_path:
            upload_file(driver, "image", test_image_path)
        
        # Submit form
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "donated" in driver.page_source.lower()
            )
            assert success_indicator, "Donation to request failed"
            print("✅ Donation to request successful")

    def test_view_my_donations(self, driver, donor_user, live_server, sample_donations):
        """Test viewing own donations"""
        # Login as donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"
        
        # Navigate to my donations page
        driver.get(f"{live_server.url}/my-donations/")
        time.sleep(1)
        
        # Check if donations are displayed
        donation_items = driver.find_elements(By.CSS_SELECTOR, ".donation-item, .card, [class*='donation']")
        assert len(donation_items) > 0, "No donations found on my donations page"
        
        # Check for donation details
        assert "Mathematics Textbooks" in driver.page_source, "Expected donation not found"
        print("✅ My donations page displayed correctly")

    def test_full_profile_workflow(self, driver, donor_user, live_server, test_image_path):
        """Test full profile workflow: view, update, upload picture"""
        # Login as donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"

        # Navigate to profile page
        driver.get(f"{live_server.url}/profile/")
        time.sleep(1)

        # --- 1️⃣ View Profile ---
        assert "John Doe" in driver.page_source, "Profile name not found"
        assert "donor1@test.com" in driver.page_source, "Profile email not found"
        assert "Dhaka" in driver.page_source, "Profile location not found"
        print("✅ Profile page displayed correctly")

        # --- 2️⃣ Update Profile ---
        fill_form_field(driver, "full_name", "John Updated Doe")
        fill_form_field(driver, "mobile_number", "01799999999")
        fill_form_field(driver, "address", "Updated Test Street")
        fill_form_field(driver, "city_postal", "Updated Dhaka")

        update_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if update_btn:
            update_btn.click()
            time.sleep(2)

        success_indicator = "successfully" in driver.page_source.lower() or "updated" in driver.page_source.lower()
        assert success_indicator, "Profile update failed"
        print("✅ Profile updated successfully")

        # --- 3️⃣ Upload Profile Picture ---
        if test_image_path:
            upload_success = upload_file(driver, "profile_picture", test_image_path)
            if upload_success:
                upload_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                if upload_btn:
                    upload_btn.click()
                    time.sleep(2)

                success_indicator = "successfully" in driver.page_source.lower() or "uploaded" in driver.page_source.lower()
                assert success_indicator, "Profile picture upload failed"
                print("✅ Profile picture uploaded successfully")


    def test_view_rewards(self, driver, donor_user, live_server, rewards):
        """Test viewing rewards and points"""
        # Login as donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"
        
        # Navigate to rewards page
        driver.get(f"{live_server.url}/my-rewards/")
        time.sleep(1)
        
        # Check if rewards information is displayed
        assert "points" in driver.page_source.lower(), "Points information not found"
        assert "reward" in driver.page_source.lower(), "Reward information not found"
        print("✅ Rewards page displayed correctly")

    

    def test_view_notifications(self, driver, donor_user, live_server):
        """Test viewing notifications page"""
        # Login as donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"
        
        # Navigate to notifications page
        driver.get(f"{live_server.url}/notifications/")
        time.sleep(1)
        
        # Check if notifications page loads
        assert "notification" in driver.page_source.lower(), "Notifications page not loaded"
        print("✅ Notifications page displayed correctly")

    def test_edit_donation(self, driver, donor_user, live_server, sample_donations):
        """Test editing own donation"""
        # Login as donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"
        
        # Navigate to edit donation page
        donation = sample_donations[0]
        driver.get(f"{live_server.url}/donation/{donation.id}/edit/")
        time.sleep(1)
        
        # Update donation details
        fill_form_field(driver, "title", "Updated Mathematics Textbooks")
        fill_form_field(driver, "description", "Updated description for the textbooks")
        
        # Submit update
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "updated" in driver.page_source.lower()
            )
            assert success_indicator, "Donation edit failed"
            print("✅ Donation edited successfully")

    def test_delete_donation(self, driver, donor_user, live_server, sample_donations):
        """Test deleting own donation"""
        # Login as donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Login failed"
        
        # Navigate to delete donation page
        donation = sample_donations[1]  # Use second donation
        driver.get(f"{live_server.url}/donation/{donation.id}/delete/")
        time.sleep(1)
        
        # Confirm deletion
        confirm_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if confirm_btn:
            confirm_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "deleted" in driver.page_source.lower()
            )
            assert success_indicator, "Donation deletion failed"
            print("✅ Donation deleted successfully")

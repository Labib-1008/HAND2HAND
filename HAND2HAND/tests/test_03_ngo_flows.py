"""
NGO flow tests
Tests campaign creation, management, updates, and donation tracking
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait,Select  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.common.exceptions import TimeoutException  # type: ignore
from tests.test_helpers import (
    login_user, logout_user, wait_for_element, wait_for_clickable,
    fill_form_field, safe_click, upload_file, select_dropdown,
    wait_for_url_contains, wait_for_text_in_element, take_screenshot
)


class TestNGOFlows:
    """Test complete NGO workflows"""

    def test_create_campaign(self, driver, ngo_user, live_server, campaign_categories, test_image_path):
        """Test creating a campaign"""
        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
        
        # Navigate to create campaign page
        driver.get(f"{live_server.url}/ngos/create-campaign/")
        time.sleep(1)
        
        # Fill campaign form
        fill_form_field(driver, "title", "Test Emergency Relief Campaign")
        fill_form_field(driver, "description", "This is a test campaign for emergency relief efforts")
        
        # Select category
        select_dropdown(driver, "category", str(campaign_categories[0].id), by_value=True)
        
        fill_form_field(driver, "goal_amount", "50000")
        
        # Set end date
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        fill_form_field(driver, "end_date", future_date)
        
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
                "submitted" in driver.page_source.lower() or
                "approval" in driver.page_source.lower()
            )
            assert success_indicator, "Campaign creation failed"
            print("✅ Campaign created successfully")

    def test_view_my_campaigns(self, driver, ngo_user, live_server, sample_campaigns):
        """Test viewing own campaigns"""
        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
        
        # Navigate to my campaigns page
        driver.get(f"{live_server.url}/ngos/my-campaigns/")
        time.sleep(1)
        
        # Check if campaigns are displayed
        campaign_items = driver.find_elements(By.CSS_SELECTOR, ".campaign-item, .card, [class*='campaign']")
        assert len(campaign_items) > 0, "No campaigns found on my campaigns page"
        
        # Check for campaign details
        assert "Emergency Flood Relief" in driver.page_source, "Expected campaign not found"
        print("✅ My campaigns page displayed correctly")

    def test_edit_campaign(self, driver, ngo_user, live_server, sample_campaigns):
        """Test editing own campaign"""
        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
        
        # Navigate to edit campaign page
        campaign = sample_campaigns[1]  # Pending campaign
        driver.get(f"{live_server.url}/ngos/campaign/{campaign.id}/edit/")
        time.sleep(1)
        
        # Update campaign details
        fill_form_field(driver, "title", "Updated School Building Project")
        fill_form_field(driver, "description", "Updated description for the school building project")
        
        # Submit update
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        if submit_btn:
            submit_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "updated" in driver.page_source.lower() or
                "approval" in driver.page_source.lower()
            )
            assert success_indicator, "Campaign edit failed"
            print("✅ Campaign edited successfully")

    def test_delete_campaign(self, driver, ngo_user, live_server, sample_campaigns):
        """Test deleting own campaign"""

        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"

        campaign = sample_campaigns[1]  # pending campaign
        driver.get(f"{live_server.url}/ngos/my-campaigns/")  # list page

        # Locate and click the delete button
        delete_btn = wait_for_clickable(
            driver,
            By.CSS_SELECTOR,
            f"form[action$='campaign/{campaign.id}/delete/'] button.btn-delete"
      )
        assert delete_btn, "Delete button not found for campaign"
        delete_btn.click()

        # ✅ Handle JavaScript confirm alert properly
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"⚠️ Alert text: {alert.text}")
            alert.accept()
            print("✅ Alert accepted successfully")
        except Exception as e:
            print(f"⚠️ No alert found or already handled: {e}")

     # Wait for redirect to finish
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
      )

        # Verify deletion
        page_source = driver.page_source.lower()
        success_indicator = (
            "successfully" in page_source
            or "deleted" in page_source
            or campaign.title.lower() not in page_source
        )

        assert success_indicator, f"Campaign '{campaign.title}' deletion failed"
        print("✅ Campaign deleted successfully")








    def test_browse_public_campaigns(self, driver, ngo_user, live_server, sample_campaigns):
        """Test browsing public campaigns"""
        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
        
        # Navigate to explore campaigns page
        driver.get(f"{live_server.url}/ngos/explore-campaigns/")
        time.sleep(1)
        
        # Check if campaigns are displayed
        campaign_cards = driver.find_elements(By.CSS_SELECTOR, ".campaign-card, .card, [class*='campaign']")
        assert len(campaign_cards) > 0, "No campaigns found on explore page"
        
        # Check for approved campaign
        assert "Emergency Flood Relief" in driver.page_source, "Approved campaign not found"
        print("✅ Public campaigns browsing successful")

    def test_view_campaign_detail(self, driver, ngo_user, live_server, sample_campaigns):
        """Test viewing campaign detail page"""
        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
    
        # Navigate to campaign detail page
        campaign = sample_campaigns[0]  # Approved campaign
        driver.get(f"{live_server.url}/ngos/campaign/{campaign.id}/")
        time.sleep(1)
    
        # ✅ Check overview
        assert campaign.title in driver.page_source, "Campaign title not found"
        assert campaign.description in driver.page_source, "Campaign description not found"
        print("🟢 Overview tab displayed correctly")

        # ✅ Click Donations tab
        donations_tab = wait_for_clickable(driver, By.XPATH, "//li[contains(@data-tab, 'tab-donations')]")
        donations_tab.click()
        time.sleep(1)
        assert "Donations" in driver.page_source or "No donations yet" in driver.page_source, "Donations tab content missing"
        print("🟢 Donations tab displayed correctly")

        # ✅ Click Updates tab
        updates_tab = wait_for_clickable(driver, By.XPATH, "//li[contains(@data-tab, 'tab-updates')]")
        updates_tab.click()
        time.sleep(1)
        assert "Updates" in driver.page_source or "No updates yet" in driver.page_source, "Updates tab content missing"
        print("🟢 Updates tab displayed correctly")

        print("✅ Campaign detail page with all tabs works correctly")


    def test_add_campaign_update(self, driver, ngo_user, live_server, sample_campaigns):
        """Test adding campaign update"""
        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
        
        # Navigate to campaign detail page
        campaign = sample_campaigns[0]  # Approved campaign
        driver.get(f"{live_server.url}/ngos/campaign/{campaign.id}/")
        time.sleep(1)
        
        # Click the "Updates" tab manually before filling the form
        try:
           updates_tab = wait_for_clickable(driver, By.XPATH, "//li[contains(@data-tab, 'tab-updates')]")
           if updates_tab:
              updates_tab.click()
              time.sleep(1)
        except Exception as e:
              print("⚠️ Could not click updates tab:", e)
        # Add campaign update
        fill_form_field(driver, "title", "Campaign Progress Update")
        fill_form_field(driver, "message", "We have made significant progress in our relief efforts. Thank you for your support!")
        
        # Submit update
        update_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if update_btn:
            update_btn.click()
            time.sleep(2)
            
            # Check for success message
            success_indicator = (
                "successfully" in driver.page_source.lower() or
                "added" in driver.page_source.lower()
            )
            assert success_indicator, "Campaign update failed"
            print("✅ Campaign update added successfully")

    def test_view_donation_history(self, driver, ngo_user, live_server):
        """Test viewing donation history"""
        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
        
        # Navigate to donation history page
        driver.get(f"{live_server.url}/ngos/donation-history/")
        time.sleep(1)
        
        # Check if donation history page loads
        assert "donation" in driver.page_source.lower(), "Donation history page not loaded"
        print("✅ Donation history page displayed correctly")

    def test_donate_to_campaign(self, driver, donor_user, live_server, sample_campaigns):
        """Test donating to a campaign (as donor)"""
        # Login as donor
        success = login_user(driver, live_server, "donor1", "donorpass")
        assert success, "Donor login failed"
    
        # Navigate to campaign detail page
        campaign = sample_campaigns[0]  # Approved campaign
        driver.get(f"{live_server.url}/ngos/campaign/{campaign.id}/")
        time.sleep(1)
    
        # Click Donate Now on campaign detail page
        donate_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'action-buttons')]//a[text()='Donate Now']"))
         )
        assert donate_btn, "Donate Now button not found in campaign detail page"
        donate_btn.click()
        time.sleep(1)
    
        # Fill donation form
        fill_form_field(driver, "amount", "1000")
        fill_form_field(driver, "message", "Hope this helps with your relief efforts!")
        fill_form_field(driver, "payer_name", "John Doe")
    
        # Submit donation (this will redirect to payment gateway)
        submit_btn = wait_for_clickable(driver, By.CSS_SELECTOR, "button[type='submit']")
        assert submit_btn, "Donation form submit button not found"
        submit_btn.click()
        time.sleep(2)
    
        # Check if redirected to payment gateway or success page
        current_url = driver.current_url
        payment_redirected = (
            "sslcommerz" in current_url.lower() or
            "payment" in current_url.lower() or
            "gateway" in current_url.lower() or
            "success" in current_url.lower()
        )
        assert payment_redirected, "Donation form submission failed"
        print("✅ Donation to campaign initiated successfully")


    def test_cannot_donate_to_own_campaign(self, driver, ngo_user, live_server, sample_campaigns):
        """Test that NGO cannot donate to own campaign"""
        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"
        
        # Navigate to own campaign detail page
        campaign = sample_campaigns[0]  # Own campaign
        driver.get(f"{live_server.url}/ngos/campaign/{campaign.id}/")
        time.sleep(1)
        
        # Check that donate button is not present or shows error
        donate_btn = wait_for_element(driver, By.CSS_SELECTOR, "a[href*='donate'], button[onclick*='donate']")
        if donate_btn:
            donate_btn.click()
            time.sleep(1)
            
            # Check for error message
            error_message = (
                "cannot" in driver.page_source.lower() or
                "own" in driver.page_source.lower() or
                "error" in driver.page_source.lower()
            )
            assert error_message, "Should prevent NGO from donating to own campaign"
            print("✅ NGO correctly prevented from donating to own campaign")
        else:
            print("✅ Donate button not available for own campaign")

    

    def test_campaign_filters(self, driver, ngo_user, live_server, approved_campaigns):
        """Test campaign filtering functionality (category + search)"""
    
    

        # Login as NGO
        success = login_user(driver, live_server, "ngo1", "ngopass")
        assert success, "NGO login failed"

        # Navigate to explore campaigns page
        driver.get(f"{live_server.url}/ngos/explore-campaigns/")

        # ===== CATEGORY FILTER =====
        category_filter = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "category"))
        )
    
        # Get Healthcare category id from fixtures
        healthcare_cat = next(c for c in approved_campaigns if c.category.name == "Healthcare").category.id
    
        select = Select(category_filter)
        select.select_by_value(str(healthcare_cat))

        # Wait for JS auto-submit + page reload
        WebDriverWait(driver, 5).until(
            EC.staleness_of(category_filter)
        )
    
        # Check only one Healthcare campaign is displayed
        campaign_cards = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".campaign-card"))
        )
        assert len(campaign_cards) == 1, "More than one campaign shown after category filtering"
        assert "Medical Camp for Rural Areas" in campaign_cards[0].text, "Healthcare campaign not displayed correctly"

        # ===== SEARCH FILTER =====
        search_field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_field.clear()
        search_field.send_keys("flood")
    
        search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        search_btn.click()

        # Wait for search results
        campaign_cards = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".campaign-card"))
        )
        assert len(campaign_cards) == 1, "Search filter did not return correct campaign"
        assert "Emergency Flood Relief" in campaign_cards[0].text, "Search result incorrect"

        print("✅ Campaign filtering and search filters working correctly")



    

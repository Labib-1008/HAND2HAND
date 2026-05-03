"""
test_data.py
Test data fixtures and utilities for generating realistic test data
"""
import os
from PIL import Image
from io import BytesIO
from django.utils import timezone
from datetime import datetime, timedelta


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
    
    
def ensure_temp_dir():
       temp_dir = os.path.join(os.path.dirname(__file__), "temp")
       os.makedirs(temp_dir, exist_ok=True)
       return temp_dir



def get_sample_categories():
    """
    Return sample category data
    """
    return [
        {"name": "Education", "description": "Books, school supplies, educational materials", "icon": "📚"},
        {"name": "Food", "description": "Food items, groceries, meals", "icon": "🍎"},
        {"name": "Clothing", "description": "Clothes, shoes, accessories", "icon": "👕"},
        {"name": "Electronics", "description": "Electronic devices, gadgets", "icon": "📱"},
        {"name": "Medical", "description": "Medical supplies, medicines", "icon": "🏥"},
        {"name": "Furniture", "description": "Furniture, household items", "icon": "🪑"},
        {"name": "Toys", "description": "Toys and games for children", "icon": "🧸"},
        {"name": "Sports", "description": "Sports equipment and gear", "icon": "⚽"},
    ]


def get_sample_campaign_categories():
    """
    Return sample campaign category data
    """
    return [
        {"name": "Emergency Relief", "description": "Emergency and disaster relief campaigns"},
        {"name": "Education", "description": "Educational and scholarship campaigns"},
        {"name": "Healthcare", "description": "Medical and healthcare campaigns"},
        {"name": "Community Development", "description": "Community development projects"},
        {"name": "Environment", "description": "Environmental conservation campaigns"},
        {"name": "Women Empowerment", "description": "Women's rights and empowerment"},
    ]


def get_sample_donation_data():
    """
    Return sample donation item data
    """
    return [
        {
            "title": "Mathematics Textbooks",
            "description": "Grade 10 mathematics textbooks in good condition. Perfect for students preparing for exams.",
            "quantity": 5,
            "location": "Dhaka",
            "urgency": "medium",
            "category": "Education"
        },
        {
            "title": "Rice and Lentils",
            "description": "Fresh rice and lentils for families in need. Good quality food items.",
            "quantity": 10,
            "location": "Chittagong",
            "urgency": "high",
            "category": "Food"
        },
        {
            "title": "Winter Clothes",
            "description": "Warm winter jackets and sweaters. Various sizes available.",
            "quantity": 8,
            "location": "Dhaka",
            "urgency": "low",
            "category": "Clothing"
        },
        {
            "title": "Laptop Computer",
            "description": "Used laptop in working condition. Good for students or small businesses.",
            "quantity": 1,
            "location": "Sylhet",
            "urgency": "medium",
            "category": "Electronics"
        },
        {
            "title": "Medical Supplies",
            "description": "First aid supplies and basic medical equipment.",
            "quantity": 3,
            "location": "Rajshahi",
            "urgency": "high",
            "category": "Medical"
        }
    ]


def get_sample_request_data():
    """
    Return sample request item data
    """
    return [
        {
            "title": "Need School Supplies",
            "description": "Urgent need for notebooks, pens, pencils, and other school supplies for underprivileged children in rural areas.",
            "quantity": 50,
            "delivery_location": "Dhaka",
            "urgency": "high",
            "category": "Education",
            "needed_before": (timezone.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")
        },
        {
            "title": "Medical Equipment Needed",
            "description": "Need medical equipment for rural clinic. Looking for stethoscopes, blood pressure monitors, and basic diagnostic tools.",
            "quantity": 5,
            "delivery_location": "Chittagong",
            "urgency": "medium",
            "category": "Medical",
            "needed_before": (timezone.now().date() + timedelta(days=60)).strftime("%Y-%m-%d")
        },
        {
            "title": "Food for Orphanage",
            "description": "Monthly food supplies needed for orphanage. Rice, lentils, vegetables, and cooking oil.",
            "quantity": 100,
            "delivery_location": "Sylhet",
            "urgency": "high",
            "category": "Food",
            "needed_before": (timezone.now().date() + timedelta(days=15)).strftime("%Y-%m-%d")
        }
    ]


def get_sample_campaign_data():
    """
    Return sample campaign data
    """
    return [
        {
            "title": "Emergency Flood Relief",
            "description": "Help flood victims with food, shelter, and medical supplies. Your donation will directly help affected families.",
            "goal_amount": 50000.00,
            "category": "Emergency Relief",
            "end_date": (timezone.now().date() + timedelta(days=90)).strftime("%Y-%m-%d")
        },
        {
            "title": "School Building Project",
            "description": "Build a new school in rural area to provide quality education to underprivileged children.",
            "goal_amount": 100000.00,
            "category": "Education",
            "end_date": (timezone.now().date() + timedelta(days=180)).strftime("%Y-%m-%d")
        },
        {
            "title": "Medical Camp for Rural Areas",
            "description": "Organize free medical camps in rural areas with doctors, medicines, and basic health checkups.",
            "goal_amount": 75000.00,
            "category": "Healthcare",
            "end_date": (timezone.now().date() + timedelta(days=120)).strftime("%Y-%m-%d")
        }
    ]


def get_sample_user_data():
    """
    Return sample user data for testing
    """
    return {
        "donors": [
            {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "testpass123",
                "full_name": "John Doe",
                "city_postal": "Dhaka",
                "address": "123 Main Street, Dhaka",
                "mobile_number": "01712345678"
            },
            {
                "username": "jane_smith",
                "email": "jane@example.com",
                "password": "testpass123",
                "full_name": "Jane Smith",
                "city_postal": "Chittagong",
                "address": "456 Park Avenue, Chittagong",
                "mobile_number": "01787654321"
            }
        ],
        "ngos": [
            {
                "username": "hope_foundation",
                "email": "info@hopefoundation.org",
                "password": "ngopass123",
                "ngo_name": "Hope Foundation",
                "contact_person": "Dr. Sarah Wilson",
                "city_postal": "Dhaka",
                "address": "789 NGO Street, Dhaka",
                "ngo_type": "Charity",
                "social_link": "https://facebook.com/hopefoundation",
                "mobile_number": "01711111111"
            },
            {
                "username": "education_for_all",
                "email": "contact@educationforall.org",
                "password": "ngopass123",
                "ngo_name": "Education for All",
                "contact_person": "Mr. Ahmed Hassan",
                "city_postal": "Sylhet",
                "address": "321 Education Road, Sylhet",
                "ngo_type": "Educational",
                "social_link": "https://twitter.com/educationforall",
                "mobile_number": "01722222222"
            }
        ],
        "admins": [
            {
                "username": "admin_user",
                "email": "admin@donationapp.com",
                "password": "adminpass123"
            }
        ]
    }


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
    



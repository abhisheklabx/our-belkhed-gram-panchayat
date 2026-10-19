import os
import sys
import unittest
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models.database import db
from models.models import User, Household, Complaint, Announcement
from werkzeug.security import check_password_hash

class BelkhedPortalTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()

    def test_01_homepage_loads(self):
        """Test 1: Homepage loads successfully with branding and coordinates"""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('आपले बेलखेड', res.get_data(as_text=True))
        self.assertIn('19.616556', res.get_data(as_text=True))
        self.assertIn('77.636556', res.get_data(as_text=True))

    def test_02_village_info_displays(self):
        """Test 2: Village Information profile displays 2011 Census figures"""
        res = self.client.get('/village')
        self.assertEqual(res.status_code, 200)
        content = res.get_data(as_text=True)
        self.assertIn('745.31', content)
        self.assertIn('445206', content)
        self.assertIn('२,२६२', content)  # 2011 Census population
        self.assertIn('85.10%', content)  # Literacy rate

    def test_03_language_selector_switches(self):
        """Test 3: Language selector changes interface text"""
        # Switch to English
        res_en = self.client.get('/?lang=en')
        self.assertEqual(res_en.status_code, 200)
        self.assertIn('Our Belkhed', res_en.get_data(as_text=True))

        # Switch to Hindi
        res_hi = self.client.get('/?lang=hi')
        self.assertEqual(res_hi.status_code, 200)
        self.assertIn('डिजिटल ग्राम पंचायत', res_hi.get_data(as_text=True))

    def test_04_user_registration_and_privacy_notice(self):
        """Test 4: Registration page shows privacy notice and creates user"""
        # Explicitly request in Marathi
        res_get = self.client.get('/register?lang=mr')
        self.assertIn('आम्ही नागरिकांची कोणतीही संवेदनशील खाजगी माहिती गोळा करत नाही', res_get.get_data(as_text=True))

        # Register a test citizen
        test_email = 'test_citizen_99@belkhed.gov.in'
        with self.app.app_context():
            User.query.filter_by(email_or_phone=test_email).delete()
            db.session.commit()

        res_post = self.client.post('/register', data={
            'name': 'Test Citizen User',
            'email_or_phone': test_email,
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123',
            'preferred_language': 'mr',
            'village_connection': 'resident'
        }, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)

        # Check DB
        with self.app.app_context():
            u = User.query.filter_by(email_or_phone=test_email).first()
            self.assertIsNotNone(u)
            # Test 5: Passwords stored as hashes
            self.assertNotEqual(u.password_hash, 'SecurePassword@123')
            self.assertTrue(check_password_hash(u.password_hash, 'SecurePassword@123'))

    def test_06_login_and_logout(self):
        """Test 6: Login and logout work"""
        res_login = self.client.post('/login', data={
            'email_or_phone': 'abhishek@belkhed.gov.in',
            'password': 'Pass@123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn('Abhishek', res_login.get_data(as_text=True))

        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)

    def test_07_admin_routes_reject_unauthorized(self):
        """Test 7: Admin routes reject unauthorized public users"""
        # Logged out client
        self.client.get('/logout')
        res = self.client.get('/admin/', follow_redirects=False)
        # Should redirect to login
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers['Location'])

    def test_08_household_search_matches_full_name(self):
        """Test 9: Household search matches full name 'Ramesh Kisan Thakare'"""
        res = self.client.get('/api/households/search?q=Ramesh+Kisan+Thakare')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data(as_text=True))
        self.assertGreaterEqual(data['count'], 1)
        found = any('Ramesh' in h['full_name'] for h in data['results'])
        self.assertTrue(found)

    def test_09_household_search_matches_surname_and_multiple_results(self):
        """Test 10 & 11: Household search matches surname and returns multiple results"""
        res = self.client.get('/api/households/search?q=Thakare')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data(as_text=True))
        # Multiple Thakare families in demo data
        self.assertGreaterEqual(data['count'], 2)

    def test_10_unapproved_listings_never_exposed(self):
        """Test 12: Unapproved / Private household listings are not publicly exposed"""
        res = self.client.get('/api/households/search?q=Vilas+Patil')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data(as_text=True))
        # BLK-99 Vilas Patil has public_visibility=False and listing_consent=False
        self.assertEqual(data['count'], 0)

    def test_11_sample_household_coordinates(self):
        """Test 13: Sample household coordinates 19.6164779, 77.6374039 returned in maps URL"""
        res = self.client.get('/api/households/search?q=BLK-01')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data(as_text=True))
        self.assertEqual(data['count'], 1)
        item = data['results'][0]
        self.assertAlmostEqual(item['latitude'], 19.6164779, places=4)
        self.assertAlmostEqual(item['longitude'], 77.6374039, places=4)
        self.assertIn('19.6164779', item['maps_url'])
        self.assertIn('77.6374039', item['maps_url'])

    def test_12_complaint_creation_and_tracking(self):
        """Test 14: Complaint creation and status tracking"""
        res_post = self.client.post('/complaints/new', data={
            'reporter_name': 'Anil Shinde',
            'reporter_contact': '9876599999',
            'category': 'water',
            'description': 'Water leak test complaint',
            'location_address': 'Belkhed Chowk'
        }, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertIn('BLK-CMP-2026', res_post.get_data(as_text=True))

    def test_13_ai_assistant_prototype_fallback(self):
        """Test 16: Gemini fallback works without an API key"""
        res = self.client.post('/api/assistant/chat', json={
            'message': 'गावातील घर कसे शोधायचे?',
            'lang': 'mr'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data(as_text=True))
        self.assertTrue(data['success'])
        self.assertIn('घर', data['response'])

    def test_14_footer_credits_present(self):
        """Test: Footer has mandatory copyright and Made by Abhishek Thakare"""
        res = self.client.get('/')
        content = res.get_data(as_text=True)
        self.assertIn('© All Rights Reserved Grampanchayat Belkhed', content)
        self.assertIn('Made by Abhishek Thakare', content)

if __name__ == '__main__':
    unittest.main()

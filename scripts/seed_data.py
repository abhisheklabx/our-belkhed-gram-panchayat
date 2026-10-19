import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models.database import db
from models.models import (
    User, Household, HouseholdMembershipCode,
    Complaint, ComplaintUpdate, Announcement,
    DevelopmentProject, ProjectUpdate, ResidentVerificationRequest,
    VillageSetting
)
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    with app.app_context():
        print("Ensuring tables are created in database...")
        db.create_all()

        # 1. Admin User
        admin_email = app.config.get('ADMIN_EMAIL', 'abhishek@belkhed.gov.in')
        admin_user = User.query.filter_by(email_or_phone=admin_email).first()
        if not admin_user:
            admin_user = User(
                name=app.config.get('ADMIN_NAME', 'Abhishek Thakare'),
                email_or_phone=admin_email,
                role='admin',
                preferred_language='mr',
                account_status='active',
                village_connection='resident'
            )
            admin_user.set_password(app.config.get('ADMIN_PASSWORD', 'Pass@123'))
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user created: {admin_email} / {app.config.get('ADMIN_PASSWORD')}")
        else:
            print(f"Admin user already exists: {admin_email}")

        # 2. Sample Resident User
        resident_user = User.query.filter_by(email_or_phone='resident@belkhed.gov.in').first()
        if not resident_user:
            resident_user = User(
                name='Ramesh Kisan Thakare',
                email_or_phone='resident@belkhed.gov.in',
                role='resident',
                preferred_language='mr',
                account_status='active',
                village_connection='resident'
            )
            resident_user.set_password('Resident@123')
            db.session.add(resident_user)
            db.session.commit()

        # 3. Households
        if Household.query.count() == 0:
            households = [
                # Mandatory prompt test household
                Household(
                    first_name='Ramesh',
                    middle_name='Kisan',
                    last_name='Thakare',
                    full_name='Ramesh Kisan Thakare',
                    house_number='BLK-01',
                    locality='Gaothan, Gram Panchayat Ward 1',
                    landmark='Opposite Shri Hanuman Mandir',
                    latitude=19.6164779,
                    longitude=77.6374039,
                    image_path='/static/images/house_placeholder.jpg',
                    listing_consent=True,
                    public_visibility=True,
                    verification_status='verified'
                ),
                Household(
                    first_name='Suresh',
                    middle_name='Devidas',
                    last_name='Thakare',
                    full_name='Suresh Devidas Thakare',
                    house_number='BLK-02',
                    locality='Shankar Nagar Galli',
                    landmark='Near Vitthal Mandir',
                    latitude=19.617120,
                    longitude=77.636890,
                    image_path='/static/images/house_placeholder.jpg',
                    listing_consent=True,
                    public_visibility=True,
                    verification_status='verified'
                ),
                Household(
                    first_name='Sunita',
                    middle_name='Ramesh',
                    last_name='Thakare',
                    full_name='Sunita Ramesh Thakare',
                    house_number='BLK-03',
                    locality='Mandir Road',
                    landmark='Near Hanuman Chowk',
                    latitude=19.616900,
                    longitude=77.637800,
                    image_path='/static/images/house_placeholder.jpg',
                    listing_consent=True,
                    public_visibility=True,
                    verification_status='verified'
                ),
                Household(
                    first_name='Ganesh',
                    middle_name='Vitthalrao',
                    last_name='Jadhav',
                    full_name='Ganesh Vitthalrao Jadhav',
                    house_number='BLK-04',
                    locality='Shala Parisar',
                    landmark='Behind Z.P. Primary School',
                    latitude=19.615850,
                    longitude=77.635920,
                    image_path='/static/images/house_placeholder.jpg',
                    listing_consent=True,
                    public_visibility=True,
                    verification_status='verified'
                ),
                Household(
                    first_name='Pravin',
                    middle_name='Babarao',
                    last_name='Deshmukh',
                    full_name='Pravin Babarao Deshmukh',
                    house_number='BLK-05',
                    locality='Pani Taki Galli',
                    landmark='Near Overhead Water Reservoir',
                    latitude=19.617400,
                    longitude=77.637150,
                    image_path='/static/images/house_placeholder.jpg',
                    listing_consent=True,
                    public_visibility=True,
                    verification_status='verified'
                ),
                Household(
                    first_name='Ananda',
                    middle_name='Maroti',
                    last_name='Shinde',
                    full_name='Ananda Maroti Shinde',
                    house_number='BLK-06',
                    locality='Arogya Kendra Road',
                    landmark='Near Health Sub-Centre',
                    latitude=19.615100,
                    longitude=77.635300,
                    image_path='/static/images/house_placeholder.jpg',
                    listing_consent=True,
                    public_visibility=True,
                    verification_status='verified'
                ),
                # Private household (Must NOT appear in public searches)
                Household(
                    first_name='Vilas',
                    middle_name='Pandurang',
                    last_name='Patil',
                    full_name='Vilas Pandurang Patil',
                    house_number='BLK-99',
                    locality='Private Lane',
                    landmark='South Farm Road',
                    latitude=19.614500,
                    longitude=77.634200,
                    image_path='/static/images/house_placeholder.jpg',
                    listing_consent=False,
                    public_visibility=False,
                    verification_status='unverified'
                )
            ]
            db.session.add_all(households)
            db.session.commit()
            print("Seeded 7 sample households.")

            # Generate sample verification codes
            h1 = Household.query.filter_by(house_number='BLK-01').first()
            if h1:
                code1 = HouseholdMembershipCode(
                    household_id=h1.id,
                    code_hash=generate_password_hash('BLK-8491'),
                    code_display='BLK-8491',
                    is_used=False
                )
                db.session.add(code1)
                db.session.commit()

        # 4. Sample Complaints
        if Complaint.query.count() == 0:
            c1 = Complaint(
                complaint_number='BLK-CMP-2026-001',
                reporter_name='Ramesh Kisan Thakare',
                reporter_contact='9876543210',
                category='water',
                description='सार्वजनिक नळ योजनेची मुख्य पाईपलाईन हनुमान मंदिरासमोरील चौकात गळती होत असून पाणी वाया जात आहे.',
                latitude=19.616600,
                longitude=77.637200,
                location_address='Hanuman Mandir Chowk, Belkhed',
                status='in_progress',
                assigned_staff='Gram Sevak Belkhed'
            )
            c2 = Complaint(
                complaint_number='BLK-CMP-2026-002',
                reporter_name='Ganesh Vitthalrao Jadhav',
                reporter_contact='9876500002',
                category='electricity',
                description='जि. प. प्राथमिक शाळेजवळील स्ट्रीटलाईट खांब क्रमांक १२ चा दिवा मागील ३ दिवसांपासून बंद आहे.',
                latitude=19.615800,
                longitude=77.635800,
                location_address='Near ZP Primary School, Belkhed',
                status='resolved',
                assigned_staff='Electrical Contractor',
                resolution_details='नवीन एलईडी दिवा बसवून स्ट्रीटलाईट दुरुस्त करण्यात आला.'
            )
            c3 = Complaint(
                complaint_number='BLK-CMP-2026-003',
                reporter_name='Pravin Deshmukh',
                reporter_contact='9876500003',
                category='drainage',
                description='गावठाण मुख्य रस्त्यावरील सांडपाणी गटार कचऱ्यामुळे तुंबले असून दुर्गंधी पसरत आहे.',
                latitude=19.617300,
                longitude=77.637000,
                location_address='Main Gaothan Road, Belkhed',
                status='submitted'
            )
            db.session.add_all([c1, c2, c3])
            db.session.commit()

            # Add updates
            up1 = ComplaintUpdate(
                complaint_id=c1.id,
                update_type='public',
                message='ग्रामपंचायत पाणीपुरवठा कर्मचाऱ्यास प्रत्यक्ष स्थळ पाहणीसाठी पाठविण्यात आले आहे.'
            )
            up2 = ComplaintUpdate(
                complaint_id=c2.id,
                update_type='public',
                message='तक्रार यशस्वीरित्या निवारण करण्यात आली आहे. प्रकाश पूर्ववत सुरू झाला.'
            )
            db.session.add_all([up1, up2])
            db.session.commit()
            print("Seeded sample complaints and updates.")

        # 5. Announcements
        if Announcement.query.count() == 0:
            ann1 = Announcement(
                title='विशेष ग्रामसभा बैठक सूचना - विकास आराखडा व पाणी व्यवस्थापन',
                content='बेलखेड गावातील सर्व नागरिक, महिला व ज्येष्ठांना कळविण्यात येते की, ग्रामपंचायत सभागृहात चालू आर्थिक वर्षाच्या विकास कामांचे नियोजन व जल जीवन मिशन आढाव्यासाठी विशेष ग्रामसभेचे आयोजन करण्यात आले आहे. सर्वांनी वेळेवर उपस्थित राहावे.',
                language='mr',
                publication_status='published',
                is_important=True
            )
            ann2 = Announcement(
                title='सार्वजनिक आरोग्य तपासणी व लसीकरण शिबीर',
                content='प्राथमिक आरोग्य उपकेंद्र बेलखेड येथे गरोदर माता व लहान मुलांसाठी मोफत आरोग्य तपासणी व पोषण आहार मार्गदर्शन शिबीर आयोजित करण्यात आले आहे. सर्व लाभार्थ्यांनी लाभ घ्यावा.',
                language='mr',
                publication_status='published',
                is_important=False
            )
            ann3 = Announcement(
                title='PM Kisan & Namo Shetkari Yojana e-KYC Reminder',
                content='All eligible farmers of Belkhed village are requested to complete their Aadhaar biometric e-KYC at the nearest CSC center or Gram Panchayat desk to receive upcoming installments without delay.',
                language='en',
                publication_status='published',
                is_important=True
            )
            db.session.add_all([ann1, ann2, ann3])
            db.session.commit()
            print("Seeded sample announcements.")

        # 6. Development Projects
        if DevelopmentProject.query.count() == 0:
            p1 = DevelopmentProject(
                title='गावांतर्गत मुख्य रस्ता सिमेंट काँक्रीटीकरण व बंदिस्त गटार बांधकाम',
                description='उमरखेड मुख्य रस्त्यापासून ग्रामपंचायत कार्यालय ते मारुती मंदिरापर्यंत दर्जेदार सिमेंट रस्ता व सांडपाणी निचऱ्यासाठी बंदिस्त गटार योजना.',
                approved_budget='₹ 18,50,000',
                start_date='15 Jan 2026',
                expected_completion='30 Jun 2026',
                status='ongoing',
                latitude=19.616600,
                longitude=77.636900
            )
            p2 = DevelopmentProject(
                title='पर्यावरणपूरक सौर ऊर्जा पथदिवे (Solar Streetlights) टप्पा १',
                description='गावातील प्रमुख चौकांमध्ये व शाळा परिसरात २५ नवीन उच्च क्षमतेचे सौरऊर्जा पथदिवे बसवून अखंडित प्रकाश व्यवस्था.',
                approved_budget='₹ 4,80,000',
                start_date='01 Oct 2025',
                actual_completion='10 Dec 2025',
                status='completed',
                latitude=19.616800,
                longitude=77.637200
            )
            p3 = DevelopmentProject(
                title='प्राथमिक आरोग्य उपकेंद्र व अंगणवाडी इमारत दुरुस्ती व रंगरंगोटी',
                description='ग्रामस्थांच्या आरोग्य व बालसंगोपनासाठी उपकेंद्राचे नूतनीकरण आणि पिण्याच्या पाण्याची फिल्टर सुविधा.',
                approved_budget='₹ 6,25,000',
                start_date='10 Feb 2026',
                expected_completion='15 May 2026',
                status='ongoing',
                latitude=19.615200,
                longitude=77.635500
            )
            db.session.add_all([p1, p2, p3])
            db.session.commit()
            print("Seeded sample development projects.")

        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()

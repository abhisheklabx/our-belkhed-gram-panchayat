from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email_or_phone = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default='visitor')  # visitor, resident, staff, admin
    preferred_language = db.Column(db.String(10), default='mr')  # mr, hi, en
    account_status = db.Column(db.String(20), default='active')  # active, pending, suspended
    village_connection = db.Column(db.String(100), nullable=True)  # resident, native_away, visitor, relative
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    complaints = db.relationship('Complaint', backref='user', lazy=True, foreign_keys='Complaint.user_id')
    verification_requests = db.relationship('ResidentVerificationRequest', backref='user', lazy=True, foreign_keys='ResidentVerificationRequest.user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email_or_phone': self.email_or_phone,
            'role': self.role,
            'preferred_language': self.preferred_language,
            'account_status': self.account_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class Household(db.Model):
    __tablename__ = 'households'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=True, index=True)
    middle_name = db.Column(db.String(100), nullable=True, index=True)
    last_name = db.Column(db.String(100), nullable=True, index=True)
    full_name = db.Column(db.String(250), nullable=False, index=True)
    house_number = db.Column(db.String(50), nullable=False, index=True)
    locality = db.Column(db.String(150), nullable=True)
    landmark = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Numeric(11, 7), nullable=False)
    longitude = db.Column(db.Numeric(11, 7), nullable=False)
    image_path = db.Column(db.String(300), nullable=True)
    listing_consent = db.Column(db.Boolean, default=True)
    public_visibility = db.Column(db.Boolean, default=True)
    verification_status = db.Column(db.String(30), default='verified')  # verified, pending, unverified
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    membership_codes = db.relationship('HouseholdMembershipCode', backref='household', lazy=True, cascade='all, delete-orphan')
    verification_requests = db.relationship('ResidentVerificationRequest', backref='household', lazy=True)

    def to_public_dict(self):
        lat = float(self.latitude) if self.latitude is not None else 0.0
        lng = float(self.longitude) if self.longitude is not None else 0.0
        return {
            'id': self.id,
            'full_name': self.full_name,
            'house_number': self.house_number,
            'locality': self.locality or '',
            'landmark': self.landmark or '',
            'latitude': lat,
            'longitude': lng,
            'image_path': self.image_path or '/static/images/house_placeholder.jpg',
            'maps_url': f"https://www.google.com/maps/search/?api=1&query={lat},{lng}",
            'directions_url': f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
        }


class HouseholdMembershipCode(db.Model):
    __tablename__ = 'household_membership_codes'

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    code_display = db.Column(db.String(20), nullable=True)  # e.g. BLK-8491
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ResidentVerificationRequest(db.Model):
    __tablename__ = 'resident_verification_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=True)
    verification_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    verification_code_entered = db.Column(db.String(50), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    complaint_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reporter_name = db.Column(db.String(150), nullable=False)
    reporter_contact = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # water, road, electricity, drainage, sanitation, infrastructure, other
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(300), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='submitted')  # submitted, in_progress, resolved, rejected
    assigned_staff = db.Column(db.String(150), nullable=True)
    resolution_details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    updates = db.relationship('ComplaintUpdate', backref='complaint', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'complaint_number': self.complaint_number,
            'reporter_name': self.reporter_name,
            'category': self.category,
            'description': self.description,
            'status': self.status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_address': self.location_address,
            'image_path': self.image_path,
            'created_at': self.created_at.strftime('%d %b %Y, %I:%M %p') if self.created_at else '',
            'resolution_details': self.resolution_details
        }


class ComplaintUpdate(db.Model):
    __tablename__ = 'complaint_updates'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    update_type = db.Column(db.String(30), default='public')  # public, internal
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='mr')  # mr, hi, en, all
    publication_status = db.Column(db.String(20), default='published')  # published, draft, archived
    is_important = db.Column(db.Boolean, default=False)
    published_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DevelopmentProject(db.Model):
    __tablename__ = 'development_projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    approved_budget = db.Column(db.String(100), nullable=True)  # e.g. "₹12,50,000"
    start_date = db.Column(db.String(50), nullable=True)
    expected_completion = db.Column(db.String(50), nullable=True)
    actual_completion = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default='ongoing')  # planned, ongoing, completed
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    image_path = db.Column(db.String(300), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updates = db.relationship('ProjectUpdate', backref='project', lazy=True, cascade='all, delete-orphan')


class ProjectUpdate(db.Model):
    __tablename__ = 'project_updates'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('development_projects.id'), nullable=False)
    progress_description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(300), nullable=True)
    public_visibility = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VillageSetting(db.Model):
    __tablename__ = 'village_settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

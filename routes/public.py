import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g, session
from werkzeug.utils import secure_filename
from models.database import db
from models.models import (
    Household, Complaint, ComplaintUpdate, Announcement,
    DevelopmentProject, VillageSetting
)

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    latest_notices = Announcement.query.filter_by(publication_status='published').order_by(Announcement.published_date.desc()).limit(4).all()
    projects = DevelopmentProject.query.order_by(DevelopmentProject.id.desc()).limit(3).all()
    sample_households = Household.query.filter_by(public_visibility=True, listing_consent=True).limit(4).all()

    # Village stats
    stats = {
        'population': '2,262',
        'households': '488',
        'literacy': '85.10%',
        'area': '745.31 Ha',
        'taluka': 'Umarkhed (9 km)',
        'district': 'Yavatmal (120 km)'
    }
    return render_template('index.html', notices=latest_notices, projects=projects, households=sample_households, stats=stats)


@public_bp.route('/village')
def village_info():
    return render_template('village_info.html')


@public_bp.route('/find-home')
def find_home():
    query = request.args.get('q', '').strip()
    return render_template('find_home.html', initial_query=query)


@public_bp.route('/gis-map')
def gis_map():
    return render_template('gis_map.html')


@public_bp.route('/services')
def services():
    return render_template('services.html')


@public_bp.route('/complaints/new', methods=['GET', 'POST'])
def complaint_new():
    if request.method == 'POST':
        name = request.form.get('reporter_name', '').strip()
        contact = request.form.get('reporter_contact', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        location_address = request.form.get('location_address', '').strip()
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')

        if not name or not contact or not description or not category:
            flash("कृपया सर्व आवश्यक माहिती भरा. (Please fill all required fields)", "danger")
            return redirect(url_for('public.complaint_new'))

        # Generate unique complaint number BLK-CMP-YYYY-XXXX
        complaint_count = Complaint.query.count() + 1
        complaint_number = f"BLK-CMP-2026-{complaint_count:04d}"

        # Image upload handling
        image_path = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                fname = secure_filename(file.filename)
                ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    saved_name = f"cmp_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{fname}"
                    dest = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_name)
                    file.save(dest)
                    image_path = f"/static/uploads/{saved_name}"

        complaint = Complaint(
            complaint_number=complaint_number,
            user_id=g.user.id if g.user else None,
            reporter_name=name,
            reporter_contact=contact,
            category=category,
            description=description,
            location_address=location_address,
            latitude=float(lat) if lat and lat.strip() else None,
            longitude=float(lng) if lng and lng.strip() else None,
            image_path=image_path,
            status='submitted'
        )
        db.session.add(complaint)
        db.session.commit()

        # Add initial audit update
        init_up = ComplaintUpdate(
            complaint_id=complaint.id,
            update_type='public',
            message='तक्रार डिजिटल प्रणालीवर यशस्वीरित्या नोंदवली गेली आहे.'
        )
        db.session.add(init_up)
        db.session.commit()

        flash(f"तक्रार यशस्वीरित्या नोंदवली गेली! आपला तक्रार क्रमांक आहे: {complaint_number}", "success")
        return redirect(url_for('public.complaint_track', cid=complaint_number))

    return render_template('complaint_new.html')


@public_bp.route('/complaints/track')
def complaint_track():
    cid = request.args.get('cid', '').strip()
    complaint = None
    if cid:
        complaint = Complaint.query.filter_by(complaint_number=cid).first()
    return render_template('complaint_track.html', complaint=complaint, cid=cid)


@public_bp.route('/schemes')
def schemes():
    return render_template('schemes.html')


@public_bp.route('/development')
def development():
    projects = DevelopmentProject.query.order_by(DevelopmentProject.id.desc()).all()
    return render_template('development.html', projects=projects)


@public_bp.route('/notices')
def notices():
    announcements = Announcement.query.filter_by(publication_status='published').order_by(Announcement.is_important.desc(), Announcement.published_date.desc()).all()
    return render_template('notices.html', announcements=announcements)


@public_bp.route('/contact')
def contact():
    return render_template('contact.html')


@public_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')


@public_bp.route('/terms')
def terms():
    return render_template('terms.html')


@public_bp.route('/qr')
def qr_landing():
    return render_template('qr_landing.html')

import os
from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models.database import db
from models.models import (
    User, Household, HouseholdMembershipCode,
    ResidentVerificationRequest, Complaint, ComplaintUpdate,
    Announcement, DevelopmentProject, ProjectUpdate,
    AuditLog, VillageSetting
)

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            flash("प्रशासक कक्षात प्रवेश करण्यासाठी कृपया लॉगिन करा.", "warning")
            return redirect(url_for('auth.login'))
        if g.user.role not in ['admin', 'staff']:
            flash("अनधिकृत प्रवेश! केवळ अधिकृत ग्रामपंचायत प्रशासक येथे प्रवेश करू शकतात.", "danger")
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    users_count = User.query.count()
    verified_residents = User.query.filter_by(role='resident').count()
    pending_verifications = ResidentVerificationRequest.query.filter_by(verification_status='pending').count()
    households_count = Household.query.count()
    active_listings = Household.query.filter_by(public_visibility=True).count()

    complaints_total = Complaint.query.count()
    complaints_pending = Complaint.query.filter(Complaint.status.in_(['submitted', 'in_progress'])).count()
    complaints_resolved = Complaint.query.filter_by(status='resolved').count()

    recent_complaints = Complaint.query.order_by(Complaint.id.desc()).limit(5).all()
    recent_audits = AuditLog.query.order_by(AuditLog.id.desc()).limit(8).all()

    metrics = {
        'users_count': users_count,
        'verified_residents': verified_residents,
        'pending_verifications': pending_verifications,
        'households_count': households_count,
        'active_listings': active_listings,
        'complaints_total': complaints_total,
        'complaints_pending': complaints_pending,
        'complaints_resolved': complaints_resolved
    }
    return render_template('admin/dashboard.html', metrics=metrics, complaints=recent_complaints, audits=recent_audits)


@admin_bp.route('/households')
@admin_required
def households():
    q = request.args.get('q', '').strip()
    query = Household.query
    if q:
        query = query.filter(
            (Household.full_name.ilike(f"%{q}%")) |
            (Household.house_number.ilike(f"%{q}%")) |
            (Household.locality.ilike(f"%{q}%")) |
            (Household.last_name.ilike(f"%{q}%"))
        )
    items = query.order_by(Household.id.desc()).all()
    return render_template('admin/households.html', households=items, search_q=q)


@admin_bp.route('/households/new', methods=['GET', 'POST'])
@admin_required
def household_new():
    if request.method == 'POST':
        fname = request.form.get('first_name', '').strip()
        mname = request.form.get('middle_name', '').strip()
        lname = request.form.get('last_name', '').strip()
        house_num = request.form.get('house_number', '').strip()
        locality = request.form.get('locality', '').strip()
        landmark = request.form.get('landmark', '').strip()
        lat = request.form.get('latitude', '').strip()
        lng = request.form.get('longitude', '').strip()
        consent = True if request.form.get('listing_consent') else False
        visible = True if request.form.get('public_visibility') else False

        # Build consistent full name
        full_name = f"{fname} {mname} {lname}".strip()
        if not full_name:
            full_name = request.form.get('full_name', '').strip()

        # Validate coordinate ranges
        try:
            flat = float(lat)
            flng = float(lng)
            if not (-90 <= flat <= 90 and -180 <= flng <= 180):
                raise ValueError("Out of range")
        except ValueError:
            flash("अवैध अक्षांश व रेखांश (Invalid coordinates). कृपया योग्य आकडे भरा.", "danger")
            return render_template('admin/household_form.html', household=None)

        # Image upload
        img_path = '/static/images/house_placeholder.jpg'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                fname_sec = secure_filename(file.filename)
                ext = fname_sec.rsplit('.', 1)[-1].lower() if '.' in fname_sec else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    saved_name = f"house_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{fname_sec}"
                    dest = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_name)
                    file.save(dest)
                    img_path = f"/static/uploads/{saved_name}"

        h = Household(
            first_name=fname,
            middle_name=mname,
            last_name=lname,
            full_name=full_name,
            house_number=house_num,
            locality=locality,
            landmark=landmark,
            latitude=flat,
            longitude=flng,
            image_path=img_path,
            listing_consent=consent,
            public_visibility=visible,
            verification_status='verified'
        )
        db.session.add(h)
        db.session.commit()

        # Generate unique verification code e.g. BLK-XXXX
        code_str = f"BLK-{h.id:04d}"
        code_obj = HouseholdMembershipCode(
            household_id=h.id,
            code_hash=generate_password_hash(code_str),
            code_display=code_str,
            created_by=g.user.id
        )
        db.session.add(code_obj)
        db.session.commit()

        # Audit
        audit = AuditLog(
            user_id=g.user.id,
            action='HOUSEHOLD_CREATE',
            entity_type='household',
            entity_id=h.id,
            details=f"Added household {full_name} ({house_num})"
        )
        db.session.add(audit)
        db.session.commit()

        flash(f"कुटुंब नोंदणी यशस्वी! पडताळणी कोड: {code_str}", "success")
        return redirect(url_for('admin.households'))

    return render_template('admin/household_form.html', household=None)


@admin_bp.route('/households/<int:hid>/edit', methods=['GET', 'POST'])
@admin_required
def household_edit(hid):
    h = Household.query.get_or_404(hid)
    if request.method == 'POST':
        fname = request.form.get('first_name', '').strip()
        mname = request.form.get('middle_name', '').strip()
        lname = request.form.get('last_name', '').strip()
        house_num = request.form.get('house_number', '').strip()
        locality = request.form.get('locality', '').strip()
        landmark = request.form.get('landmark', '').strip()
        lat = request.form.get('latitude', '').strip()
        lng = request.form.get('longitude', '').strip()
        consent = True if request.form.get('listing_consent') else False
        visible = True if request.form.get('public_visibility') else False

        full_name = f"{fname} {mname} {lname}".strip()
        if not full_name:
            full_name = request.form.get('full_name', '').strip()

        try:
            flat = float(lat)
            flng = float(lng)
        except ValueError:
            flash("अवैध अक्षांश किंवा रेखांश!", "danger")
            return render_template('admin/household_form.html', household=h)

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                fname_sec = secure_filename(file.filename)
                ext = fname_sec.rsplit('.', 1)[-1].lower() if '.' in fname_sec else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    saved_name = f"house_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{fname_sec}"
                    dest = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_name)
                    file.save(dest)
                    h.image_path = f"/static/uploads/{saved_name}"

        h.first_name = fname
        h.middle_name = mname
        h.last_name = lname
        h.full_name = full_name
        h.house_number = house_num
        h.locality = locality
        h.landmark = landmark
        h.latitude = flat
        h.longitude = flng
        h.listing_consent = consent
        h.public_visibility = visible

        db.session.commit()

        audit = AuditLog(
            user_id=g.user.id,
            action='HOUSEHOLD_UPDATE',
            entity_type='household',
            entity_id=h.id,
            details=f"Updated household {full_name}"
        )
        db.session.add(audit)
        db.session.commit()

        flash("कुटुंब माहिती अद्ययावत केली गेली आहे.", "success")
        return redirect(url_for('admin.households'))

    return render_template('admin/household_form.html', household=h)


@admin_bp.route('/households/<int:hid>/delete', methods=['POST'])
@admin_required
def household_delete(hid):
    h = Household.query.get_or_404(hid)
    h.public_visibility = False
    h.listing_consent = False
    db.session.commit()
    flash(f"कुटुंब नोंद ({h.full_name}) सार्वजनिक यादीतून निष्क्रिय केली गेली.", "info")
    return redirect(url_for('admin.households'))


@admin_bp.route('/complaints')
@admin_required
def complaints():
    cat = request.args.get('category')
    status = request.args.get('status')
    query = Complaint.query
    if cat:
        query = query.filter_by(category=cat)
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(Complaint.id.desc()).all()
    return render_template('admin/complaints.html', complaints=items, sel_cat=cat, sel_status=status)


@admin_bp.route('/complaints/<int:cid>', methods=['GET', 'POST'])
@admin_required
def complaint_detail(cid):
    c = Complaint.query.get_or_404(cid)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_status':
            new_status = request.form.get('status')
            assigned_staff = request.form.get('assigned_staff')
            res_details = request.form.get('resolution_details')
            public_msg = request.form.get('public_message', '').strip()
            internal_note = request.form.get('internal_note', '').strip()

            c.status = new_status
            if assigned_staff:
                c.assigned_staff = assigned_staff
            if res_details:
                c.resolution_details = res_details

            # Record public update
            if public_msg:
                up_pub = ComplaintUpdate(
                    complaint_id=c.id,
                    author_id=g.user.id,
                    update_type='public',
                    message=public_msg
                )
                db.session.add(up_pub)

            # Record internal note
            if internal_note:
                up_int = ComplaintUpdate(
                    complaint_id=c.id,
                    author_id=g.user.id,
                    update_type='internal',
                    message=f"[Internal Note] {internal_note}"
                )
                db.session.add(up_int)

            db.session.commit()

            audit = AuditLog(
                user_id=g.user.id,
                action='COMPLAINT_UPDATE',
                entity_type='complaint',
                entity_id=c.id,
                details=f"Status changed to {new_status}"
            )
            db.session.add(audit)
            db.session.commit()

            flash("तक्रार स्थिती व नोंदी यशस्वीरित्या अद्ययावत झाल्या.", "success")
            return redirect(url_for('admin.complaint_detail', cid=c.id))

    return render_template('admin/complaint_detail.html', complaint=c)


@admin_bp.route('/verifications')
@admin_required
def verifications():
    reqs = ResidentVerificationRequest.query.order_by(ResidentVerificationRequest.id.desc()).all()
    return render_template('admin/verifications.html', requests=reqs)


@admin_bp.route('/verifications/<int:rid>/action', methods=['POST'])
@admin_required
def verification_action(rid):
    v = ResidentVerificationRequest.query.get_or_404(rid)
    action = request.form.get('action')  # approve / reject
    notes = request.form.get('review_notes', '').strip()

    if action == 'approve':
        v.verification_status = 'approved'
        v.user.role = 'resident'
    else:
        v.verification_status = 'rejected'

    v.review_notes = notes
    v.reviewed_by = g.user.id
    db.session.commit()

    audit = AuditLog(
        user_id=g.user.id,
        action=f"VERIFICATION_{action.upper()}",
        entity_type='verification',
        entity_id=v.id,
        details=f"Verification request {action}d for user ID {v.user_id}"
    )
    db.session.add(audit)
    db.session.commit()

    flash(f"अर्ज {action} करण्यात आला.", "success")
    return redirect(url_for('admin.verifications'))


@admin_bp.route('/announcements', methods=['GET', 'POST'])
@admin_required
def announcements():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        lang = request.form.get('language', 'mr')
        status = request.form.get('publication_status', 'published')
        is_imp = True if request.form.get('is_important') else False

        if title and content:
            ann = Announcement(
                title=title,
                content=content,
                language=lang,
                publication_status=status,
                is_important=is_imp,
                author_id=g.user.id
            )
            db.session.add(ann)
            db.session.commit()
            flash("सूचना यशस्वीरित्या प्रसिद्ध करण्यात आली.", "success")
            return redirect(url_for('admin.announcements'))

    items = Announcement.query.order_by(Announcement.id.desc()).all()
    return render_template('admin/announcements.html', announcements=items)


@admin_bp.route('/projects', methods=['GET', 'POST'])
@admin_required
def projects():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        desc = request.form.get('description', '').strip()
        budget = request.form.get('approved_budget', '').strip()
        start_date = request.form.get('start_date', '').strip()
        exp_date = request.form.get('expected_completion', '').strip()
        status = request.form.get('status', 'ongoing')
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')

        if title and desc:
            p = DevelopmentProject(
                title=title,
                description=desc,
                approved_budget=budget,
                start_date=start_date,
                expected_completion=exp_date,
                status=status,
                latitude=float(lat) if lat and lat.strip() else None,
                longitude=float(lng) if lng and lng.strip() else None,
                author_id=g.user.id
            )
            db.session.add(p)
            db.session.commit()
            flash("विकास प्रकल्प नोंदवला गेला.", "success")
            return redirect(url_for('admin.projects'))

    items = DevelopmentProject.query.order_by(DevelopmentProject.id.desc()).all()
    return render_template('admin/projects.html', projects=items)


@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:uid>/role', methods=['POST'])
@admin_required
def user_update_role(uid):
    target = User.query.get_or_404(uid)
    new_role = request.form.get('role')
    new_status = request.form.get('account_status')
    if new_role:
        target.role = new_role
    if new_status:
        target.account_status = new_status
    db.session.commit()
    flash(f"वापरकर्ता {target.name} चे तपशील बदलले.", "success")
    return redirect(url_for('admin.users'))


@admin_bp.route('/audit-logs')
@admin_required
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.id.desc()).limit(100).all()
    return render_template('admin/audit_logs.html', logs=logs)


@admin_bp.route('/settings')
@admin_required
def settings():
    return render_template('admin/settings.html')

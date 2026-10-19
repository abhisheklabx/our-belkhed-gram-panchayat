from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models.database import db
from models.models import User, Household, HouseholdMembershipCode, ResidentVerificationRequest, AuditLog
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email_or_phone = request.form.get('email_or_phone', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        preferred_lang = request.form.get('preferred_language', 'mr')
        village_connection = request.form.get('village_connection', 'resident')

        if not name or not email_or_phone or not password:
            flash("कृपया नाव, ईमेल/मोबाईल आणि पासवर्ड प्रविष्ट करा. (All fields are required)", "danger")
            return render_template('auth/register.html')

        if len(password) < 6:
            flash("संकेतशब्द (Password) किमान ६ वर्णांचा असावा. (Password must be at least 6 characters)", "danger")
            return render_template('auth/register.html')

        if password != confirm_password:
            flash("दोन्ही पासवर्ड जुळत नाहीत. कृपया पुन्हा तपासा. (Passwords do not match)", "danger")
            return render_template('auth/register.html')

        existing_user = User.query.filter_by(email_or_phone=email_or_phone).first()
        if existing_user:
            flash("हा ईमेल किंवा मोबाईल क्रमांक आधीच नोंदणीकृत आहे. कृपया लॉगिन करा.", "warning")
            return redirect(url_for('auth.login'))

        # Create new user with encrypted password hash
        new_user = User(
            name=name,
            email_or_phone=email_or_phone,
            role='resident' if village_connection == 'resident' else 'visitor',
            preferred_language=preferred_lang,
            village_connection=village_connection,
            account_status='active'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Audit log
        audit = AuditLog(
            user_id=new_user.id,
            action='USER_REGISTRATION',
            entity_type='user',
            entity_id=new_user.id,
            details=f"New user registered: {name} ({email_or_phone})"
        )
        db.session.add(audit)
        db.session.commit()

        flash("आपले खाते यशस्वीरित्या तयार झाले आहे! आता आपण लॉगिन करू शकता.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        email_or_phone = request.form.get('email_or_phone', '').strip().lower()
        password = request.form.get('password', '')

        if not email_or_phone or not password:
            flash("कृपया लॉगिन तपशील प्रविष्ट करा. (Please provide both credentials)", "danger")
            return render_template('auth/login.html')

        user = User.query.filter_by(email_or_phone=email_or_phone).first()
        if user and user.check_password(password):
            if user.account_status != 'active':
                flash("आपले खाते तात्पुरते निष्क्रिय करण्यात आले आहे. कृपया ग्रामपंचायतीशी संपर्क साधा.", "danger")
                return render_template('auth/login.html')

            # Set session
            session['user_id'] = user.id
            session['lang'] = user.preferred_language or session.get('lang', 'mr')

            audit = AuditLog(
                user_id=user.id,
                action='USER_LOGIN',
                entity_type='user',
                entity_id=user.id,
                details=f"Successful login: {user.name}"
            )
            db.session.add(audit)
            db.session.commit()

            flash(f"स्वागत आहे, {user.name}!", "success")
            if user.role in ['admin', 'staff']:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('public.index'))
        else:
            flash("चुकीचा ईमेल/मोबाईल किंवा पासवर्ड! कृपया पुन्हा तपासा.", "danger")

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    uid = session.get('user_id')
    if uid:
        audit = AuditLog(
            user_id=uid,
            action='USER_LOGOUT',
            entity_type='user',
            entity_id=uid,
            details="User logged out"
        )
        db.session.add(audit)
        db.session.commit()

    session.pop('user_id', None)
    flash("आपण यशस्वीरित्या बाहेर पडला आहात. (Logged out successfully)", "info")
    return redirect(url_for('public.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not g.user:
        flash("कृपया आधी लॉगिन करा.", "warning")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            g.user.name = request.form.get('name', g.user.name).strip()
            g.user.preferred_language = request.form.get('preferred_language', g.user.preferred_language)
            session['lang'] = g.user.preferred_language
            db.session.commit()
            flash("प्रोफाइल माहिती अद्ययावत केली गेली आहे.", "success")

        elif action == 'verify_code':
            code_input = request.form.get('household_code', '').strip().upper()
            if not code_input:
                flash("कृपया कुटुंब पडताळणी कोड प्रविष्ट करा.", "warning")
            else:
                # Match code
                matching_code = None
                all_codes = HouseholdMembershipCode.query.filter_by(is_used=False).all()
                for c in all_codes:
                    if (c.code_display and c.code_display.upper() == code_input) or check_password_hash(c.code_hash, code_input):
                        matching_code = c
                        break

                if matching_code:
                    req = ResidentVerificationRequest(
                        user_id=g.user.id,
                        household_id=matching_code.household_id,
                        verification_status='approved',
                        verification_code_entered=code_input,
                        review_notes='स्वयंचलित पडताळणी कोडद्वारे तात्काळ मंजूर.'
                    )
                    matching_code.is_used = True
                    g.user.role = 'resident'
                    db.session.add(req)
                    db.session.commit()
                    flash("अभिनंदन! आपले कुटुंब पडताळणी यशस्वी झाली आहे आणि आपण अधिकृत रहिवासी म्हणून प्रमाणित झाला आहात.", "success")
                else:
                    flash("अवैध किंवा आधीच वापरलेला कुटुंब कोड. कृपया ग्रामपंचायतीशी संपर्क साधा.", "danger")

        return redirect(url_for('auth.profile'))

    user_requests = ResidentVerificationRequest.query.filter_by(user_id=g.user.id).all()
    user_complaints = g.user.complaints
    return render_template('auth/profile.html', requests=user_requests, complaints=user_complaints)

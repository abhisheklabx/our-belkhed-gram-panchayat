from flask import Blueprint, request, jsonify, session, g
from models.models import Household
from services.gemini_service import ask_belkhed_assistant
from services.gis_service import get_belkhed_gis_geojson

api_bp = Blueprint('api', __name__)

@api_bp.route('/households/search')
def search_households():
    raw_query = request.args.get('q', '').strip()
    if not raw_query:
        return jsonify({'results': [], 'count': 0, 'query': ''})

    # Normalize query (lowercase, clean multiple spaces)
    q_tokens = [tok for tok in raw_query.lower().split() if tok]
    
    # Query ONLY publicly approved records with consent
    base_query = Household.query.filter_by(public_visibility=True, listing_consent=True)

    # Search by full name, first name, middle name, last name, or house number
    filters = []
    for tok in q_tokens:
        tok_pattern = f"%{tok}%"
        filters.append(
            (Household.full_name.ilike(tok_pattern)) |
            (Household.first_name.ilike(tok_pattern)) |
            (Household.middle_name.ilike(tok_pattern)) |
            (Household.last_name.ilike(tok_pattern)) |
            (Household.house_number.ilike(tok_pattern)) |
            (Household.locality.ilike(tok_pattern))
        )

    # Execute search
    results_query = base_query
    for f in filters:
        results_query = results_query.filter(f)

    households = results_query.order_by(Household.house_number.asc()).limit(50).all()

    # Suggestions / Autocomplete list
    suggestions = [h.full_name for h in households[:5]]

    data = [h.to_public_dict() for h in households]
    return jsonify({
        'query': raw_query,
        'count': len(data),
        'suggestions': suggestions,
        'results': data
    })


@api_bp.route('/assistant/chat', methods=['POST'])
def assistant_chat():
    payload = request.get_json(silent=True) or {}
    message = payload.get('message', '').strip()
    lang = payload.get('lang', session.get('lang', 'mr'))

    if not message:
        return jsonify({'success': False, 'error': 'Empty message'}), 400

    if len(message) > 500:
        return jsonify({'success': False, 'error': 'Message exceeds limit (500 characters)'}), 400

    result = ask_belkhed_assistant(message, lang)
    return jsonify(result)


@api_bp.route('/gis/data')
def gis_data():
    data = get_belkhed_gis_geojson()
    return jsonify(data)


@api_bp.route('/set-language', methods=['POST'])
def set_language():
    payload = request.get_json(silent=True) or {}
    lang = payload.get('lang', 'mr')
    if lang in ['mr', 'hi', 'en']:
        session['lang'] = lang
        if g.user:
            g.user.preferred_language = lang
            from models.database import db
            db.session.commit()
        return jsonify({'success': True, 'lang': lang})
    return jsonify({'success': False, 'error': 'Invalid language'}), 400

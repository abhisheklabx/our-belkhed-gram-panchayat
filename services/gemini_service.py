import os
import requests
import json
from config import Config

VILLAGE_SYSTEM_PROMPT = """
You are 'Belkhed Assistant' (बेलखेड सहाय्यक), a helpful, polite civic AI assistant for the official 'Our Belkhed | आपले बेलखेड' digital Gram Panchayat portal.
Village: Belkhed, Taluka: Umarkhed, District: Yavatmal, Maharashtra, India. PIN: 445206.
Coordinates: Latitude 19.616556, Longitude 77.636556.
Area: 745.31 hectares. 2011 Census: 2,262 population (1,118 male, 1,144 female), 488 households, 85.10% literacy rate.
Distance: 9 km from Umarkhed, 120 km from Yavatmal.

Key instructions:
1. Always respond in the language asked by the user (Marathi, Hindi, or English).
2. Help users navigate the website:
   - 'Find a Home' (/find-home): Search households by person's name, surname, or house number and get direct Google Maps navigation.
   - 'GIS Map' (/gis-map): View official village boundary, schools, water tank, Gram Panchayat office, and landmark layers.
   - 'Register Complaint' (/complaint/new): Submit grievances for water supply, roads, electricity, or sanitation with photos and GPS.
   - 'Track Complaint' (/complaint/track): Track status using complaint ID.
   - 'Government Schemes' (/schemes): Information on PM Awas Yojana, Jal Jeevan Mission, Krishi Sanman, etc.
   - 'Development Work' (/development): Ongoing village projects and verified budgets.
3. Be respectful, accurate, and concise. Never invent phone numbers, unofficial statistics, or private resident details.
4. Direct users to the Gram Panchayat office or Gram Sevak for legal or document certification matters.
"""

def ask_belkhed_assistant(user_message, lang='mr'):
    """
    Sends message to Gemini API or uses the offline prototype knowledge engine.
    """
    api_key = Config.GEMINI_API_KEY
    clean_key = (api_key or '').strip()

    # Pre-crafted local intelligent fallback responses
    def get_fallback_response(query, language):
        q = query.lower()
        if 'घर' in q or 'home' in q or 'house' in q or 'पत्ता' in q or 'रस्ता' in q or 'दिशा' in q or 'location' in q:
            if language == 'mr':
                return "गावातील घर शोधण्यासाठी 'घर शोधा' (Find a Home) पेजवर जा. तेथे रहिवाशांचे नाव, आडनाव किंवा घर क्रमांक टाकून शोधा. मिळालेल्या निकालावर 'View Location in Google Maps' क्लिक केल्यास थेट गुगल मॅप्सद्वारे घराची अचूक दिशा व अंतर दिसेल!"
            elif language == 'hi':
                return "गांव में किसी का घर ढूंढने के लिए 'घर खोजें' (Find a Home) पृष्ठ पर जाएं। वहां नाम या घर संख्या डालकर खोजें और 'View Location in Google Maps' बटन दबाकर सीधे नेविगेशन प्राप्त करें।"
            else:
                return "To locate a household, navigate to the 'Find a Home' page. Search by resident's name, surname, or house number. Click 'View Location in Google Maps' on any result card for direct GPS turn-by-turn navigation."

        if 'तक्रार' in q or 'complaint' in q or 'समस्या' in q or 'पाणी' in q or 'रस्ता' in q or 'लाईट' in q or 'light' in q or 'water' in q:
            if language == 'mr':
                return "बेलखेड ग्रामपंचायतीकडे तक्रार नोंदवण्यासाठी 'तक्रार नोंदवा' (Services -> Complaint) मेनूमध्ये जा. तेथे पाणीपुरवठा, रस्ते, स्वच्छता किंवा दिवाबत्ती या विषयाची तक्रार फोटोसह व आवाजाने (Voice Typing) नोंदवू शकता. तुम्हाला ट्रॅकिंग नंबर मिळेल."
            elif language == 'hi':
                return "गांव की समस्या या शिकायत दर्ज करने के लिए 'सेवाएं' मेनू में जाकर नई शिकायत दर्ज करें। आप अपनी आवाज (Voice Typing) या टाइप करके फोटो सहित शिकायत भेज सकते हैं।"
            else:
                return "To register a grievance regarding water supply, sanitation, roads, or streetlights, visit the 'File a Complaint' section. You can upload a photo, use voice typing, and track your grievance using your unique Complaint ID."

        if 'योजना' in q or 'scheme' in q or 'अनुदान' in q or 'आवास' in q or 'pm' in q:
            if language == 'mr':
                return "ग्रामपंचायत बेलखेड अंतर्गत केंद्र व राज्य शासनाच्या विविध योजनांची माहिती 'शासकीय योजना' (Schemes) विभागात उपलब्ध आहे, जसे की पंतप्रधान आवास योजना, जल जीवन मिशन, नरेगा व शेतकरी योजना."
            elif language == 'hi':
                return "सरकारी योजनाओं की जानकारी के लिए 'योजनाएं' (Schemes) अनुभाग देखें। यहां पीएम आवास, जल जीवन मिशन और कृषि योजनाओं की पात्रता और आवेदन प्रक्रिया समझाई गई है।"
            else:
                return "For government welfare schemes, visit the 'Government Schemes' page. It details PM Awas Yojana, Jal Jeevan Mission, and farmer assistance criteria."

        if 'माहिती' in q or 'लोकसंख्या' in q or 'population' in q or 'area' in q or 'क्षेत्रफळ' in q or 'गाव' in q or 'belkhed' in q:
            if language == 'mr':
                return "बेलखेड (ता. उमरखेड, जि. यवतमाळ): क्षेत्रफळ ७४५.३१ हेक्टर, २०११ च्या जनगणनेनुसार लोकसंख्या २,२६२ (पुरुष १,११८, स्त्रिया १,१४४), ४८८ कुटुंबे आणि साक्षरता दर ८५.१०% आहे. उमरखेड शहरापासून अंतर सुमारे ९ किमी आहे."
            elif language == 'hi':
                return "बेलखेड (तहसील उमरखेड, जिला यवतमाळ): क्षेत्रफल 745.31 हेक्टेयर, 2011 जनगणना अनुसार आबादी 2,262 और 488 परिवार हैं। उमरखेड से यह 9 किमी दूर है।"
            else:
                return "Belkhed Village (Umarkhed Taluka, Yavatmal District): Total area 745.31 hectares. 2011 Census: population 2,262, 488 households, and 85.10% literacy rate. Located 9 km from Umarkhed."

        # Default general response
        if language == 'mr':
            return f"नमस्कार! मी बेलखेड सहाय्यक आहे. मी तुम्हाला घर शोधणे, तक्रार नोंदवणे, ग्रामपंचायत योजना, जीआयएस नकाशा व गाव माहितीबाबत मार्गदर्शन करू शकतो. कृपया आपला प्रश्न विचारा."
        elif language == 'hi':
            return f"नमस्ते! मैं बेलखेड सहायक हूँ। मैं आपको घर खोजने, शिकायत दर्ज करने, सरकारी योजनाओं और गांव की जानकारी में सहायता कर सकता हूँ।"
        else:
            return f"Hello! I am Belkhed Assistant. I can assist you with household navigation, grievance redressal, GIS village maps, public services, and village demographics."

    # If valid looking Gemini API key exists, call Gemini REST API
    if clean_key and len(clean_key) > 20 and not clean_key.startswith("your_"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={clean_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{VILLAGE_SYSTEM_PROMPT}\nUser Language: {lang}\nUser Question: {user_message}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 400
                }
            }
            res = requests.post(url, headers=headers, json=payload, timeout=6)
            if res.status_code == 200:
                data = res.json()
                answer = data['candidates'][0]['content']['parts'][0]['text']
                return {
                    "success": True,
                    "response": answer,
                    "source": "Gemini Live API"
                }
        except Exception as e:
            # Fall through gracefully to intelligent fallback
            pass

    # Fallback Prototype Mode
    return {
        "success": True,
        "response": get_fallback_response(user_message, lang),
        "source": "Belkhed Civic Assistant Engine (Local Prototype Mode)"
    }

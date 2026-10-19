# आपले बेलखेड | Our Belkhed
> **Digital Gram Panchayat & Citizen Services Platform**
> Village: Belkhed (बेलखेड), Taluka: Umarkhed, District: Yavatmal, Maharashtra, India — PIN: 445206
> Coordinates: Latitude 19.616556, Longitude 77.636556

---

## 🌟 Overview

**Our Belkhed (आपले बेलखेड)** is a modern, responsive digital Gram Panchayat and civic-services platform. It empowers citizens, elderly villagers, visitors, and administrators with:
1. **Find a Home (घर शोधा):** Search households by resident's name, surname, or house number and open turn-by-turn Google Maps navigation.
2. **GIS Village Map:** Interactive Leaflet GIS map with village revenue boundaries (745.31 hectares), gaothan residential settlement, water tanks, schools, health sub-centre, and registered household points.
3. **Public Grievance Redressal (तक्रार निवारण):** Submit complaints for water supply, roads, sanitation, electricity, or public infrastructure with photos, GPS coordinates, voice typing, and unique tracking IDs.
4. **Professional Authentication:** Secure session-based authentication with Werkzeug password hashing (passwords are cryptographically encrypted; even administrators cannot read them).
5. **Belkhed AI Assistant (बेलखेड सहाय्यक):** Multilingual civic guide powered by Google Gemini API with offline prototype fallback.
6. **Voice Typing & Speech Synthesis:** Speak in Marathi, Hindi, or English using Web Speech API.
7. **Mobile-First Citizen Portal & PC-Optimized Admin Desk:** Fast, accessible UI for smartphones and a comprehensive desktop management dashboard for Gram Panchayat staff.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.13)
- MySQL Server (running on `localhost:3306`)

### 2. Installation
```bash
# Clone or navigate to the directory
cd "c:\Users\abhis\Downloads\Aaple Belkhed"

# Install required dependencies
pip install -r requirements.txt
```

### 3. Database Initialization & Demo Data
The system automatically creates database tables and seeds demo households, complaints, announcements, and development projects:
```bash
python scripts/seed_data.py
```

### 4. Running the Web Application
```bash
python app.py
```
Open your browser and navigate to: **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Login Accounts (Demo Data)

### 👑 Administrator Account (PC Admin Desk)
- **URL:** [http://localhost:5000/login](http://localhost:5000/login)
- **Email:** `abhishek@belkhed.gov.in`
- **Password:** `Pass@123`
- *Access to Admin Dashboard at `/admin`: Manage households, approve resident requests, resolve complaints, publish notices, and view security audit logs.*

### 👤 Sample Citizen / Resident Account
- **Email:** `resident@belkhed.gov.in`
- **Password:** `Resident@123`

---

## 📍 Key Features & Route Architecture

| Route | Page | Description |
|---|---|---|
| `/` | **Home Portal** | Welcome Hero, 2011 Census metrics, Quick cards, embedded map & emergency contacts |
| `/find-home` | **Find a Home** | Real-time household search with Google Maps direct navigation & voice typing |
| `/gis-map` | **GIS Map** | Fullscreen GIS layer viewer (revenue boundary, amenities, gaothan, roads) |
| `/village` | **Village Profile** | Belkhed historical 2011 Census data, administrative profile & economy |
| `/services` | **Gram Services** | Catalog of public services, grievances, and schemes |
| `/complaints/new` | **Register Grievance** | Complaint submission with GPS auto-locate, photo upload, and voice typing |
| `/complaints/track`| **Track Status** | Real-time grievance status tracking by Complaint ID (e.g., `BLK-CMP-2026-0001`) |
| `/schemes` | **Govt Schemes** | PM Awas, Jal Jeevan Mission, PM-Kisan & NREGA guidelines |
| `/development` | **Development Works**| Ongoing and completed village projects with approved budgets |
| `/notices` | **Notices** | Gram Sabha meetings, health camps, and public alerts |
| `/qr` | **QR Code Landing** | Downloadable QR code for public village signage |
| `/register` | **Registration** | Account creation with prominent data privacy guarantee banner |
| `/login` | **Authentication** | Secure rate-limited login |
| `/profile` | **My Profile** | Account settings & Household verification code redemption (`BLK-8491`) |
| `/admin/*` | **Admin Desk** | Desktop-friendly PC suite for Sarpanch / Gram Sevak management |

---

## 🔒 Security & Privacy Notice
As displayed on the registration page:
> *"We do NOT collect sensitive private information. We only collect publicly required details (Name, Email/Mobile, and Password). Passwords are cryptographically hashed using standard algorithms and cannot be read by anyone, including administrators."*

---

## 🧪 Running Automated Tests
Run the test suite covering 13 comprehensive test cases:
```bash
python -m unittest tests/test_app.py
```

---

## 📜 Footer Notice
```text
© All Rights Reserved Grampanchayat Belkhed
Made by Abhishek Thakare
```

/**
 * Main application scripts for Our Belkhed
 */

// Language switcher
function changeLanguage(lang) {
  fetch('/api/set-language', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lang: lang })
  }).then(res => res.json()).then(data => {
    if (data.success) {
      // Reload current page to render new translations
      window.location.reload();
    }
  }).catch(err => {
    // Fallback: URL query param reload
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
  });
}

// Open Google Maps directions with optional user GPS
function openGoogleDirections(lat, lng) {
  if (!lat || !lng) {
    alert("स्थान गुणक (Coordinates) उपलब्ध नाहीत.");
    return;
  }

  // Ask citizen if they want directions from their current location
  const useGPS = confirm("आपल्या सध्याच्या स्थानावरून थेट गुगल मॅप्स मार्गदर्शन (Turn-by-turn Directions) हवे आहे का?\n(Do you want directions from your current GPS location?)");
  if (useGPS && navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const uLat = pos.coords.latitude;
        const uLng = pos.coords.longitude;
        const url = `https://www.google.com/maps/dir/?api=1&origin=${uLat},${uLng}&destination=${lat},${lng}&travelmode=driving`;
        window.open(url, '_blank');
      },
      (err) => {
        // Geolocation denied or unavailable - still open destination directly
        const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
        window.open(url, '_blank');
      },
      { timeout: 7000 }
    );
  } else {
    // Directly open Google Maps destination
    const url = `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;
    window.open(url, '_blank');
  }
}

// Auto-fill coordinates on complaint form if user clicks GPS button
function getCurrentLocationForComplaint(latInputId, lngInputId, addressInputId) {
  if (!navigator.geolocation) {
    alert("आपल्या डिव्हाइसवर जीपीएस सुविधा उपलब्ध नाही.");
    return;
  }
  const btn = event.currentTarget;
  const originalHtml = btn.innerHTML;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> शोधत आहे...';
  btn.disabled = true;

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      document.getElementById(latInputId).value = pos.coords.latitude.toFixed(7);
      document.getElementById(lngInputId).value = pos.coords.longitude.toFixed(7);
      if (addressInputId && !document.getElementById(addressInputId).value) {
        document.getElementById(addressInputId).value = `GPS: ${pos.coords.latitude.toFixed(6)}, ${pos.coords.longitude.toFixed(6)} (Belkhed)`;
      }
      btn.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i> स्थान नोंदवले';
      setTimeout(() => {
        btn.innerHTML = originalHtml;
        btn.disabled = false;
      }, 3000);
    },
    (err) => {
      alert("जीपीएस परवानगी नाकारली गेली किंवा स्थान सापडले नाही. आपण पत्ता स्वतः लिहू शकता.");
      btn.innerHTML = originalHtml;
      btn.disabled = false;
    },
    { enableHighAccuracy: true, timeout: 8000 }
  );
}

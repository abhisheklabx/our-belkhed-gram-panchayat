import json

def get_belkhed_gis_geojson():
    """
    Generates synthetic GIS GeoJSON boundary and point layers for Belkhed Village.
    Coordinates center: 19.616556, 77.636556
    Area: 745.31 hectares
    """
    geojson = {
        "type": "FeatureCollection",
        "name": "Belkhed_Village_GIS_Layers",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": [
            # 1. Village Revenue Boundary Polygon (~745 hectares approximate polygon)
            {
                "type": "Feature",
                "properties": {
                    "id": "poly_boundary",
                    "layer": "boundary",
                    "name": "Belkhed Gram Panchayat Boundary",
                    "name_mr": "बेलखेड ग्रामपंचायत महसूल सीमा",
                    "category": "Village Boundary",
                    "area_hectares": 745.31,
                    "stroke": "#1b5e20",
                    "stroke_width": 3,
                    "fill": "#4caf50",
                    "fill_opacity": 0.12,
                    "description": "745.31 Hectares - Belkhed Revenue Village, Umarkhed Taluka, Yavatmal"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [77.6220, 19.6080],
                        [77.6330, 19.6050],
                        [77.6480, 19.6090],
                        [77.6520, 19.6200],
                        [77.6470, 19.6280],
                        [77.6320, 19.6270],
                        [77.6210, 19.6210],
                        [77.6220, 19.6080]
                    ]]
                }
            },
            # 2. Gaothan / Settlement Core
            {
                "type": "Feature",
                "properties": {
                    "id": "poly_gaothan",
                    "layer": "residential",
                    "name": "Belkhed Gaothan (Main Residential Settlement)",
                    "name_mr": "बेलखेड गावठाण व वस्ती क्षेत्र",
                    "category": "Settlement Area",
                    "stroke": "#d84315",
                    "stroke_width": 2,
                    "fill": "#ff7043",
                    "fill_opacity": 0.25,
                    "description": "Core residential settlement & households area"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [77.6335, 19.6145],
                        [77.6395, 19.6140],
                        [77.6410, 19.6190],
                        [77.6350, 19.6195],
                        [77.6335, 19.6145]
                    ]]
                }
            },
            # 3. Main Road Line
            {
                "type": "Feature",
                "properties": {
                    "id": "road_main",
                    "layer": "infrastructure",
                    "name": "Umarkhed - Belkhed Approach Road",
                    "name_mr": "उमरखेड - बेलखेड मुख्य रस्ता",
                    "category": "Paved Road",
                    "color": "#e65100",
                    "weight": 4
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [77.6250, 19.6110],
                        [77.6310, 19.6135],
                        [77.636556, 19.616556],
                        [77.6420, 19.6185],
                        [77.6490, 19.6220]
                    ]
                }
            },
            # 4. Gram Panchayat Office Point
            {
                "type": "Feature",
                "properties": {
                    "id": "poi_gp",
                    "layer": "civic",
                    "name": "Gram Panchayat Belkhed Office",
                    "name_mr": "ग्रामपंचायत बेलखेड कार्यालय",
                    "category": "Government Office",
                    "icon": "building",
                    "color": "#1b5e20",
                    "contact": "Gram Sevak / Sarpanch Desk"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.636556, 19.616556]
                }
            },
            # 5. Overhead Water Tank
            {
                "type": "Feature",
                "properties": {
                    "id": "poi_watertank",
                    "layer": "civic",
                    "name": "Gram Panchayat Water Supply Reservoir Tank",
                    "name_mr": "सार्वजनिक पाणीपुरवठा पाण्याची टाकी",
                    "category": "Water Supply",
                    "icon": "water",
                    "color": "#0288d1"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.637100, 19.617200]
                }
            },
            # 6. ZP Primary School
            {
                "type": "Feature",
                "properties": {
                    "id": "poi_school",
                    "layer": "civic",
                    "name": "Z.P. Primary School Belkhed",
                    "name_mr": "जि. प. प्राथमिक शाळा बेलखेड",
                    "category": "Education",
                    "icon": "graduation-cap",
                    "color": "#6a1b9a"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.635800, 19.617800]
                }
            },
            # 7. Anganwadi Centre
            {
                "type": "Feature",
                "properties": {
                    "id": "poi_anganwadi",
                    "layer": "civic",
                    "name": "Anganwadi Kendra Belkhed",
                    "name_mr": "अंगणवाडी केंद्र बेलखेड",
                    "category": "Child Welfare & Nutrition",
                    "icon": "heart",
                    "color": "#ad1457"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.635200, 19.616900]
                }
            },
            # 8. Primary Health Sub-Centre
            {
                "type": "Feature",
                "properties": {
                    "id": "poi_health",
                    "layer": "civic",
                    "name": "Primary Health Sub-Centre (Arogya Upkendra)",
                    "name_mr": "प्राथमिक आरोग्य उपकेंद्र बेलखेड",
                    "category": "Healthcare",
                    "icon": "medkit",
                    "color": "#c62828"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.634900, 19.615800]
                }
            },
            # 9. Hanuman Temple
            {
                "type": "Feature",
                "properties": {
                    "id": "poi_temple",
                    "layer": "heritage",
                    "name": "Shri Hanuman Mandir",
                    "name_mr": "श्री हनुमान मंदिर",
                    "category": "Place of Worship",
                    "icon": "sun",
                    "color": "#f57f17"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.636900, 19.616200]
                }
            },
            # 10. Sample Household Coordinates
            {
                "type": "Feature",
                "properties": {
                    "id": "poi_sample_house",
                    "layer": "household",
                    "name": "Sample Household (Thakare Nivas)",
                    "name_mr": "नमुना घर (ठाकरे निवास)",
                    "category": "Registered Household",
                    "house_no": "BLK-01",
                    "icon": "home",
                    "color": "#2e7d32"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.6374039, 19.6164779]
                }
            }
        ]
    }
    return geojson

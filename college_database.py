"""
Karnataka Colleges Database
===========================

Known colleges in Karnataka with their official websites and information.
"""

KARNATAKA_COLLEGES = {
    # Engineering Colleges
    "bangalore institute of technology": {
        "official_name": "Bangalore Institute of Technology",
        "website": "https://www.bit-bangalore.edu.in/",
        "location": "Bangalore, Karnataka",
        "type": "Engineering",
        "established": "1979",
        "affiliation": "VTU"
    },
    "rv college of engineering": {
        "official_name": "R.V. College of Engineering",
        "website": "https://www.rvce.edu.in/",
        "location": "Bangalore, Karnataka", 
        "type": "Engineering",
        "established": "1963",
        "affiliation": "VTU"
    },
    "bmsce": {
        "official_name": "BMS College of Engineering",
        "website": "https://bmsce.ac.in/",
        "location": "Bangalore, Karnataka",
        "type": "Engineering", 
        "established": "1946",
        "affiliation": "VTU"
    },
    "ms ramaiah institute of technology": {
        "official_name": "M.S. Ramaiah Institute of Technology",
        "website": "https://msrit.edu/",
        "location": "Bangalore, Karnataka",
        "type": "Engineering",
        "established": "1962",
        "affiliation": "VTU"
    },
    "sit": {
        "official_name": "Siddaganga Institute of Technology",
        "website": "https://sit.ac.in/",
        "location": "Tumkur, Karnataka",
        "type": "Engineering",
        "established": "1963",
        "affiliation": "VTU"
    },
    "pes university": {
        "official_name": "PES University",
        "website": "https://pes.edu/",
        "location": "Bangalore, Karnataka",
        "type": "Engineering",
        "established": "1972",
        "affiliation": "Autonomous"
    },
    "manipal institute of technology": {
        "official_name": "Manipal Institute of Technology",
        "website": "https://manipal.edu/mit.html",
        "location": "Manipal, Karnataka",
        "type": "Engineering",
        "established": "1957",
        "affiliation": "Deemed University"
    },
    
    # Medical Colleges
    "bangalore medical college": {
        "official_name": "Bangalore Medical College and Research Institute",
        "website": "https://bmcri.edu.in/",
        "location": "Bangalore, Karnataka",
        "type": "Medical",
        "established": "1955",
        "affiliation": "RGUHS"
    },
    "mysore medical college": {
        "official_name": "Mysore Medical College & Research Institute",
        "website": "https://www.mmcri.gov.in/",
        "location": "Mysore, Karnataka",
        "type": "Medical",
        "established": "1924",
        "affiliation": "RGUHS"
    },
    "karnataka institute of medical sciences": {
        "official_name": "Karnataka Institute of Medical Sciences",
        "website": "https://kims.ac.in/",
        "location": "Hubli, Karnataka",
        "type": "Medical",
        "established": "1957",
        "affiliation": "RGUHS"
    },
    
    # Universities
    "iisc": {
        "official_name": "Indian Institute of Science",
        "website": "https://iisc.ac.in/",
        "location": "Bangalore, Karnataka",
        "type": "Research University",
        "established": "1909",
        "affiliation": "Institute of Eminence"
    },
    "bangalore university": {
        "official_name": "Bangalore University",
        "website": "https://bangaloreuniversity.ac.in/",
        "location": "Bangalore, Karnataka",
        "type": "University",
        "established": "1964",
        "affiliation": "State University"
    },
    "mysore university": {
        "official_name": "University of Mysore",
        "website": "https://uni-mysore.ac.in/",
        "location": "Mysore, Karnataka",
        "type": "University",
        "established": "1916",
        "affiliation": "State University"
    },
    "karnataka university": {
        "official_name": "Karnatak University",
        "website": "https://kud.ac.in/",
        "location": "Dharwad, Karnataka",
        "type": "University",
        "established": "1949",
        "affiliation": "State University"
    },
    
    # Management Colleges
    "iim bangalore": {
        "official_name": "Indian Institute of Management Bangalore",
        "website": "https://www.iimb.ac.in/",
        "location": "Bangalore, Karnataka",
        "type": "Management",
        "established": "1973",
        "affiliation": "Institute of National Importance"
    },
    "christ university": {
        "official_name": "CHRIST (Deemed to be University)",
        "website": "https://christuniversity.in/",
        "location": "Bangalore, Karnataka",
        "type": "Multi-disciplinary",
        "established": "1969",
        "affiliation": "Deemed University"
    }
}

def find_college_by_name(search_name: str):
    """Find college information by name (fuzzy matching)."""
    search_name = search_name.lower().strip()
    
    # Direct match
    if search_name in KARNATAKA_COLLEGES:
        return KARNATAKA_COLLEGES[search_name]
    
    # Fuzzy matching
    for key, college_info in KARNATAKA_COLLEGES.items():
        if search_name in key or key in search_name:
            return college_info
        
        # Check official name
        official_name = college_info['official_name'].lower()
        if search_name in official_name or any(word in official_name for word in search_name.split()):
            return college_info
    
    return None

def get_all_college_names():
    """Get list of all known college names."""
    names = []
    for key, info in KARNATAKA_COLLEGES.items():
        names.append(info['official_name'])
    return sorted(names)

def get_colleges_by_type(college_type: str):
    """Get colleges by type (Engineering, Medical, etc.)."""
    matching_colleges = []
    for key, info in KARNATAKA_COLLEGES.items():
        if info['type'].lower() == college_type.lower():
            matching_colleges.append(info)
    return matching_colleges
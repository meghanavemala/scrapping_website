"""
Data Processing Pipeline
=======================

Utilities for cleaning, structuring, and formatting scraped college data
before AI processing.
"""

import re
import json
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse
import pandas as pd
from datetime import datetime

from utils import setup_logger, clean_text, normalize_phone_number, validate_email

class DataProcessor:
    """Main data processing class for college information."""
    
    def __init__(self):
        self.logger = setup_logger()
        
        # Define known college keywords for validation
        self.college_keywords = {
            'engineering', 'medical', 'arts', 'science', 'commerce', 'management',
            'university', 'college', 'institute', 'school', 'academy', 'education'
        }
        
        # Define course categories
        self.course_categories = {
            'Engineering': [
                'btech', 'be', 'mtech', 'me', 'civil', 'mechanical', 'electrical',
                'computer science', 'information technology', 'electronics', 'chemical'
            ],
            'Medical': [
                'mbbs', 'bds', 'md', 'ms', 'nursing', 'pharmacy', 'physiotherapy',
                'medical', 'dental', 'veterinary'
            ],
            'Management': [
                'mba', 'bba', 'pgdm', 'management', 'business administration',
                'finance', 'marketing', 'hr', 'operations'
            ],
            'Arts': [
                'ba', 'ma', 'english', 'history', 'political science', 'sociology',
                'psychology', 'literature', 'fine arts', 'performing arts'
            ],
            'Science': [
                'bsc', 'msc', 'physics', 'chemistry', 'biology', 'mathematics',
                'botany', 'zoology', 'microbiology', 'biotechnology'
            ],
            'Commerce': [
                'bcom', 'mcom', 'commerce', 'accounting', 'economics', 'taxation',
                'banking', 'insurance'
            ],
            'Computer Science': [
                'bca', 'mca', 'computer science', 'information technology',
                'software engineering', 'data science', 'artificial intelligence'
            ],
            'Law': [
                'llb', 'llm', 'law', 'legal studies', 'constitutional law',
                'corporate law', 'criminal law'
            ]
        }
        
        # Define facility categories
        self.facility_categories = {
            'Academic': [
                'library', 'laboratory', 'computer lab', 'classroom', 'auditorium',
                'seminar hall', 'conference room', 'research center'
            ],
            'Accommodation': [
                'hostel', 'dormitory', 'residence', 'accommodation', 'guest house',
                'boys hostel', 'girls hostel'
            ],
            'Recreation': [
                'sports complex', 'gymnasium', 'playground', 'swimming pool',
                'cafeteria', 'canteen', 'food court', 'student center'
            ],
            'Technology': [
                'wifi', 'internet', 'computer center', 'smart classroom',
                'projector', 'audio visual', 'language lab'
            ],
            'Healthcare': [
                'medical center', 'health center', 'clinic', 'infirmary',
                'first aid', 'counseling center'
            ],
            'Transportation': [
                'bus service', 'transport', 'shuttle', 'parking', 'vehicle'
            ]
        }
    
    def clean_college_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and structure raw college data."""
        try:
            college_name = raw_data.get('name', '')
            self.logger.info(f"Processing data for: {college_name}")
            
            cleaned_data = {
                'name': self.clean_college_name(raw_data.get('name', '')),
                'location': self.clean_location(raw_data.get('location', '')),
                'address': self.clean_address(raw_data.get('address', '')),
                'phone': self.clean_phone_numbers(raw_data.get('phone', [])),
                'email': self.clean_email_addresses(raw_data.get('email', [])),
                'website': self.clean_website_url(raw_data.get('website', '')),
                'courses': self.clean_and_categorize_courses(raw_data.get('courses', [])),
                'facilities': self.clean_and_categorize_facilities(raw_data.get('facilities', [])),
                'description': self.clean_description(raw_data.get('description', '')),
                'established': self.clean_establishment_year(raw_data.get('established', '')),
                'affiliation': self.clean_affiliation(raw_data.get('affiliation', '')),
                'source_url': raw_data.get('source_url', ''),
                'images': self.clean_image_urls(raw_data.get('images', [])),
                'data_quality': self.assess_data_quality(raw_data),
                'processed_at': datetime.now().isoformat()
            }
            
            # Add computed fields
            cleaned_data['college_type'] = self.determine_college_type(cleaned_data)
            cleaned_data['location_info'] = self.extract_location_details(cleaned_data['location'])
            cleaned_data['completeness_score'] = self.calculate_completeness(cleaned_data)
            
            self.logger.info(f"✅ Successfully processed: {cleaned_data['name']}")
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"Error cleaning data for {college_name}: {str(e)}")
            return self.create_minimal_clean_data(raw_data)
    
    def clean_college_name(self, name: str) -> str:
        """Clean and standardize college name."""
        if not name:
            return "Unknown College"
        
        name = clean_text(name)
        
        # Remove common prefixes/suffixes that might be duplicated
        name = re.sub(r'^(college of|institute of|university of)\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(college|institute|university)$', r' \1', name, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Capitalize properly
        if name.isupper() or name.islower():
            name = ' '.join(word.capitalize() for word in name.split())
        
        return name
    
    def clean_location(self, location: str) -> str:
        """Clean and standardize location information."""
        if not location:
            return ""
        
        location = clean_text(location)
        
        # Extract Karnataka-specific locations
        karnataka_cities = [
            'bangalore', 'mysore', 'hubli', 'dharwad', 'belgaum', 'mangalore',
            'gulbarga', 'davangere', 'bellary', 'bijapur', 'shimoga', 'tumkur',
            'raichur', 'bidar', 'hassan', 'udupi', 'chickmagalur'
        ]
        
        location_lower = location.lower()
        for city in karnataka_cities:
            if city in location_lower:
                # Extract surrounding context
                pattern = rf'.{{0,50}}{city}.{{0,50}}'
                match = re.search(pattern, location_lower)
                if match:
                    return clean_text(match.group())
        
        # If no specific city found, return first 100 characters
        return location[:100] if len(location) > 100 else location
    
    def clean_address(self, address: str) -> str:
        """Clean address information."""
        if not address:
            return ""
        
        address = clean_text(address)
        
        # Remove excessive details but keep essential information
        address = re.sub(r'(pin\s*code|pincode|zip)[\s:]*\d{6}', '', address, flags=re.IGNORECASE)
        address = re.sub(r'\s+', ' ', address).strip()
        
        return address[:200] if len(address) > 200 else address
    
    def clean_phone_numbers(self, phone_list: List[str]) -> List[str]:
        """Clean and validate phone numbers."""
        if not phone_list:
            return []
        
        cleaned_phones = []
        seen_phones = set()
        
        for phone in phone_list:
            if isinstance(phone, str):
                normalized = normalize_phone_number(phone)
                if normalized and normalized not in seen_phones:
                    cleaned_phones.append(normalized)
                    seen_phones.add(normalized)
        
        return cleaned_phones[:5]  # Limit to 5 phone numbers
    
    def clean_email_addresses(self, email_list: List[str]) -> List[str]:
        """Clean and validate email addresses."""
        if not email_list:
            return []
        
        cleaned_emails = []
        seen_emails = set()
        
        for email in email_list:
            if isinstance(email, str):
                email = email.strip().lower()
                if validate_email(email) and email not in seen_emails:
                    cleaned_emails.append(email)
                    seen_emails.add(email)
        
        return cleaned_emails[:3]  # Limit to 3 email addresses
    
    def clean_website_url(self, website: str) -> str:
        """Clean and validate website URL."""
        if not website:
            return ""
        
        website = website.strip()
        
        # Add protocol if missing
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        
        # Validate URL structure
        try:
            parsed = urlparse(website)
            if parsed.netloc:
                return website
        except:
            pass
        
        return ""
    
    def clean_and_categorize_courses(self, course_list: List[str]) -> Dict[str, Any]:
        """Clean course list and categorize by type."""
        if not course_list:
            return {"courses": [], "categories": {}, "total_courses": 0}
        
        cleaned_courses = []
        categories = {category: [] for category in self.course_categories.keys()}
        categories['Other'] = []
        
        for course in course_list:
            if isinstance(course, str):
                course = clean_text(course)
                
                # Skip if too short or too long
                if len(course) < 3 or len(course) > 100:
                    continue
                
                cleaned_courses.append(course)
                
                # Categorize course
                course_lower = course.lower()
                categorized = False
                
                for category, keywords in self.course_categories.items():
                    if any(keyword in course_lower for keyword in keywords):
                        categories[category].append(course)
                        categorized = True
                        break
                
                if not categorized:
                    categories['Other'].append(course)
        
        # Remove empty categories
        categories = {k: v for k, v in categories.items() if v}
        
        return {
            "courses": cleaned_courses[:20],  # Limit to 20 courses
            "categories": categories,
            "total_courses": len(cleaned_courses),
            "unique_categories": len(categories)
        }
    
    def clean_and_categorize_facilities(self, facility_list: List[str]) -> Dict[str, Any]:
        """Clean facility list and categorize by type."""
        if not facility_list:
            return {"facilities": [], "categories": {}, "total_facilities": 0}
        
        cleaned_facilities = []
        categories = {category: [] for category in self.facility_categories.keys()}
        categories['Other'] = []
        
        for facility in facility_list:
            if isinstance(facility, str):
                facility = clean_text(facility)
                
                # Skip if too short or too long
                if len(facility) < 3 or len(facility) > 100:
                    continue
                
                cleaned_facilities.append(facility)
                
                # Categorize facility
                facility_lower = facility.lower()
                categorized = False
                
                for category, keywords in self.facility_categories.items():
                    if any(keyword in facility_lower for keyword in keywords):
                        categories[category].append(facility)
                        categorized = True
                        break
                
                if not categorized:
                    categories['Other'].append(facility)
        
        # Remove empty categories
        categories = {k: v for k, v in categories.items() if v}
        
        return {
            "facilities": cleaned_facilities[:15],  # Limit to 15 facilities
            "categories": categories,
            "total_facilities": len(cleaned_facilities),
            "unique_categories": len(categories)
        }
    
    def clean_description(self, description: str) -> str:
        """Clean college description."""
        if not description:
            return ""
        
        description = clean_text(description)
        
        # Remove excessive marketing language
        description = re.sub(r'(click here|visit our website|contact us)', '', description, flags=re.IGNORECASE)
        
        # Limit length
        if len(description) > 500:
            # Try to cut at sentence boundary
            sentences = description.split('.')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence) <= 500:
                    truncated += sentence + "."
                else:
                    break
            description = truncated if truncated else description[:500]
        
        return description
    
    def clean_establishment_year(self, year: str) -> str:
        """Clean and validate establishment year."""
        if not year:
            return ""
        
        # Extract 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', str(year))
        if year_match:
            year_int = int(year_match.group())
            current_year = datetime.now().year
            
            # Validate reasonable range
            if 1800 <= year_int <= current_year:
                return str(year_int)
        
        return ""
    
    def clean_affiliation(self, affiliation: str) -> str:
        """Clean affiliation information."""
        if not affiliation:
            return ""
        
        affiliation = clean_text(affiliation)
        
        # Common university/board abbreviations
        common_affiliations = [
            'aicte', 'ugc', 'naac', 'nba', 'vtu', 'bangalore university',
            'mysore university', 'karnataka university', 'mangalore university'
        ]
        
        affiliation_lower = affiliation.lower()
        for common in common_affiliations:
            if common in affiliation_lower:
                return affiliation
        
        return affiliation[:100] if len(affiliation) <= 100 else ""
    
    def clean_image_urls(self, image_list: List[str]) -> List[str]:
        """Clean and validate image URLs."""
        if not image_list:
            return []
        
        cleaned_images = []
        
        for img_url in image_list:
            if isinstance(img_url, str):
                img_url = img_url.strip()
                
                # Basic URL validation
                if img_url.startswith(('http://', 'https://')) and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    cleaned_images.append(img_url)
        
        return cleaned_images[:5]  # Limit to 5 images
    
    def determine_college_type(self, data: Dict[str, Any]) -> str:
        """Determine the primary type of college based on courses."""
        courses_data = data.get('courses', {})
        if not isinstance(courses_data, dict):
            return "General"
        
        categories = courses_data.get('categories', {})
        
        if not categories:
            return "General"
        
        # Find the category with most courses
        max_courses = 0
        primary_type = "General"
        
        for category, course_list in categories.items():
            if len(course_list) > max_courses:
                max_courses = len(course_list)
                primary_type = category
        
        return primary_type
    
    def extract_location_details(self, location: str) -> Dict[str, str]:
        """Extract detailed location information."""
        location_info = {
            "city": "",
            "district": "",
            "state": "Karnataka",
            "region": ""
        }
        
        if not location:
            return location_info
        
        location_lower = location.lower()
        
        # Karnataka cities and their districts
        city_district_map = {
            'bangalore': 'Bangalore Urban',
            'mysore': 'Mysuru',
            'hubli': 'Dharwad',
            'dharwad': 'Dharwad',
            'belgaum': 'Belagavi',
            'mangalore': 'Dakshina Kannada',
            'gulbarga': 'Kalaburagi',
            'davangere': 'Davanagere',
            'bellary': 'Ballari',
            'bijapur': 'Vijayapura',
            'shimoga': 'Shivamogga',
            'tumkur': 'Tumakuru'
        }
        
        for city, district in city_district_map.items():
            if city in location_lower:
                location_info["city"] = city.title()
                location_info["district"] = district
                break
        
        # Determine region
        if location_info["city"] in ['Bangalore', 'Mysore', 'Tumkur']:
            location_info["region"] = "South Karnataka"
        elif location_info["city"] in ['Hubli', 'Dharwad', 'Belgaum']:
            location_info["region"] = "North Karnataka"
        elif location_info["city"] in ['Mangalore', 'Udupi']:
            location_info["region"] = "Coastal Karnataka"
        
        return location_info
    
    def assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of scraped data."""
        quality_metrics = {
            "completeness": 0.0,
            "accuracy": "medium",
            "freshness": "recent",
            "reliability": "medium"
        }
        
        # Calculate completeness
        required_fields = ['name', 'location', 'courses', 'phone', 'description']
        available_fields = sum(1 for field in required_fields if data.get(field))
        quality_metrics["completeness"] = round(available_fields / len(required_fields), 2)
        
        # Assess accuracy based on source
        source_url = data.get('source_url', '')
        if any(domain in source_url for domain in ['.edu', '.ac.in', '.gov.in']):
            quality_metrics["accuracy"] = "high"
        elif any(domain in source_url for domain in ['careers360', 'collegedunia', 'shiksha']):
            quality_metrics["accuracy"] = "medium"
        else:
            quality_metrics["accuracy"] = "low"
        
        return quality_metrics
    
    def calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate overall data completeness score."""
        fields_weights = {
            'name': 0.2,
            'location': 0.15,
            'phone': 0.15,
            'email': 0.1,
            'courses': 0.2,
            'facilities': 0.1,
            'description': 0.1
        }
        
        score = 0.0
        for field, weight in fields_weights.items():
            if data.get(field):
                if isinstance(data[field], (list, dict)):
                    if len(data[field]) > 0:
                        score += weight
                else:
                    score += weight
        
        return round(score, 2)
    
    def create_minimal_clean_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create minimal clean data structure when processing fails."""
        return {
            'name': raw_data.get('name', 'Unknown College'),
            'location': raw_data.get('location', ''),
            'address': '',
            'phone': [],
            'email': [],
            'website': '',
            'courses': {"courses": [], "categories": {}, "total_courses": 0},
            'facilities': {"facilities": [], "categories": {}, "total_facilities": 0},
            'description': raw_data.get('description', ''),
            'established': '',
            'affiliation': '',
            'source_url': raw_data.get('source_url', ''),
            'images': [],
            'college_type': 'General',
            'location_info': {"city": "", "district": "", "state": "Karnataka", "region": ""},
            'completeness_score': 0.1,
            'data_quality': {"completeness": 0.1, "accuracy": "low", "freshness": "recent", "reliability": "low"},
            'processed_at': datetime.now().isoformat()
        }
"""
Utility Functions
================

Helper functions for logging, text processing, validation, and file operations.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import pandas as pd

def setup_logger(name: str = "college_scraper", level: int = logging.INFO) -> logging.Logger:
    """Set up logger with file and console handlers."""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?()-]', '', text)
    
    # Remove HTML entities
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
        '&#39;': "'", '&nbsp;': ' ', '&hellip;': '...'
    }
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)
    
    # Strip and normalize
    text = text.strip()
    
    return text

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    if not text:
        return []
    
    phone_numbers = []
    
    # Indian phone number patterns
    patterns = [
        r'\+91[\s-]?\d{10}',  # +91 followed by 10 digits
        r'0\d{2,4}[\s-]?\d{6,8}',  # STD codes
        r'\b\d{10}\b',  # 10 digit numbers
        r'\b\d{3}[\s-]\d{3}[\s-]\d{4}\b',  # XXX-XXX-XXXX format
        r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}',  # (XXX) XXX-XXXX format
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean the number
            clean_number = re.sub(r'[^\d+]', '', match)
            if len(clean_number) >= 10:
                phone_numbers.append(match.strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_phones = []
    for phone in phone_numbers:
        if phone not in seen:
            seen.add(phone)
            unique_phones.append(phone)
    
    return unique_phones[:5]  # Limit to 5 numbers

def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    if not text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Clean and validate emails
    valid_emails = []
    for email in emails:
        email = email.lower().strip()
        if validate_email(email):
            valid_emails.append(email)
    
    # Remove duplicates
    return list(set(valid_emails))[:3]  # Limit to 3 emails

def normalize_phone_number(phone: str) -> Optional[str]:
    """Normalize phone number to a standard format."""
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Handle Indian numbers
    if cleaned.startswith('+91'):
        cleaned = cleaned[3:]
    elif cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith('0'):
        cleaned = cleaned[1:]
    
    # Validate length
    if len(cleaned) == 10 and cleaned.isdigit():
        return f"+91-{cleaned[:5]}-{cleaned[5:]}"
    elif len(cleaned) >= 6 and len(cleaned) <= 11 and cleaned.isdigit():
        return cleaned
    
    return None

def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email or '@' not in email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def save_results(data: Dict[str, Any], output_dir: str = "output") -> str:
    """Save processing results to multiple formats."""
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save as JSON
    json_file = os.path.join(output_dir, f"college_data_{timestamp}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save as Excel if colleges data exists
    if data.get('colleges'):
        excel_file = os.path.join(output_dir, f"college_data_{timestamp}.xlsx")
        save_to_excel(data['colleges'], excel_file)
    
    # Save summary report
    summary_file = os.path.join(output_dir, f"summary_report_{timestamp}.txt")
    create_summary_report(data, summary_file)
    
    return json_file

def save_to_excel(colleges_data: List[Dict[str, Any]], file_path: str):
    """Save college data to Excel format."""
    try:
        # Prepare data for Excel
        excel_data = []
        
        for college in colleges_data:
            raw_data = college.get('raw_data', {})
            ai_content = college.get('ai_generated', {}).get('ai_generated_content', {})
            
            row = {
                'ID': college.get('id', ''),
                'College Name': raw_data.get('name', ''),
                'Location': raw_data.get('location', ''),
                'Phone': ', '.join(raw_data.get('phone', [])),
                'Email': ', '.join(raw_data.get('email', [])),
                'Website': raw_data.get('website', ''),
                'Established': raw_data.get('established', ''),
                'College Type': raw_data.get('college_type', ''),
                'Total Courses': raw_data.get('courses', {}).get('total_courses', 0),
                'Total Facilities': raw_data.get('facilities', {}).get('total_facilities', 0),
                'Completeness Score': raw_data.get('completeness_score', 0),
                'AI Overview': ai_content.get('overview', ''),
                'AI Recommendation': ai_content.get('final_recommendation', ''),
                'Source URL': raw_data.get('source_url', ''),
                'Processed At': college.get('processed_at', '')
            }
            excel_data.append(row)
        
        # Create DataFrame and save
        df = pd.DataFrame(excel_data)
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Colleges Summary', index=False)
            
            # Create additional sheets for detailed data
            create_courses_sheet(colleges_data, writer)
            create_facilities_sheet(colleges_data, writer)
        
        print(f"Excel file saved: {file_path}")
        
    except Exception as e:
        print(f"Error saving Excel file: {str(e)}")

def create_courses_sheet(colleges_data: List[Dict[str, Any]], writer):
    """Create detailed courses sheet in Excel."""
    courses_data = []
    
    for college in colleges_data:
        raw_data = college.get('raw_data', {})
        college_name = raw_data.get('name', '')
        courses_info = raw_data.get('courses', {})
        
        if courses_info.get('categories'):
            for category, course_list in courses_info['categories'].items():
                for course in course_list:
                    courses_data.append({
                        'College Name': college_name,
                        'Category': category,
                        'Course': course,
                        'College ID': college.get('id', '')
                    })
    
    if courses_data:
        df_courses = pd.DataFrame(courses_data)
        df_courses.to_excel(writer, sheet_name='Courses Detail', index=False)

def create_facilities_sheet(colleges_data: List[Dict[str, Any]], writer):
    """Create detailed facilities sheet in Excel."""
    facilities_data = []
    
    for college in colleges_data:
        raw_data = college.get('raw_data', {})
        college_name = raw_data.get('name', '')
        facilities_info = raw_data.get('facilities', {})
        
        if facilities_info.get('categories'):
            for category, facility_list in facilities_info['categories'].items():
                for facility in facility_list:
                    facilities_data.append({
                        'College Name': college_name,
                        'Category': category,
                        'Facility': facility,
                        'College ID': college.get('id', '')
                    })
    
    if facilities_data:
        df_facilities = pd.DataFrame(facilities_data)
        df_facilities.to_excel(writer, sheet_name='Facilities Detail', index=False)

def create_summary_report(data: Dict[str, Any], file_path: str):
    """Create a human-readable summary report."""
    
    summary = data.get('summary', {})
    colleges = data.get('colleges', [])
    errors = data.get('errors', [])
    
    report_content = f"""
COLLEGE DATA SCRAPING SUMMARY REPORT
====================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW
--------
Total Colleges Processed: {summary.get('total_colleges', 0)}
Successful Processing: {summary.get('successful_processing', 0)}
Errors Encountered: {len(errors)}
Processing Completed: {summary.get('processing_time', 'Unknown')}

COLLEGE BREAKDOWN
-----------------
"""
    
    if colleges:
        # College type distribution
        college_types = {}
        completeness_scores = []
        
        for college in colleges:
            raw_data = college.get('raw_data', {})
            college_type = raw_data.get('college_type', 'Unknown')
            college_types[college_type] = college_types.get(college_type, 0) + 1
            
            completeness = raw_data.get('completeness_score', 0)
            completeness_scores.append(completeness)
        
        report_content += "\nCollege Types:\n"
        for college_type, count in sorted(college_types.items()):
            report_content += f"  {college_type}: {count}\n"
        
        if completeness_scores:
            avg_completeness = sum(completeness_scores) / len(completeness_scores)
            report_content += f"\nAverage Data Completeness: {avg_completeness:.2f}\n"
        
        # Top colleges by completeness
        sorted_colleges = sorted(
            colleges, 
            key=lambda x: x.get('raw_data', {}).get('completeness_score', 0), 
            reverse=True
        )
        
        report_content += "\nTop 10 Colleges by Data Completeness:\n"
        for i, college in enumerate(sorted_colleges[:10]):
            raw_data = college.get('raw_data', {})
            name = raw_data.get('name', 'Unknown')
            score = raw_data.get('completeness_score', 0)
            report_content += f"  {i+1:2d}. {name[:50]} (Score: {score:.2f})\n"
    
    # Error summary
    if errors:
        report_content += f"\nERRORS ENCOUNTERED ({len(errors)}):\n"
        for i, error in enumerate(errors[:10]):  # Show first 10 errors
            report_content += f"  {i+1}. {error}\n"
        
        if len(errors) > 10:
            report_content += f"  ... and {len(errors) - 10} more errors\n"
    
    report_content += "\n" + "="*50 + "\n"
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Summary report saved: {file_path}")

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config from {config_path}: {str(e)}")
        return {}

def create_sample_config(file_path: str = "config.json"):
    """Create a sample configuration file."""
    sample_config = {
        "scraping": {
            "max_colleges": 50,
            "request_delay": 1.5,
            "timeout": 30,
            "retry_attempts": 3,
            "use_selenium_fallback": True
        },
        "ai_generation": {
            "model": "openai/gpt-3.5-turbo",
            "max_tokens": 2500,
            "temperature": 0.7,
            "rural_student_focus": True
        },
        "output": {
            "save_formats": ["json", "excel", "summary"],
            "output_directory": "output",
            "include_raw_data": True,
            "include_images": False
        },
        "search_terms": [
            "engineering colleges Karnataka",
            "medical colleges Karnataka",
            "arts colleges Karnataka",
            "management colleges Karnataka",
            "universities Karnataka"
        ],
        "target_sources": [
            "https://kea.kar.nic.in/",
            "https://www.careers360.com/colleges/list-of-colleges-in-karnataka",
            "https://www.collegedunia.com/karnataka-colleges"
        ]
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=4)
    
    print(f"Sample configuration created: {file_path}")
    
    return sample_config

def format_rural_student_content(content: Dict[str, Any]) -> str:
    """Format content specifically for rural students in simple language."""
    
    formatted_sections = []
    
    # Overview section
    if content.get('overview'):
        formatted_sections.append(f"📚 ABOUT THIS COLLEGE:\n{content['overview']}\n")
    
    # Key highlights
    if content.get('key_highlights'):
        formatted_sections.append("✨ MAIN HIGHLIGHTS:")
        for i, highlight in enumerate(content['key_highlights'], 1):
            formatted_sections.append(f"  {i}. {highlight}")
        formatted_sections.append("")
    
    # Courses
    if content.get('courses_summary'):
        formatted_sections.append(f"📖 COURSES OFFERED:\n{content['courses_summary']}\n")
    
    # Admission guidance
    if content.get('admission_guidance'):
        formatted_sections.append(f"📝 HOW TO APPLY:\n{content['admission_guidance']}\n")
    
    # Fees information
    if content.get('fees_information'):
        formatted_sections.append(f"💰 FEES & MONEY MATTERS:\n{content['fees_information']}\n")
    
    # Rural student tips
    if content.get('rural_student_tips'):
        formatted_sections.append(f"🌾 SPECIAL TIPS FOR RURAL STUDENTS:\n{content['rural_student_tips']}\n")
    
    # Contact information
    if content.get('contact_summary'):
        formatted_sections.append(f"📞 CONTACT INFORMATION:\n{content['contact_summary']}\n")
    
    # Final recommendation
    if content.get('final_recommendation'):
        formatted_sections.append(f"💡 OUR RECOMMENDATION:\n{content['final_recommendation']}")
    
    return "\n".join(formatted_sections)
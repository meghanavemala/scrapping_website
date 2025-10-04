"""
AI Content Generator using OpenRouter
====================================

Generates rural-student-friendly content from scraped college data
using OpenRouter API with various language models.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import openai
from dotenv import load_dotenv

from utils import setup_logger, clean_text

@dataclass
class CollegeContentTemplate:
    """Template structure for generated college content."""
    overview: str
    key_highlights: List[str]
    courses_summary: str
    admission_guidance: str
    fees_information: str
    placement_prospects: str
    facilities_overview: str
    rural_student_tips: str
    contact_summary: str
    final_recommendation: str

class AIContentGenerator:
    """AI-powered content generator for college information."""
    
    def __init__(self):
        load_dotenv()
        self.logger = setup_logger()
        
        # OpenRouter configuration
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        # Configure OpenAI client for OpenRouter
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
        self.logger.info(f"AI Content Generator initialized with model: {self.model}")
    
    def create_rural_friendly_prompt(self, college_data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for generating rural-student-friendly content."""
        
        prompt = f"""
You are an educational counselor helping rural students understand college information. 
Create comprehensive, easy-to-understand content about this college in simple language.

COLLEGE DATA:
College Name: {college_data.get('name', 'Not provided')}
Location: {college_data.get('location', 'Not provided')}
Courses: {', '.join(college_data.get('courses', []))}
Facilities: {', '.join(college_data.get('facilities', []))}
Established: {college_data.get('established', 'Not provided')}
Description: {college_data.get('description', 'Not provided')}
Phone: {', '.join(college_data.get('phone', []))}
Email: {', '.join(college_data.get('email', []))}
Website: {college_data.get('website', 'Not provided')}

REQUIREMENTS:
1. Write in simple, clear language that rural students can easily understand
2. Explain technical terms and abbreviations
3. Focus on practical information that helps with decision-making
4. Include specific guidance for rural students
5. Mention financial considerations and scholarship opportunities
6. Provide actionable next steps

OUTPUT FORMAT (JSON):
{{
    "overview": "A simple 2-3 sentence introduction about the college",
    "key_highlights": ["3-5 main points about why this college is good"],
    "courses_summary": "Easy explanation of what courses they offer and what students will learn",
    "admission_guidance": "Simple steps on how to apply, what documents needed, important dates",
    "fees_information": "What it might cost and financial help available",
    "placement_prospects": "Job opportunities after graduation in simple terms",
    "facilities_overview": "What facilities are available for students",
    "rural_student_tips": "Specific advice for students from rural areas",
    "contact_summary": "How to contact the college with phone numbers and addresses",
    "final_recommendation": "Overall assessment and recommendation for rural students"
}}

Generate comprehensive, helpful content that empowers rural students to make informed decisions.
"""
        return prompt
    
    async def generate_content_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Generate content with retry mechanism."""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert educational counselor helping rural students understand college information. Respond in valid JSON format."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2500,
                    temperature=0.7,
                    top_p=0.9,
                )
                
                content = response.choices[0].message.content.strip()
                
                # Clean up the response to ensure it's valid JSON
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                # Validate JSON
                try:
                    json.loads(content)
                    return content
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON response on attempt {attempt + 1}")
                    if attempt == max_retries - 1:
                        return self.create_fallback_content(prompt)
                
            except Exception as e:
                self.logger.error(f"API error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return self.create_fallback_content(prompt)
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    def create_fallback_content(self, prompt: str) -> str:
        """Create fallback content when AI generation fails."""
        fallback = {
            "overview": "This college offers various educational programs for students.",
            "key_highlights": [
                "Educational institution in Karnataka",
                "Offers multiple courses",
                "Has basic facilities for students"
            ],
            "courses_summary": "The college offers various undergraduate and postgraduate courses. Students can choose based on their interests and career goals.",
            "admission_guidance": "Contact the college directly for admission information. Visit their office or call the provided phone numbers.",
            "fees_information": "Fee structure varies by course. Contact the college for detailed fee information and scholarship opportunities.",
            "placement_prospects": "The college helps students find job opportunities after graduation. Career guidance is provided.",
            "facilities_overview": "Basic educational facilities are available including classrooms, library, and computer labs.",
            "rural_student_tips": "Rural students should prepare all documents in advance, learn about hostel facilities, and ask about financial assistance programs.",
            "contact_summary": "Contact the college through the provided phone numbers and email addresses for more information.",
            "final_recommendation": "This college can be a good option for students. Visit the campus and talk to current students before making a decision."
        }
        return json.dumps(fallback)
    
    async def generate_college_content(self, college_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive AI content for a college."""
        try:
            college_name = college_data.get('name', 'Unknown College')
            self.logger.info(f"Generating AI content for: {college_name}")
            
            # Create the prompt
            prompt = self.create_rural_friendly_prompt(college_data)
            
            # Generate content
            ai_response = await self.generate_content_with_retry(prompt)
            
            if ai_response:
                try:
                    generated_content = json.loads(ai_response)
                    
                    # Enhance with additional processing
                    enhanced_content = self.enhance_generated_content(
                        generated_content, 
                        college_data
                    )
                    
                    self.logger.info(f"✅ Successfully generated content for: {college_name}")
                    return enhanced_content
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON parsing error for {college_name}: {str(e)}")
                    fallback_content = json.loads(self.create_fallback_content(prompt))
                    return self.enhance_generated_content(fallback_content, college_data)
            else:
                self.logger.error(f"Failed to generate content for: {college_name}")
                fallback_content = json.loads(self.create_fallback_content(prompt))
                return self.enhance_generated_content(fallback_content, college_data)
                
        except Exception as e:
            self.logger.error(f"Critical error generating content for {college_name}: {str(e)}")
            fallback_content = json.loads(self.create_fallback_content(""))
            return self.enhance_generated_content(fallback_content, college_data)
    
    def enhance_generated_content(self, ai_content: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance AI-generated content with additional structured information."""
        
        enhanced = {
            "ai_generated_content": ai_content,
            "structured_data": {
                "basic_info": {
                    "name": original_data.get('name', ''),
                    "location": original_data.get('location', ''),
                    "established": original_data.get('established', ''),
                    "website": original_data.get('website', ''),
                    "source_url": original_data.get('source_url', '')
                },
                "contact_details": {
                    "phones": original_data.get('phone', []),
                    "emails": original_data.get('email', []),
                    "address": original_data.get('address', '')
                },
                "academic_info": {
                    "courses_offered": original_data.get('courses', []),
                    "total_courses": len(original_data.get('courses', [])),
                    "departments": self.extract_departments(original_data.get('courses', []))
                },
                "facilities": {
                    "available_facilities": original_data.get('facilities', []),
                    "total_facilities": len(original_data.get('facilities', [])),
                    "categorized_facilities": self.categorize_facilities(original_data.get('facilities', []))
                },
                "multimedia": {
                    "images": original_data.get('images', []),
                    "total_images": len(original_data.get('images', []))
                }
            },
            "rural_student_specific": {
                "accessibility_score": self.calculate_accessibility_score(original_data),
                "financial_considerations": self.analyze_financial_aspects(original_data),
                "support_systems": self.identify_support_systems(original_data),
                "practical_tips": self.generate_practical_tips(original_data)
            },
            "content_quality": {
                "completeness_score": self.calculate_completeness_score(original_data),
                "information_richness": len([v for v in original_data.values() if v]),
                "data_reliability": "medium"  # Based on source types
            }
        }
        
        return enhanced
    
    def extract_departments(self, courses: List[str]) -> List[str]:
        """Extract department names from course list."""
        departments = set()
        dept_keywords = {
            'Engineering': ['engineering', 'btech', 'mtech', 'be', 'me'],
            'Medical': ['medical', 'mbbs', 'md', 'nursing', 'pharmacy'],
            'Management': ['mba', 'management', 'business', 'bba'],
            'Arts': ['ba', 'ma', 'arts', 'literature', 'english'],
            'Science': ['bsc', 'msc', 'science', 'physics', 'chemistry', 'biology'],
            'Commerce': ['bcom', 'mcom', 'commerce', 'accounting', 'finance'],
            'Computer Science': ['computer', 'it', 'software', 'bca', 'mca'],
            'Law': ['law', 'llb', 'llm', 'legal']
        }
        
        for course in courses:
            course_lower = course.lower()
            for dept, keywords in dept_keywords.items():
                if any(keyword in course_lower for keyword in keywords):
                    departments.add(dept)
        
        return list(departments)
    
    def categorize_facilities(self, facilities: List[str]) -> Dict[str, List[str]]:
        """Categorize facilities into different types."""
        categories = {
            'Academic': [],
            'Accommodation': [],
            'Recreation': [],
            'Technology': [],
            'Healthcare': [],
            'Other': []
        }
        
        category_keywords = {
            'Academic': ['library', 'lab', 'classroom', 'auditorium', 'seminar'],
            'Accommodation': ['hostel', 'accommodation', 'dormitory', 'residence'],
            'Recreation': ['sports', 'gym', 'playground', 'canteen', 'cafeteria'],
            'Technology': ['computer', 'wifi', 'internet', 'projector', 'smart'],
            'Healthcare': ['medical', 'health', 'clinic', 'infirmary', 'first aid']
        }
        
        for facility in facilities:
            facility_lower = facility.lower()
            categorized = False
            
            for category, keywords in category_keywords.items():
                if any(keyword in facility_lower for keyword in keywords):
                    categories[category].append(facility)
                    categorized = True
                    break
            
            if not categorized:
                categories['Other'].append(facility)
        
        return {k: v for k, v in categories.items() if v}  # Remove empty categories
    
    def calculate_accessibility_score(self, college_data: Dict[str, Any]) -> int:
        """Calculate accessibility score for rural students (1-10)."""
        score = 5  # Base score
        
        # Bonus for contact information
        if college_data.get('phone'):
            score += 1
        if college_data.get('email'):
            score += 1
        
        # Bonus for location information
        if college_data.get('location'):
            score += 1
        
        # Bonus for comprehensive course information
        if len(college_data.get('courses', [])) > 5:
            score += 1
        
        # Bonus for facilities
        if len(college_data.get('facilities', [])) > 3:
            score += 1
        
        return min(score, 10)
    
    def analyze_financial_aspects(self, college_data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze financial considerations for rural students."""
        return {
            "fee_transparency": "Contact college for detailed fee structure",
            "scholarship_potential": "Check for government and merit-based scholarships",
            "hidden_costs": "Ask about additional fees for labs, library, and activities",
            "payment_options": "Inquire about installment payment options"
        }
    
    def identify_support_systems(self, college_data: Dict[str, Any]) -> List[str]:
        """Identify support systems available for rural students."""
        support_systems = [
            "Contact college counselor for guidance",
            "Look for senior student mentorship programs",
            "Check for language support if needed"
        ]
        
        facilities = college_data.get('facilities', [])
        for facility in facilities:
            if 'hostel' in facility.lower():
                support_systems.append("Hostel accommodation available")
            if 'transport' in facility.lower():
                support_systems.append("Transportation services may be available")
        
        return support_systems
    
    def generate_practical_tips(self, college_data: Dict[str, Any]) -> List[str]:
        """Generate practical tips for rural students."""
        tips = [
            "Visit the college campus before admission if possible",
            "Prepare all documents in advance (10th, 12th marks, certificates)",
            "Learn basic English if courses are taught in English",
            "Budget for living expenses beyond tuition fees",
            "Connect with other students from your region"
        ]
        
        if college_data.get('phone'):
            tips.append("Call the college directly to clarify any doubts")
        
        if college_data.get('website'):
            tips.append("Check the college website regularly for updates")
        
        return tips
    
    def calculate_completeness_score(self, college_data: Dict[str, Any]) -> float:
        """Calculate how complete the college data is (0-1)."""
        required_fields = ['name', 'location', 'courses', 'phone', 'description']
        available_fields = sum(1 for field in required_fields if college_data.get(field))
        
        return round(available_fields / len(required_fields), 2)
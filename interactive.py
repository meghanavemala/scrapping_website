"""
Interactive College Information Tool
===================================

Takes college names as input from user and displays results in terminal.
"""

import asyncio
import os
import sys
from typing import List, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from scraper import CollegeScraper
from ai_generator import AIContentGenerator
from data_processor import DataProcessor
from utils import setup_logger, format_rural_student_content
from college_database import find_college_by_name, get_all_college_names, KARNATAKA_COLLEGES

class InteractiveCollegeInfo:
    """Interactive college information system with terminal interface."""
    
    def __init__(self):
        load_dotenv()
        self.logger = setup_logger()
        
        # Initialize components
        self.scraper = CollegeScraper()
        self.ai_generator = AIContentGenerator()
        self.data_processor = DataProcessor()
        
        print("🎓 Interactive College Information Tool")
        print("=" * 50)
        print("✅ System initialized successfully!")
        print()
        self.show_available_colleges()
    
    def show_available_colleges(self):
        """Show list of available colleges in database."""
        print("💡 Popular Karnataka Colleges (we have detailed info for these):")
        college_names = get_all_college_names()
        for i, name in enumerate(college_names[:10], 1):  # Show first 10
            print(f"   {i:2d}. {name}")
        
        if len(college_names) > 10:
            print(f"   ... and {len(college_names) - 10} more!")
        
        print("\n🔍 You can also search for any other college name!")
        print()
    
    def get_user_input(self) -> List[str]:
        """Get college names from user input."""
        print("📝 Enter college names to search for:")
        print("   (You can enter multiple colleges separated by commas)")
        print("   (Type 'list' to see available colleges)")
        print("   (Type 'quit' or 'exit' to stop)")
        print()
        
        while True:
            user_input = input("🏫 College name(s): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                return []
            
            if user_input.lower() == 'list':
                print()
                self.show_available_colleges()
                continue
            
            if not user_input:
                print("❌ Please enter at least one college name.")
                continue
            
            # Split by comma and clean up
            college_names = [name.strip() for name in user_input.split(',')]
            college_names = [name for name in college_names if name]  # Remove empty strings
            
            if college_names:
                return college_names
            else:
                print("❌ Please enter valid college names.")
    
    async def search_college_by_name(self, college_name: str) -> List[Dict[str, Any]]:
        """Search for a specific college by name."""
        print(f"🔍 Searching for: {college_name}")
        
        # First, check if it's in our known colleges database
        known_college = find_college_by_name(college_name)
        if known_college:
            print(f"✅ Found in database: {known_college['official_name']}")
            print(f"   📄 Official website: {known_college['website']}")
            
            # Scrape the known college website
            try:
                scraped_data = await self.scraper.scrape_college_from_url(known_college['website'])
                if scraped_data:
                    # Enhance with database information
                    scraped_data.update({
                        'name': known_college['official_name'],
                        'location': known_college['location'],
                        'established': known_college['established'],
                        'affiliation': known_college['affiliation'],
                        'college_type': known_college['type']
                    })
                    return [scraped_data]
                else:
                    print(f"   ⚠️ Could not scrape website, using database info only")
                    return [known_college]
            except Exception as e:
                print(f"   ⚠️ Website access failed, using database info only")
                return [known_college]
        
        # If not in database, try general search
        print("   📡 Searching online...")
        
        # Create search terms for the specific college
        search_terms = [
            f"{college_name} Karnataka",
            f"{college_name} college Karnataka"
        ]
        
        # Try to find college URLs
        all_urls = set()
        
        # Search using modified terms
        for term in search_terms[:1]:  # Limit to avoid too many requests
            try:
                urls = await self.scraper.search_colleges_google(term, max_results=3)
                all_urls.update(urls)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                self.logger.error(f"Search error for {term}: {str(e)}")
                continue
        
        # If no URLs found, try manual URL construction
        if not all_urls:
            # Try common college URL patterns
            college_name_clean = college_name.lower().replace(' ', '').replace('college', '').replace('university', '').replace('institute', '')
            potential_urls = [
                f"https://{college_name_clean}.ac.in/",
                f"https://www.{college_name_clean}.edu/",
                f"https://{college_name_clean}.edu.in/",
            ]
            all_urls.update(potential_urls)
        
        # Scrape the found URLs
        college_data = []
        for url in list(all_urls)[:3]:  # Limit to 3 URLs per college
            try:
                print(f"   📄 Checking: {url}")
                html = await self.scraper.fetch_url(self.scraper.session, url)
                if html:
                    college_info = self.scraper.extract_college_info_from_html(html, url)
                    if college_info.get('name') or college_info.get('description'):
                        college_data.append(college_info)
                        print(f"   ✅ Found data from: {url}")
                        break  # Found good data, stop searching
                    else:
                        print(f"   ⚠️ No useful data from: {url}")
                else:
                    print(f"   ❌ Could not access: {url}")
            except Exception as e:
                print(f"   ❌ Error accessing {url}: {str(e)}")
                continue
        
        return college_data
    
    def display_college_info(self, college_data: Dict[str, Any], ai_content: Dict[str, Any] = None):
        """Display college information in a formatted way."""
        
        # Handle both database-only and full scraped data
        if 'official_name' in college_data:  # Database entry
            raw_data = college_data
            ai_generated = {}
        else:  # Scraped data
            raw_data = college_data
            ai_generated = ai_content.get('ai_generated_content', {}) if ai_content else {}
        
        print("\n" + "="*60)
        print(f"🏫 {raw_data.get('name', raw_data.get('official_name', 'Unknown College'))}")
        print("="*60)
        
        # Basic Information
        if raw_data.get('location'):
            print(f"📍 Location: {raw_data['location']}")
        
        if raw_data.get('established'):
            print(f"📅 Established: {raw_data['established']}")
        
        if raw_data.get('type'):
            print(f"🏛️ Type: {raw_data['type']}")
        
        if raw_data.get('affiliation'):
            print(f"🔗 Affiliation: {raw_data['affiliation']}")
        
        if raw_data.get('website'):
            print(f"🌐 Website: {raw_data['website']}")
        
        # Contact Information
        if raw_data.get('phone'):
            phones = raw_data['phone'] if isinstance(raw_data['phone'], list) else [raw_data['phone']]
            print(f"📞 Phone: {', '.join(phones[:2])}")  # Show first 2 numbers
        
        if raw_data.get('email'):
            emails = raw_data['email'] if isinstance(raw_data['email'], list) else [raw_data['email']]
            print(f"✉️ Email: {', '.join(emails[:2])}")  # Show first 2 emails
        
        print()
        
        # AI Generated Content
        if ai_generated.get('overview'):
            print("📚 OVERVIEW:")
            print(f"   {ai_generated['overview']}")
            print()
        
        if ai_generated.get('key_highlights'):
            print("✨ KEY HIGHLIGHTS:")
            for i, highlight in enumerate(ai_generated['key_highlights'][:5], 1):
                print(f"   {i}. {highlight}")
            print()
        
        # Courses Information
        courses_info = raw_data.get('courses', {})
        if isinstance(courses_info, dict) and courses_info.get('categories'):
            print("📖 COURSES OFFERED:")
            for category, course_list in list(courses_info['categories'].items())[:3]:  # Show top 3 categories
                if course_list:
                    print(f"   🔹 {category}: {', '.join(course_list[:3])}")  # Show first 3 courses
            print()
        
        # Facilities
        facilities_info = raw_data.get('facilities', {})
        if isinstance(facilities_info, dict) and facilities_info.get('facilities'):
            print("🏢 FACILITIES:")
            facilities = facilities_info['facilities'][:6]  # Show first 6 facilities
            for facility in facilities:
                print(f"   • {facility}")
            print()
        
        # Rural Student Specific Information
        if ai_generated.get('rural_student_tips'):
            print("🌾 TIPS FOR RURAL STUDENTS:")
            print(f"   {ai_generated['rural_student_tips']}")
            print()
        
        if ai_generated.get('admission_guidance'):
            print("📝 ADMISSION GUIDANCE:")
            print(f"   {ai_generated['admission_guidance']}")
            print()
        
        if ai_generated.get('final_recommendation'):
            print("💡 RECOMMENDATION:")
            print(f"   {ai_generated['final_recommendation']}")
            print()
        
        # Data Quality Score
        completeness = raw_data.get('completeness_score', 0)
        print(f"📊 Data Completeness: {completeness:.1%}")
        print("="*60)
    
    async def process_college(self, college_name: str):
        """Process a single college and display results."""
        try:
            # Search for college data
            college_data_list = await self.search_college_by_name(college_name)
            
            if not college_data_list:
                print(f"❌ No data found for '{college_name}'")
                print("💡 Try:")
                print("   - Using the full official name")
                print("   - Adding 'college' or 'university' to the name")
                print("   - Checking the spelling")
                return
            
            # Process the first (best) result
            raw_college_data = college_data_list[0]
            
            print(f"🔄 Processing data for '{college_name}'...")
            
            # Clean and process the data
            clean_data = self.data_processor.clean_college_data(raw_college_data)
            
            # Generate AI content
            print("🤖 Generating AI content...")
            ai_content = await self.ai_generator.generate_college_content(clean_data)
            
            # Display the results
            self.display_college_info(clean_data, ai_content)
            
        except Exception as e:
            print(f"❌ Error processing '{college_name}': {str(e)}")
            self.logger.error(f"Error processing {college_name}: {str(e)}")
    
    async def run_interactive_mode(self):
        """Main interactive loop."""
        print("🚀 Ready to search for colleges!")
        print("💡 Example: 'RV College of Engineering', 'IISc Bangalore', 'Mysore University'")
        print()
        
        while True:
            college_names = self.get_user_input()
            
            if not college_names:  # User wants to quit
                print("👋 Thank you for using College Information Tool!")
                break
            
            print(f"\n🔍 Processing {len(college_names)} college(s)...")
            print("-" * 50)
            
            for i, college_name in enumerate(college_names, 1):
                print(f"\n[{i}/{len(college_names)}] Processing: {college_name}")
                await self.process_college(college_name)
                
                # Small delay between colleges
                if i < len(college_names):
                    await asyncio.sleep(1)
            
            print("\n" + "🎯" * 20)
            print("✅ All colleges processed!")
            print("🔄 You can search for more colleges or type 'quit' to exit.")
            print()

async def main():
    """Main entry point for interactive mode."""
    try:
        tool = InteractiveCollegeInfo()
        await tool.run_interactive_mode()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using College Information Tool!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("💡 Please check your internet connection and API key.")

if __name__ == "__main__":
    asyncio.run(main())
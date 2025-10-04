"""
Simple Interactive College Information Tool
==========================================

User-friendly version that works reliably with database and AI generation.
"""

import asyncio
import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from ai_generator import AIContentGenerator
from utils import setup_logger
from college_database import find_college_by_name, get_all_college_names, KARNATAKA_COLLEGES

class SimpleCollegeInfo:
    """Simple reliable college information system."""
    
    def __init__(self):
        load_dotenv()
        self.logger = setup_logger()
        
        # Initialize AI generator
        try:
            self.ai_generator = AIContentGenerator()
            self.ai_available = True
        except Exception as e:
            print(f"⚠️ AI Generation unavailable: {str(e)}")
            self.ai_available = False
        
        self.show_welcome()
    
    def show_welcome(self):
        """Show welcome message and available colleges."""
        print("🎓 Karnataka College Information Tool")
        print("=" * 50)
        print("✅ System ready!")
        if self.ai_available:
            print("🤖 AI content generation: Available")
        else:
            print("📋 Basic database info: Available")
        print()
        
        print("💡 Popular Karnataka Colleges (we have detailed info):")
        college_names = get_all_college_names()
        for i, name in enumerate(college_names[:12], 1):
            print(f"   {i:2d}. {name}")
        
        if len(college_names) > 12:
            print(f"   ... and {len(college_names) - 12} more!")
        print()
    
    def get_user_input(self) -> List[str]:
        """Get college names from user input."""
        print("📝 Enter college name to search:")
        print("   (Type 'list' to see all available colleges)")
        print("   (Type 'quit' or 'exit' to stop)")
        print()
        
        while True:
            user_input = input("🏫 College name: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                return []
            
            if user_input.lower() == 'list':
                self.show_all_colleges()
                continue
            
            if not user_input:
                print("❌ Please enter a college name.")
                continue
            
            return [user_input]
    
    def show_all_colleges(self):
        """Show all available colleges in database."""
        print("\n📚 All Available Colleges:")
        print("-" * 40)
        
        colleges_by_type = {}
        for key, info in KARNATAKA_COLLEGES.items():
            college_type = info['type']
            if college_type not in colleges_by_type:
                colleges_by_type[college_type] = []
            colleges_by_type[college_type].append(info['official_name'])
        
        for college_type, colleges in colleges_by_type.items():
            print(f"\n🔹 {college_type}:")
            for college in sorted(colleges):
                print(f"   • {college}")
        print()
    
    async def search_and_display(self, college_name: str):
        """Search for college and display information."""
        print(f"\n🔍 Searching for: {college_name}")
        print("-" * 50)
        
        # Look up in database
        college_info = find_college_by_name(college_name)
        
        if not college_info:
            print("❌ College not found in our database.")
            print("\n💡 Suggestions:")
            print("   - Check the spelling")
            print("   - Try a shorter name (e.g., 'IISc' instead of 'Indian Institute of Science')")
            print("   - Type 'list' to see all available colleges")
            return False
        
        # Display basic information
        self.display_basic_info(college_info)
        
        # Generate and display AI content if available
        if self.ai_available:
            print("🤖 Generating detailed AI content...")
            try:
                ai_content = await self.ai_generator.generate_college_content(college_info)
                self.display_ai_content(ai_content)
            except Exception as e:
                print(f"⚠️ AI generation failed: {str(e)}")
                print("📋 Showing database information only.")
        
        return True
    
    def display_basic_info(self, college_info: Dict[str, Any]):
        """Display basic college information from database."""
        print("\n" + "="*60)
        print(f"🏫 {college_info['official_name']}")
        print("="*60)
        
        print(f"📍 Location: {college_info['location']}")
        print(f"📅 Established: {college_info['established']}")
        print(f"🏛️ Type: {college_info['type']}")
        print(f"🔗 Affiliation: {college_info['affiliation']}")
        print(f"🌐 Website: {college_info['website']}")
        print()
    
    def display_ai_content(self, ai_content: Dict[str, Any]):
        """Display AI-generated content."""
        content = ai_content.get('ai_generated_content', {})
        
        if content.get('overview'):
            print("📚 OVERVIEW:")
            print(f"   {content['overview']}")
            print()
        
        if content.get('key_highlights'):
            print("✨ KEY HIGHLIGHTS:")
            for i, highlight in enumerate(content['key_highlights'][:5], 1):
                print(f"   {i}. {highlight}")
            print()
        
        if content.get('admission_guidance'):
            print("📝 ADMISSION GUIDANCE:")
            print(f"   {content['admission_guidance']}")
            print()
        
        if content.get('rural_student_tips'):
            print("🌾 TIPS FOR RURAL STUDENTS:")
            print(f"   {content['rural_student_tips']}")
            print()
        
        if content.get('final_recommendation'):
            print("💡 RECOMMENDATION:")
            print(f"   {content['final_recommendation']}")
            print()
        
        print("="*60)
    
    async def run(self):
        """Main interactive loop."""
        print("🚀 Ready to help you find college information!")
        print()
        
        while True:
            college_names = self.get_user_input()
            
            if not college_names:
                print("\n👋 Goodbye! Thanks for using the College Information Tool!")
                break
            
            for college_name in college_names:
                success = await self.search_and_display(college_name)
                
                if success:
                    print("\n🎯" + "="*59)
                    print("✅ Information displayed successfully!")
                    print("🔄 You can search for another college or type 'quit' to exit.")
                    print("="*60)
                else:
                    print("\n💭 Try another search or type 'list' to see available colleges.")
                
                print()

async def main():
    """Main entry point."""
    tool = SimpleCollegeInfo()
    await tool.run()

if __name__ == "__main__":
    asyncio.run(main())
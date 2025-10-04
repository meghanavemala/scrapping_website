"""
Example Usage Scripts
====================

Various examples showing how to use the college scraping system.
"""

import asyncio
import json
from main import CollegeInfoProcessor

async def example_basic_usage():
    """Basic usage example - simple college search."""
    print("🎓 Basic College Search Example")
    print("=" * 40)
    
    processor = CollegeInfoProcessor()
    
    # Simple search for engineering colleges
    results = await processor.process_colleges(
        search_terms=["engineering colleges Karnataka"],
        max_colleges=10
    )
    
    print(f"✅ Found {len(results['colleges'])} colleges")
    print(f"⚠️ Errors: {len(results['errors'])}")
    
    # Display first college as example
    if results['colleges']:
        first_college = results['colleges'][0]
        name = first_college['raw_data'].get('name', 'Unknown')
        location = first_college['raw_data'].get('location', 'Unknown')
        print(f"\n📍 Example College: {name}")
        print(f"📍 Location: {location}")

async def example_specific_colleges():
    """Example with specific college URLs."""
    print("\n🎓 Specific Colleges Example")
    print("=" * 40)
    
    processor = CollegeInfoProcessor()
    
    # Specific well-known colleges
    specific_urls = [
        "https://iisc.ac.in/",
        "https://bmsce.ac.in/",
        "https://rvce.edu.in/",
        "https://msrit.edu/",
        "https://sit.ac.in/"
    ]
    
    results = await processor.process_colleges(
        specific_urls=specific_urls,
        max_colleges=5
    )
    
    print(f"✅ Processed {len(results['colleges'])} specific colleges")
    
    # Show AI-generated content for first college
    if results['colleges']:
        first_college = results['colleges'][0]
        ai_content = first_college.get('ai_generated', {}).get('ai_generated_content', {})
        
        if ai_content.get('overview'):
            print(f"\n🤖 AI-Generated Overview:")
            print(ai_content['overview'])

async def example_medical_colleges():
    """Example focused on medical colleges."""
    print("\n🏥 Medical Colleges Example")
    print("=" * 40)
    
    processor = CollegeInfoProcessor()
    
    medical_search_terms = [
        "medical colleges Karnataka MBBS",
        "dental colleges Karnataka BDS",
        "nursing colleges Karnataka",
        "pharmacy colleges Karnataka",
        "physiotherapy colleges Karnataka"
    ]
    
    results = await processor.process_colleges(
        search_terms=medical_search_terms,
        max_colleges=15
    )
    
    # Analyze medical college types
    medical_types = {}
    for college in results['colleges']:
        courses = college['raw_data'].get('courses', {}).get('categories', {})
        if 'Medical' in courses:
            college_name = college['raw_data'].get('name', 'Unknown')
            medical_courses = courses['Medical']
            medical_types[college_name] = medical_courses
    
    print(f"🏥 Found {len(medical_types)} colleges with medical courses:")
    for name, courses in list(medical_types.items())[:5]:  # Show first 5
        print(f"  📚 {name}: {', '.join(courses[:2])}")

async def example_rural_student_focus():
    """Example showcasing rural student features."""
    print("\n🌾 Rural Student Focus Example")
    print("=" * 40)
    
    processor = CollegeInfoProcessor()
    
    # Search for colleges with good accessibility
    results = await processor.process_colleges(
        search_terms=["affordable colleges Karnataka", "government colleges Karnataka"],
        max_colleges=8
    )
    
    # Find colleges with good rural student support
    rural_friendly = []
    for college in results['colleges']:
        ai_content = college.get('ai_generated', {})
        rural_support = ai_content.get('rural_student_specific', {})
        accessibility_score = rural_support.get('accessibility_score', 0)
        
        if accessibility_score >= 7:  # High accessibility
            rural_friendly.append({
                'name': college['raw_data'].get('name', 'Unknown'),
                'location': college['raw_data'].get('location', 'Unknown'),
                'score': accessibility_score,
                'tips': ai_content.get('ai_generated_content', {}).get('rural_student_tips', '')
            })
    
    print(f"🌾 Found {len(rural_friendly)} rural-friendly colleges:")
    for college in rural_friendly:
        print(f"  ⭐ {college['name']} (Score: {college['score']})")
        if college['tips']:
            print(f"     💡 Tip: {college['tips'][:100]}...")

async def example_data_analysis():
    """Example showing data analysis capabilities."""
    print("\n📊 Data Analysis Example")
    print("=" * 40)
    
    processor = CollegeInfoProcessor()
    
    results = await processor.process_colleges(
        search_terms=["colleges Karnataka"],
        max_colleges=20
    )
    
    # Analyze the data
    college_types = {}
    locations = {}
    total_courses = 0
    total_facilities = 0
    
    for college in results['colleges']:
        raw_data = college['raw_data']
        
        # College types
        college_type = raw_data.get('college_type', 'Unknown')
        college_types[college_type] = college_types.get(college_type, 0) + 1
        
        # Locations
        location_info = raw_data.get('location_info', {})
        city = location_info.get('city', 'Unknown')
        locations[city] = locations.get(city, 0) + 1
        
        # Course and facility counts
        courses_data = raw_data.get('courses', {})
        facilities_data = raw_data.get('facilities', {})
        total_courses += courses_data.get('total_courses', 0)
        total_facilities += facilities_data.get('total_facilities', 0)
    
    print("📈 Analysis Results:")
    print(f"  📚 Total courses found: {total_courses}")
    print(f"  🏢 Total facilities found: {total_facilities}")
    
    print(f"\n🏫 College Types:")
    for ctype, count in sorted(college_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ctype}: {count}")
    
    print(f"\n📍 Top Locations:")
    for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {location}: {count}")

async def example_export_formats():
    """Example showing different export formats."""
    print("\n💾 Export Formats Example")
    print("=" * 40)
    
    processor = CollegeInfoProcessor()
    
    results = await processor.process_colleges(
        search_terms=["top colleges Karnataka"],
        max_colleges=5
    )
    
    print("📄 Files created in output/ directory:")
    
    # The results are automatically saved by the processor
    # Let's show what files should be created
    from datetime import datetime
    timestamp_format = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    expected_files = [
        f"college_data_{timestamp_format}.json",
        f"college_data_{timestamp_format}.xlsx", 
        f"summary_report_{timestamp_format}.txt"
    ]
    
    for filename in expected_files:
        print(f"  📁 {filename}")
    
    print("\n📊 Excel file contains:")
    print("  🔹 Colleges Summary sheet")
    print("  🔹 Courses Detail sheet") 
    print("  🔹 Facilities Detail sheet")

def display_sample_ai_content():
    """Display sample AI-generated content."""
    print("\n🤖 Sample AI-Generated Content")
    print("=" * 40)
    
    sample_content = {
        "overview": "RV College of Engineering is a well-known engineering college in Bangalore. It has been teaching students since 1963 and offers many engineering courses.",
        "key_highlights": [
            "One of the oldest engineering colleges in Karnataka",
            "Good placement record with top companies visiting",
            "Strong alumni network across the world",
            "Modern labs and library facilities"
        ],
        "rural_student_tips": "Rural students should prepare for English-medium classes. The college has hostels available. Apply early for government quotas and scholarships. Contact seniors from your district for guidance.",
        "final_recommendation": "This is a good college for engineering students. Rural students will find good support systems. The fees are reasonable compared to private colleges. Visit the campus before admission to understand the environment."
    }
    
    from utils import format_rural_student_content
    formatted = format_rural_student_content(sample_content)
    print(formatted)

async def main():
    """Run all examples."""
    print("🚀 College Scraper Examples")
    print("=" * 50)
    
    # Run examples
    await example_basic_usage()
    await example_specific_colleges()
    await example_medical_colleges()
    await example_rural_student_focus()
    await example_data_analysis()
    await example_export_formats()
    display_sample_ai_content()
    
    print("\n✅ All examples completed!")
    print("💡 Check the output/ directory for generated files")
    print("📝 Check logs/ directory for detailed execution logs")

if __name__ == "__main__":
    # Make sure you have set up your .env file with OPENROUTER_API_KEY
    print("⚠️  Make sure you have:")
    print("   1. Set OPENROUTER_API_KEY in .env file")
    print("   2. Installed all requirements: pip install -r requirements.txt")
    print("   3. Good internet connection for scraping")
    print("\nStarting examples in 3 seconds...")
    
    import time
    time.sleep(3)
    
    asyncio.run(main())
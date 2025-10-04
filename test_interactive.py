"""
Quick Test Script for Interactive College Tool
==============================================
"""

import asyncio
from interactive import InteractiveCollegeInfo

async def test_known_college():
    """Test with a known college from our database."""
    
    tool = InteractiveCollegeInfo()
    
    # Test with RV College of Engineering (known college)
    print("Testing with 'RV College of Engineering'...")
    results = await tool.search_college_by_name("RV College of Engineering")
    
    if results:
        print(f"\n✅ Found {len(results)} result(s)")
        tool.display_college_info(results[0])
    else:
        print("❌ No results found")
    
    print("\n" + "="*60)
    
    # Test with partial name
    print("Testing with 'bit bangalore'...")
    results = await tool.search_college_by_name("bit bangalore")
    
    if results:
        print(f"\n✅ Found {len(results)} result(s)")
        tool.display_college_info(results[0])
    else:
        print("❌ No results found")

if __name__ == "__main__":
    print("🧪 Testing Interactive College Tool")
    print("=" * 50)
    
    asyncio.run(test_known_college())
    
    print("\n✅ Test completed! If you see college information above, the system is working!")
    print("💡 Now try running: python interactive.py")
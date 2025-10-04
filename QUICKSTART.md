# College Scraper Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get OpenRouter API Key
1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up and get your API key
3. Edit `.env` file and add your key:
```
OPENROUTER_API_KEY=your_actual_key_here
```

### Step 3: Run the Scraper
```bash
python main.py
```

That's it! The scraper will:
- 🔍 Search for colleges in Karnataka
- 📊 Extract detailed information
- 🤖 Generate AI-enhanced content
- 💾 Save results to output/ folder

## 📁 What You'll Get

**JSON File** (`college_data_[timestamp].json`)
- Complete structured data
- Raw scraped information
- AI-generated content

**Excel File** (`college_data_[timestamp].xlsx`)
- Summary sheet with all colleges
- Detailed courses breakdown
- Facilities categorization

**Summary Report** (`summary_report_[timestamp].txt`)
- Human-readable overview
- Statistics and analysis
- Error summary

## 🎯 Quick Examples

### Search for Engineering Colleges Only
```python
import asyncio
from main import CollegeInfoProcessor

async def engineering_search():
    processor = CollegeInfoProcessor()
    results = await processor.process_colleges(
        search_terms=["engineering colleges Karnataka VTU"],
        max_colleges=15
    )
    print(f"Found {len(results['colleges'])} engineering colleges")

asyncio.run(engineering_search())
```

### Target Specific Colleges
```python
specific_urls = [
    "https://iisc.ac.in/",
    "https://bmsce.ac.in/",
    "https://rvce.edu.in/"
]

results = await processor.process_colleges(
    specific_urls=specific_urls
)
```

## 🌾 Rural Student Features

The AI automatically generates:
- Simple language explanations
- Financial guidance and scholarship info
- Practical admission tips
- Accessibility assessments
- Support system information

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
    "scraping": {
        "max_colleges": 30,
        "request_delay": 2.0
    },
    "ai_generation": {
        "model": "openai/gpt-3.5-turbo",
        "temperature": 0.7
    }
}
```

## 🔧 Troubleshooting

**No results found?**
- Check internet connection
- Try different search terms
- Verify API key is correct

**Slow performance?**
- Reduce `max_colleges` parameter
- Increase `request_delay` in config

**AI generation fails?**
- Verify OpenRouter credits
- Try different model in config

## 📊 Sample Output Structure

```json
{
    "colleges": [
        {
            "id": 1,
            "raw_data": {
                "name": "College Name",
                "location": "City, Karnataka",
                "courses": {...},
                "facilities": {...}
            },
            "ai_generated": {
                "ai_generated_content": {
                    "overview": "Simple explanation...",
                    "rural_student_tips": "Practical advice...",
                    "final_recommendation": "Assessment..."
                },
                "rural_student_specific": {
                    "accessibility_score": 8,
                    "financial_considerations": {...}
                }
            }
        }
    ]
}
```

## 💡 Pro Tips

1. **Start Small**: Use `max_colleges=10` for testing
2. **Check Logs**: Look in `logs/` folder for detailed info
3. **Rural Focus**: AI content is specifically designed for rural students
4. **Multiple Formats**: Use Excel for easy sharing with students
5. **Reuse Code**: All modules can be imported and used separately

## 📞 Need Help?

1. Check the `README.md` for detailed documentation
2. Run `python examples.py` for usage examples
3. Look at log files for error details
4. Test with smaller datasets first

---

**Happy College Hunting! 🎓**
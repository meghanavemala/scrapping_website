# Karnataka College Information Scraper & AI Content Generator

A comprehensive tool that scrapes college information from multiple sources across Karnataka and generates AI-enhanced, rural-student-friendly content using OpenRouter API.

## Features

🎓 **Comprehensive Data Collection**
- Scrapes multiple education portals and college websites
- Extracts detailed information: courses, facilities, contact details, fees
- Supports both automated search and specific URL targeting

🤖 **AI-Powered Content Generation**
- Uses OpenRouter API with multiple language models
- Generates rural-student-friendly explanations
- Creates structured, easy-to-understand summaries
- Provides practical guidance and tips

📊 **Multi-Format Output**
- JSON format for programmatic use
- Excel spreadsheets with multiple sheets
- Human-readable summary reports
- Categorized data (courses by type, facilities by category)

🌾 **Rural Student Focus**
- Simple language explanations
- Financial guidance and scholarship information
- Practical admission tips
- Accessibility assessments

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd scrapping

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit the `.env` file with your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

Get your API key from [OpenRouter](https://openrouter.ai/).

### 3. Run the Scraper

```bash
python main.py
```

## Project Structure

```
scrapping/
├── main.py                 # Main entry point
├── scraper.py             # Web scraping module
├── ai_generator.py        # AI content generation
├── data_processor.py      # Data cleaning and processing
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── config.json           # Configuration file (optional)
├── README.md             # This file
├── logs/                 # Application logs
└── output/               # Generated results
    ├── college_data_[timestamp].json
    ├── college_data_[timestamp].xlsx
    └── summary_report_[timestamp].txt
```

## Usage Examples

### Basic Usage

```python
from main import CollegeInfoProcessor
import asyncio

async def main():
    processor = CollegeInfoProcessor()
    
    # Search for colleges
    results = await processor.process_colleges(
        search_terms=["engineering colleges Karnataka"],
        max_colleges=20
    )
    
    print(f"Processed {len(results['colleges'])} colleges")

asyncio.run(main())
```

### Advanced Usage with Custom Configuration

```python
from main import CollegeInfoProcessor
import asyncio

async def main():
    # Initialize with custom config
    processor = CollegeInfoProcessor("config.json")
    
    # Specific search terms for different types
    search_terms = [
        "medical colleges Karnataka NEET",
        "engineering colleges Karnataka JEE",
        "arts colleges Karnataka humanities",
        "management colleges Karnataka MBA"
    ]
    
    # Add specific college URLs if known
    specific_urls = [
        "https://iisc.ac.in/",
        "https://bmsce.ac.in/",
        "https://rvce.edu.in/"
    ]
    
    results = await processor.process_colleges(
        search_terms=search_terms,
        specific_urls=specific_urls,
        max_colleges=50
    )
    
    # Results are automatically saved to output/ directory
    print("Processing complete!")

asyncio.run(main())
```

## Configuration Options

Create a `config.json` file to customize the scraping process:

```json
{
    "scraping": {
        "max_colleges": 50,
        "request_delay": 1.5,
        "timeout": 30,
        "retry_attempts": 3
    },
    "ai_generation": {
        "model": "openai/gpt-3.5-turbo",
        "max_tokens": 2500,
        "temperature": 0.7
    },
    "search_terms": [
        "engineering colleges Karnataka",
        "medical colleges Karnataka",
        "arts colleges Karnataka"
    ]
}
```

## Output Formats

### 1. JSON Output
Complete structured data with raw scraped information and AI-generated content:

```json
{
    "timestamp": "2025-10-04T10:30:00",
    "colleges": [
        {
            "id": 1,
            "raw_data": {
                "name": "RV College of Engineering",
                "location": "Bangalore, Karnataka",
                "courses": {...},
                "facilities": {...}
            },
            "ai_generated": {
                "ai_generated_content": {
                    "overview": "Simple explanation...",
                    "rural_student_tips": "Practical advice..."
                }
            }
        }
    ]
}
```

### 2. Excel Output
- **Colleges Summary**: Overview of all colleges
- **Courses Detail**: Detailed course listings by category
- **Facilities Detail**: Comprehensive facility information

### 3. Summary Report
Human-readable text report with:
- Processing statistics
- College type distribution
- Top colleges by data completeness
- Error summary

## Supported College Sources

The scraper automatically searches and extracts from:

- **Government Portals**: KEA Karnataka, AICTE, UGC
- **Education Websites**: Careers360, CollegeDunia, Shiksha
- **College Websites**: Direct institutional sites
- **University Portals**: VTU, Bangalore University, etc.

## Rural Student Features

The AI generates content specifically designed for rural students:

- **Simple Language**: Technical terms explained clearly
- **Financial Guidance**: Fee structure, scholarships, hidden costs
- **Practical Tips**: Document preparation, language support
- **Accessibility**: Transportation, accommodation information
- **Support Systems**: Mentorship programs, counseling services

## API Models Supported

Through OpenRouter, you can use various models:

- `openai/gpt-3.5-turbo` (recommended for cost)
- `openai/gpt-4`
- `anthropic/claude-3-haiku`
- `meta-llama/llama-3-8b-instruct`
- And many more available on OpenRouter

## Troubleshooting

### Common Issues

1. **No colleges found**: 
   - Check internet connection
   - Verify search terms are relevant
   - Some websites may be temporarily unavailable

2. **AI generation fails**:
   - Verify OpenRouter API key is correct
   - Check API credits/quota
   - Try a different model

3. **Slow performance**:
   - Reduce `max_colleges` parameter
   - Increase `request_delay` in config
   - Use selenium fallback for problematic sites

### Logs

Check the `logs/` directory for detailed execution logs:
- `college_scraper_[date].log`: Complete application logs
- Includes success/failure details for each college

## Data Quality

The system automatically assesses data quality:

- **Completeness Score**: 0-1 based on available information
- **Source Reliability**: Educational sites ranked higher
- **Data Freshness**: Recent scraping marked
- **Validation**: Phone numbers, emails, URLs verified

## Ethical Considerations

- Respects robots.txt when available
- Implements rate limiting to avoid overwhelming servers
- Focuses on publicly available educational information
- No personal student data collection

## Contributing

To extend functionality:

1. **Add New Sources**: Modify `scraper.py` to include new college directories
2. **Improve AI Prompts**: Enhance prompts in `ai_generator.py`
3. **Add Data Fields**: Extend extraction logic in `data_processor.py`
4. **New Output Formats**: Add exporters in `utils.py`

## License

This project is for educational purposes. Please respect website terms of service and use responsibly.

## Support

For issues or questions:
1. Check the logs for error details
2. Verify configuration settings
3. Ensure all dependencies are installed
4. Test with a smaller dataset first

---

**Happy Scraping! 🎓**
"""
College Information Web Scraper and AI Content Generator
========================================================

A comprehensive tool for scraping college information in Karnataka and
generating AI-enhanced, student-friendly content using OpenRouter models.

Author: GitHub Copilot
Date: October 2025
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm

from scraper import CollegeScraper
from ai_generator import AIContentGenerator
from data_processor import DataProcessor
from utils import setup_logger, save_results, load_config

class CollegeInfoProcessor:
    """Main orchestrator for college information processing."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the processor with configuration."""
        load_dotenv()
        
        self.logger = setup_logger()
        self.config = load_config(config_path) if config_path else {}
        
        # Initialize components
        self.scraper = CollegeScraper()
        self.ai_generator = AIContentGenerator()
        self.data_processor = DataProcessor()
        
        self.logger.info("College Info Processor initialized successfully")
    
    async def process_colleges(self, 
                             search_terms: List[str] = None,
                             specific_urls: List[str] = None,
                             max_colleges: int = 50) -> Dict[str, Any]:
        """
        Main method to process college information.
        
        Args:
            search_terms: List of search terms for finding colleges
            specific_urls: List of specific college URLs to scrape
            max_colleges: Maximum number of colleges to process
            
        Returns:
            Dictionary containing processed results
        """
        self.logger.info(f"Starting college processing with max_colleges={max_colleges}")
        
        if not search_terms:
            search_terms = [
                "engineering colleges Karnataka",
                "medical colleges Karnataka", 
                "arts colleges Karnataka",
                "commerce colleges Karnataka",
                "universities Karnataka"
            ]
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "colleges": [],
            "summary": {},
            "errors": []
        }
        
        try:
            # Step 1: Scrape college data
            self.logger.info("Step 1: Scraping college data...")
            scraped_data = await self.scraper.scrape_colleges(
                search_terms=search_terms,
                specific_urls=specific_urls,
                max_results=max_colleges
            )
            
            self.logger.info(f"Scraped data for {len(scraped_data)} colleges")
            
            # Step 2: Process and clean data
            self.logger.info("Step 2: Processing and cleaning data...")
            processed_colleges = []
            
            for i, college_data in enumerate(tqdm(scraped_data, desc="Processing colleges")):
                try:
                    # Clean and structure the data
                    clean_data = self.data_processor.clean_college_data(college_data)
                    
                    # Generate AI-enhanced content
                    enhanced_content = await self.ai_generator.generate_college_content(clean_data)
                    
                    # Combine original and enhanced data
                    final_college_data = {
                        "id": i + 1,
                        "raw_data": clean_data,
                        "ai_generated": enhanced_content,
                        "processed_at": datetime.now().isoformat()
                    }
                    
                    processed_colleges.append(final_college_data)
                    
                    # Small delay to avoid overwhelming APIs
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    error_msg = f"Error processing college {i+1}: {str(e)}"
                    self.logger.error(error_msg)
                    results["errors"].append(error_msg)
                    continue
            
            results["colleges"] = processed_colleges
            results["summary"] = {
                "total_colleges": len(processed_colleges),
                "successful_processing": len(processed_colleges),
                "errors": len(results["errors"]),
                "processing_time": datetime.now().isoformat()
            }
            
            # Step 3: Save results
            self.logger.info("Step 3: Saving results...")
            output_path = save_results(results)
            self.logger.info(f"Results saved to: {output_path}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Critical error in processing: {str(e)}")
            results["errors"].append(f"Critical error: {str(e)}")
            return results

async def main():
    """Main entry point for the application."""
    print("🎓 College Information Scraper & AI Content Generator")
    print("=" * 60)
    
    # Initialize processor
    processor = CollegeInfoProcessor()
    
    # Define search parameters
    search_terms = [
        "engineering colleges Karnataka top",
        "medical colleges Karnataka NEET",
        "management colleges Karnataka MBA",
        "arts science colleges Karnataka",
        "technical universities Karnataka"
    ]
    
    # Process colleges
    results = await processor.process_colleges(
        search_terms=search_terms,
        max_colleges=30  # Adjust based on your needs
    )
    
    # Display summary
    print(f"\n📊 Processing Summary:")
    print(f"✅ Successfully processed: {results['summary'].get('successful_processing', 0)} colleges")
    print(f"❌ Errors encountered: {len(results['errors'])}")
    print(f"⏱️ Completed at: {results['summary'].get('processing_time', 'Unknown')}")
    
    if results['errors']:
        print(f"\n⚠️ Errors:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    print(f"\n🎯 Results saved! Check the output directory for detailed information.")

if __name__ == "__main__":
    asyncio.run(main())
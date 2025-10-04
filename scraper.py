"""
College Information Web Scraper
===============================

Comprehensive scraper for extracting college information from multiple sources
including government websites, education portals, and college websites.
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urljoin, urlparse
import json

import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from retry import retry
import pandas as pd

from utils import setup_logger, clean_text, extract_phone_numbers, extract_emails

class CollegeScraper:
    """Main scraper class for college information extraction."""
    
    def __init__(self):
        self.logger = setup_logger()
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Known sources for Karnataka college information
        self.sources = {
            'dte_karnataka': 'https://kea.kar.nic.in/',
            'karnataka_edu': 'https://www.education.gov.in/',
            'aicte': 'https://www.aicte-india.org/',
            'ugc': 'https://www.ugc.ac.in/',
            'careers360': 'https://www.careers360.com/colleges/list-of-colleges-in-karnataka',
            'collegedunia': 'https://www.collegedunia.com/karnataka-colleges',
            'shiksha': 'https://www.shiksha.com/college/karnataka-colleges-ctlg',
        }
        
        self.scraped_urls: Set[str] = set()
        
    def setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Selenium WebDriver with optimal configuration."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        return driver
    
    @retry(tries=3, delay=2)
    async def fetch_url(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch URL content with retry mechanism."""
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"HTTP {response.status} for URL: {url}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_college_info_from_html(self, html: str, url: str) -> Dict[str, Any]:
        """Extract college information from HTML content."""
        soup = BeautifulSoup(html, 'html.parser')
        
        college_info = {
            'source_url': url,
            'name': '',
            'location': '',
            'address': '',
            'phone': [],
            'email': [],
            'website': '',
            'courses': [],
            'fees': {},
            'facilities': [],
            'description': '',
            'established': '',
            'affiliation': '',
            'recognition': [],
            'admission_process': '',
            'placement_details': '',
            'rankings': {},
            'student_reviews': [],
            'images': []
        }
        
        # Extract college name
        name_selectors = [
            'h1', 'h2', '.college-name', '.title', '[class*="name"]',
            '[class*="title"]', '.heading', '.college-title'
        ]
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                college_info['name'] = clean_text(element.get_text())
                break
        
        # Extract contact information
        college_info['phone'] = extract_phone_numbers(html)
        college_info['email'] = extract_emails(html)
        
        # Extract location and address
        location_keywords = ['address', 'location', 'contact', 'situated', 'located']
        for keyword in location_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements:
                parent = element.parent
                if parent:
                    text = clean_text(parent.get_text())
                    if any(place in text.lower() for place in ['karnataka', 'bangalore', 'mysore', 'hubli']):
                        college_info['location'] = text
                        break
        
        # Extract courses
        course_selectors = [
            '[class*="course"]', '[class*="program"]', '[class*="department"]',
            'ul li', '.courses li', '.programs li'
        ]
        courses = set()
        for selector in course_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = clean_text(element.get_text())
                if any(term in text.lower() for term in ['engineering', 'medical', 'mba', 'bsc', 'bcom', 'ba', 'btech', 'mtech']):
                    courses.add(text)
        college_info['courses'] = list(courses)[:20]  # Limit to 20 courses
        
        # Extract facilities
        facility_keywords = ['facilities', 'amenities', 'infrastructure', 'campus']
        facilities = set()
        for keyword in facility_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements:
                parent = element.parent
                if parent:
                    # Look for lists near facility keywords
                    nearby_lists = parent.find_all(['ul', 'ol'])
                    for ul in nearby_lists:
                        for li in ul.find_all('li'):
                            facility_text = clean_text(li.get_text())
                            if len(facility_text) < 100:  # Reasonable facility description
                                facilities.add(facility_text)
        college_info['facilities'] = list(facilities)[:15]  # Limit to 15 facilities
        
        # Extract establishment year
        year_pattern = r'\b(19|20)\d{2}\b'
        established_keywords = ['established', 'founded', 'started', 'inception']
        for keyword in established_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    years = re.findall(year_pattern, text)
                    if years:
                        college_info['established'] = years[0]
                        break
        
        # Extract description (meta description or first paragraph)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            college_info['description'] = clean_text(meta_desc.get('content', ''))
        else:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = clean_text(p.get_text())
                if len(text) > 50 and len(text) < 500:
                    college_info['description'] = text
                    break
        
        # Extract images
        img_tags = soup.find_all('img')
        images = []
        for img in img_tags:
            src = img.get('src')
            if src:
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(url, src)
                if src.startswith('http') and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    images.append(src)
        college_info['images'] = images[:5]  # Limit to 5 images
        
        return college_info
    
    async def search_colleges_google(self, search_term: str, max_results: int = 20) -> List[str]:
        """Search for college URLs using Google search simulation."""
        search_urls = []
        
        # Use DuckDuckGo as an alternative to Google
        search_url = f"https://duckduckgo.com/html/?q={search_term}+site:edu+OR+site:ac.in+OR+site:org"
        
        try:
            async with aiohttp.ClientSession() as session:
                html = await self.fetch_url(session, search_url)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        href = link['href']
                        if any(domain in href for domain in ['.edu', '.ac.in', 'college', 'university']):
                            if href not in self.scraped_urls:
                                search_urls.append(href)
                                if len(search_urls) >= max_results:
                                    break
        except Exception as e:
            self.logger.error(f"Error in Google search for '{search_term}': {str(e)}")
        
        return search_urls
    
    async def scrape_college_directories(self) -> List[str]:
        """Scrape known college directory websites for Karnataka colleges."""
        college_urls = []
        
        directory_configs = {
            'careers360': {
                'url': 'https://www.careers360.com/colleges/list-of-colleges-in-karnataka',
                'selectors': ['a[href*="/colleges/"]', '.college-name a']
            },
            'collegedunia': {
                'url': 'https://www.collegedunia.com/karnataka-colleges',
                'selectors': ['a[href*="/college/"]', '.cd-clg-name a']
            },
            'shiksha': {
                'url': 'https://www.shiksha.com/college/karnataka-colleges-ctlg',
                'selectors': ['a[href*="/college/"]', '.course-name a']
            }
        }
        
        async with aiohttp.ClientSession() as session:
            for site_name, config in directory_configs.items():
                try:
                    self.logger.info(f"Scraping {site_name}...")
                    html = await self.fetch_url(session, config['url'])
                    
                    if html:
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        for selector in config['selectors']:
                            links = soup.select(selector)
                            for link in links:
                                href = link.get('href')
                                if href:
                                    if href.startswith('/'):
                                        href = urljoin(config['url'], href)
                                    if href not in self.scraped_urls and 'karnataka' in href.lower():
                                        college_urls.append(href)
                                        if len(college_urls) >= 50:  # Limit per site
                                            break
                    
                    # Delay between sites
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error scraping {site_name}: {str(e)}")
        
        return college_urls
    
    async def scrape_colleges(self, 
                            search_terms: List[str] = None, 
                            specific_urls: List[str] = None,
                            max_results: int = 50) -> List[Dict[str, Any]]:
        """Main method to scrape college information."""
        self.logger.info(f"Starting college scraping with max_results={max_results}")
        
        all_urls = set()
        
        # Add specific URLs if provided
        if specific_urls:
            all_urls.update(specific_urls)
        
        # Search for college URLs
        if search_terms:
            for term in search_terms:
                self.logger.info(f"Searching for: {term}")
                urls = await self.search_colleges_google(term, max_results // len(search_terms))
                all_urls.update(urls)
                await asyncio.sleep(1)
        
        # Scrape from known directories
        directory_urls = await self.scrape_college_directories()
        all_urls.update(directory_urls)
        
        # Limit total URLs
        all_urls = list(all_urls)[:max_results]
        self.logger.info(f"Found {len(all_urls)} URLs to scrape")
        
        # Scrape college information
        colleges_data = []
        
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(all_urls):
                try:
                    self.logger.info(f"Scraping {i+1}/{len(all_urls)}: {url}")
                    
                    html = await self.fetch_url(session, url)
                    if html:
                        college_info = self.extract_college_info_from_html(html, url)
                        
                        # Only add if we found meaningful information
                        if college_info['name'] or college_info['courses'] or college_info['description']:
                            colleges_data.append(college_info)
                            self.scraped_urls.add(url)
                            self.logger.info(f"✅ Successfully scraped: {college_info.get('name', 'Unknown')}")
                        else:
                            self.logger.warning(f"⚠️ No meaningful data found for: {url}")
                    
                    # Rate limiting
                    await asyncio.sleep(1.5)
                    
                except Exception as e:
                    self.logger.error(f"Error scraping {url}: {str(e)}")
                    continue
        
        self.logger.info(f"Successfully scraped {len(colleges_data)} colleges")
        return colleges_data

    def scrape_with_selenium(self, url: str) -> Optional[Dict[str, Any]]:
        """Fallback method using Selenium for JavaScript-heavy sites."""
        driver = None
        try:
            driver = self.setup_selenium_driver()
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and extract information
            html = driver.page_source
            return self.extract_college_info_from_html(html, url)
            
        except Exception as e:
            self.logger.error(f"Selenium error for {url}: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()
    
    async def scrape_college_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single college from a specific URL."""
        try:
            async with aiohttp.ClientSession() as session:
                html = await self.fetch_url(session, url)
                if html:
                    return self.extract_college_info_from_html(html, url)
                else:
                    # Try with selenium as fallback
                    return self.scrape_with_selenium(url)
        except Exception as e:
            self.logger.error(f"Error scraping single URL {url}: {str(e)}")
            return None
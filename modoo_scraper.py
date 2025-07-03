import requests
from bs4 import BeautifulSoup
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import csv

# Method 1: Selenium-based scraper (RECOMMENDED - Most likely to work)
def get_search_results_selenium(query, max_results=50):
    """
    Scrape Google search results using Selenium (recommended approach)
    """
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navigate to Google
        driver.get("https://www.google.com")
        time.sleep(2)
        
        # Find search box and enter query
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.submit()
        
        # Wait for results to load
        time.sleep(3)
        
        titles = []
        page = 0
        
        while len(titles) < max_results and page < 10:  # Increase to 10 pages
            try:
                # Wait for search results to be present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#search"))
                )
                
                # Find all search result containers - try multiple selectors
                result_selectors = [
                    "#rso > div",
                    "#rso div[data-hveid]",
                    "#search div[data-hveid]",
                    ".g",
                    "[data-hveid]"
                ]
                
                result_containers = []
                for selector in result_selectors:
                    containers = driver.find_elements(By.CSS_SELECTOR, selector)
                    if containers:
                        result_containers = containers
                        print(f"Using selector: {selector}, found {len(containers)} containers")
                        break
                
                for container in result_containers:
                    try:
                        # Try different selectors for title
                        title_element = None
                        selectors = ["h3", "h3.LC20lb", "[role='heading'] h3"]
                        
                        for selector in selectors:
                            try:
                                title_element = container.find_element(By.CSS_SELECTOR, selector)
                                break
                            except:
                                continue
                        
                        if title_element:
                            title = title_element.text.strip()
                            if title and title not in titles:
                                titles.append(title)
                                print(f"Found: {title}")
                                
                                if len(titles) >= max_results:
                                    break
                    except Exception as e:
                        continue
                
                # Try to go to next page
                if len(titles) < max_results:
                    try:
                        # Multiple strategies for finding next button
                        next_selectors = [
                            "a[aria-label*='Next']",
                            "a[aria-label*='다음']",  # Korean for "Next"
                            "#pnnext",
                            "a#pnnext",
                            "td.b a[aria-label*='Next']",
                            "span[style*='left:0'] + a"
                        ]
                        
                        next_button = None
                        for selector in next_selectors:
                            try:
                                next_button = driver.find_element(By.CSS_SELECTOR, selector)
                                print(f"Found next button with selector: {selector}")
                                break
                            except:
                                continue
                        
                        if next_button:
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(4)  # Longer wait
                            page += 1
                            print(f"Navigated to page {page + 1}")
                        else:
                            print("No next button found - checking current page URL")
                            current_url = driver.current_url
                            print(f"Current URL: {current_url}")
                            
                            # Try URL-based pagination as fallback
                            if 'start=' in current_url:
                                import re
                                start_match = re.search(r'start=(\d+)', current_url)
                                if start_match:
                                    current_start = int(start_match.group(1))
                                    next_start = current_start + 10
                                else:
                                    next_start = 10
                            else:
                                next_start = 10
                            
                            next_url = current_url.split('&start=')[0] + f'&start={next_start}'
                            print(f"Trying URL navigation to: {next_url}")
                            driver.get(next_url)
                            time.sleep(4)
                            page += 1
                            
                    except Exception as e:
                        print(f"Pagination error: {e}")
                        break
                else:
                    break
                    
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
        
        return titles
        
    except Exception as e:
        print(f"Selenium error: {e}")
        return []
    finally:
        if 'driver' in locals():
            driver.quit()

# Method 2: Improved requests-based scraper with debugging
def get_search_results_requests(query, max_results=50):
    """
    Improved version of your original approach with better debugging
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    titles = []
    page = 0
    
    while len(titles) < max_results and page < 5:
        start = page * 10
        params = {
            'q': query,
            'hl': 'ko',  # Korean language
            'gl': 'kr',  # Korea location
            'start': start,
            'num': 10
        }
        
        try:
            response = requests.get(
                'https://www.google.com/search',
                headers=headers,
                params=params,
                timeout=10
            )
            
            print(f"Page {page + 1} - Status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response content preview: {response.text[:500]}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Debug: Check what we actually received
            if "detected unusual traffic" in response.text.lower():
                print("Google detected unusual traffic - blocked!")
                break
            
            # Try multiple selectors that might work
            selectors = [
                'h3',
                'h3.LC20lb',
                '[role="heading"] h3',
                'div[data-hveid] h3',
                '#rso h3'
            ]
            
            found_titles_this_page = 0
            for selector in selectors:
                elements = soup.select(selector)
                print(f"Selector '{selector}' found {len(elements)} elements")
                
                for element in elements:
                    title = element.get_text().strip()
                    if title and title not in titles:
                        titles.append(title)
                        found_titles_this_page += 1
                        print(f"Found: {title}")
                        
                        if len(titles) >= max_results:
                            return titles
                
                if found_titles_this_page > 0:
                    break  # If we found titles with this selector, don't try others
            
            if found_titles_this_page == 0:
                print("No titles found on this page")
                # Save HTML for debugging
                with open(f'debug_page_{page}.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"Saved HTML to debug_page_{page}.html for inspection")
                
            page += 1
            time.sleep(2)  # Be polite
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    
    return titles

# Method 3: Google Custom Search API (requires API key)
def get_search_results_api(query, api_key, search_engine_id, max_results=50):
    """
    Use Google Custom Search API (requires setup)
    """
    titles = []
    start_index = 1
    
    while len(titles) < max_results and start_index <= 91:  # Google API limit
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'start': start_index,
            'num': min(10, max_results - len(titles))
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'items' in data:
                for item in data['items']:
                    titles.append(item['title'])
            
            start_index += 10
            
        except Exception as e:
            print(f"API error: {e}")
            break
    
    return titles

# Alternative method: Direct URL navigation
def get_search_results_direct_urls(query, max_results=100):
    """
    Alternative approach: directly navigate to each page URL
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        titles = []
        
        # Directly visit each page by constructing URLs
        for start in range(0, min(max_results, 100), 10):  # Google typically shows up to 100 pages
            url = f"https://www.google.com/search?q={query}&start={start}&hl=ko&gl=kr"
            print(f"Visiting page {start//10 + 1}: {url}")
            
            driver.get(url)
            time.sleep(3)
            
            # Find titles on this page
            found_on_page = 0
            title_selectors = ["h3", "h3.LC20lb", "[role='heading'] h3", "div[data-hveid] h3"]
            
            for selector in title_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        title = element.text.strip()
                        if title and title not in titles:
                            titles.append(title)
                            found_on_page += 1
                            print(f"Found: {title}")
                    
                    if found_on_page > 0:
                        break
                except:
                    continue
            
            print(f"Found {found_on_page} titles on page {start//10 + 1}")
            
            if found_on_page == 0:
                print("No more results found")
                break
                
            if len(titles) >= max_results:
                break
        
        return titles
        
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if 'driver' in locals():
            driver.quit()

def main():
    query = 'site:modoo.at 미금 병원'
    
    print("Attempting to scrape Google search results...")
    print(f"Query: {query}")
    print("=" * 50)
    
    # Try Method 1: Selenium (recommended)
    print("Method 1: Selenium-based scraping...")
    titles_selenium = get_search_results_selenium(query, max_results=100)
    
    if len(titles_selenium) > 10:
        print(f"\nSelenium found {len(titles_selenium)} titles")
        save_titles(titles_selenium, 'modoo_clinic_titles_selenium3.txt')
    else:
        print(f"Selenium only found {len(titles_selenium)} titles, trying direct URL method...")
        
        # Try Alternative Method: Direct URL navigation
        print("\nMethod Alternative: Direct URL navigation...")
        titles_direct = get_search_results_direct_urls(query, max_results=100)
        
        if titles_direct:
            print(f"\nDirect URL method found {len(titles_direct)} titles")
            save_titles(titles_direct, 'modoo_clinic_titles_direct.txt')
        else:
            print("\nDirect URL method failed, trying requests method...")
            
            # Try Method 2: Improved requests
            print("\nMethod 2: Requests-based scraping...")
            titles_requests = get_search_results_requests(query, max_results=100)
            
            if titles_requests:
                print(f"\nRequests method found {len(titles_requests)} titles")
                save_titles(titles_requests, 'modoo_clinic_titles_requests.txt')
            else:
                print("\nAll methods failed. Consider using the Google Custom Search API.")
                print("See: https://developers.google.com/custom-search/v1/introduction")

def save_titles(titles, filename):
    """Save titles to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for title in titles:
            f.write(title + '\n')
    
    # Also save as CSV for better data handling
    csv_filename = filename.replace('.txt', '.csv')
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title'])  # Header
        for title in titles:
            writer.writerow([title])
    
    print(f"Saved {len(titles)} titles to {filename} and {csv_filename}")

if __name__ == '__main__':
    main()
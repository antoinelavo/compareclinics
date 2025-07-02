import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from urllib.parse import urljoin, urlparse
import re

class ClinicScraper:
    def __init__(self):
        self.session = requests.Session()
        # Set a realistic user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.clinics = []
    
    def scrape_clinic_page(self, url):
        """Scrape a single clinic page"""
        try:
            # Store current URL for debugging
            self._current_url = url
            
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract clinic data - optimized for Korean clinic sites
            clinic_data = {
                'name': self.extract_clinic_name(soup),
                'phone': self.extract_phone(soup),
                'address': self.extract_address(soup),
                'services': self.extract_services(soup),
                'description': self.extract_text(soup, ['.description', '.about', '.intro', '.clinic-intro', 'meta[name="description"]']),
                'url': url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # If no address found on main page, try to find contact/location pages
            if not clinic_data['address']:
                contact_urls = self.find_contact_pages(soup, url)
                for contact_url in contact_urls[:2]:  # Try up to 2 contact pages
                    print(f"  Trying contact page: {contact_url}")
                    try:
                        contact_response = self.session.get(contact_url)
                        contact_response.raise_for_status()
                        contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                        contact_address = self.extract_address(contact_soup)
                        if contact_address:
                            clinic_data['address'] = contact_address
                            print(f"  Found address on contact page: {contact_address}")
                            break
                    except Exception as e:
                        print(f"  Error scraping contact page {contact_url}: {str(e)}")
                        continue
            
            return clinic_data
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def extract_text(self, soup, selectors):
        """Try multiple selectors to find text"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    return element.get('content', '').strip()
                text = element.get_text().strip()
                # Clean up whitespace and newlines
                text = ' '.join(text.split())
                return text
        return ''
    
    def extract_clinic_name(self, soup):
        """Extract clinic name with Korean-specific selectors"""
        # Try various selectors for clinic names
        name_selectors = [
            'h1', '.clinic-name', '.title', '.logo-text', '.brand-name',
            '.site-title', '.hospital-name', '.main-title', 'title',
            '.navbar-brand', '.header-title', '.clinic-title'
        ]
        
        name = self.extract_text(soup, name_selectors)
        
        # If we got the page title, try to clean it up
        if not name or len(name) > 100:
            title = soup.find('title')
            if title:
                name = title.get_text().strip()
                # Remove common suffixes
                name = name.replace(' - Home', '').replace(' | Home', '')
                name = name.split('|')[0].split('-')[0].strip()
        
        return name

    def extract_address(self, soup):
        """Enhanced address extraction for Korean clinic websites"""
        
        # Debug: Let's see what text we're working with for problematic sites
        url = getattr(self, '_current_url', '')
        is_debug_site = any(site in url for site in ['jkplastic.com', 'amoaskinclinic640.com'])
        
        # 1) Check for address in meta tags or script tags (sometimes stored there)
        meta_address = self.extract_meta_address(soup)
        if meta_address:
            return meta_address
        
        # 2) First try pattern matching on the full text - this catches most plain text addresses
        pattern_address = self.extract_pattern_address(soup)
        if pattern_address:
            return pattern_address
        
        # 3) Schema.org microdata
        address_data = self.extract_schema_address(soup)
        if address_data:
            return address_data
        
        # 4) JSON-LD structured data
        json_ld_address = self.extract_json_ld_address(soup)
        if json_ld_address:
            return json_ld_address
        
        # 5) Look in script tags for address data (sometimes stored in JavaScript variables)
        script_address = self.extract_script_address(soup)
        if script_address:
            return script_address
        
        # 6) Common CSS selectors with Korean-specific classes
        address_selectors = [
            '.address', '.location', '.addr', '.contact-address',
            '.clinic-address', '.hospital-address', '.venue-address',
            '.contact-info', '.info', '.clinic-info', '.location-info',
            '[class*="address"]', '[class*="location"]', '[class*="contact"]',
            '[id*="address"]', '[id*="location"]', '[id*="contact"]'
        ]
        
        for selector in address_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Look for address patterns within these elements
                element_text = element.get_text()
                if is_debug_site and element_text.strip():
                    print(f"  Debug - Found {selector}: {element_text[:100]}...")
                found_address = self.find_address_in_text(element_text)
                if found_address:
                    return found_address
        
        # 7) Look in common content areas (paragraphs, divs near contact info)
        content_elements = soup.select('p, div, span, li')
        
        for element in content_elements:
            text = element.get_text().strip()
            if len(text) > 15 and len(text) < 200:  # Reasonable length for an address
                # Debug: Show potential address-like text
                if is_debug_site and any(indicator in text.lower() for indicator in ['nonhyeon', 'samseong', '835', '640', 'gangnam', 'seoul']):
                    print(f"  Debug - Potential address text: {text}")
                
                found_address = self.find_address_in_text(text)
                if found_address:
                    return found_address
        
        # 8) If still no address found for debug sites, let's try broader patterns
        if is_debug_site:
            print(f"  Debug - Trying broader search...")
            full_text = soup.get_text()
            # Look for any text containing the known street numbers
            if '835' in full_text or '640' in full_text:
                lines = full_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if ('835' in line or '640' in line) and len(line) < 300:
                        print(f"  Debug - Line with street number: {line}")
                        # Try more lenient pattern matching
                        found = self.find_address_in_text_lenient(line)
                        if found:
                            return found
        
        return ''
    
    def extract_meta_address(self, soup):
        """Extract address from meta tags"""
        # Check various meta tags for address
        meta_selectors = [
            'meta[name="address"]',
            'meta[name="location"]', 
            'meta[property="business:contact_data:street_address"]',
            'meta[property="og:street-address"]',
            'meta[name="geo.address"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                content = self.clean_address_text(meta.get('content'))
                if self.is_valid_korean_address(content):
                    return content
        return None
    
    def extract_script_address(self, soup):
        """Extract address from JavaScript variables or data"""
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string:
                script_text = script.string
                
                # Look for common JavaScript address patterns
                js_patterns = [
                    r'address["\']?\s*[:=]\s*["\']([^"\']{20,100})["\']',
                    r'location["\']?\s*[:=]\s*["\']([^"\']{20,100})["\']',
                    r'["\']address["\']?\s*[:=]\s*["\']([^"\']{20,100})["\']',
                    r'street["\']?\s*[:=]\s*["\']([^"\']{10,100})["\']'
                ]
                
                for pattern in js_patterns:
                    matches = re.findall(pattern, script_text, re.IGNORECASE)
                    for match in matches:
                        cleaned = self.clean_address_text(match)
                        if self.is_valid_korean_address(cleaned):
                            return cleaned
        
        return None
    
    def extract_pattern_address(self, soup):
        """Extract address using regex patterns from full page text"""
        full_text = soup.get_text(separator=' ')
        return self.find_address_in_text(full_text)
    
    def extract_schema_address(self, soup):
        """Extract address from Schema.org microdata"""
        # Full address in single element
        full_address = soup.select_one('[itemprop="address"]')
        if full_address:
            addr_text = self.clean_address_text(full_address.get_text())
            if self.is_valid_korean_address(addr_text):
                return addr_text
        
        # Composite address from multiple elements
        address_parts = []
        for prop in ['streetAddress', 'addressLocality', 'addressRegion', 'postalCode']:
            element = soup.select_one(f'[itemprop="{prop}"]')
            if element:
                part = self.clean_address_text(element.get_text())
                if part:
                    address_parts.append(part)
        
        if address_parts:
            combined = ' '.join(address_parts)
            if self.is_valid_korean_address(combined):
                return combined
        
        return None
    
    def extract_json_ld_address(self, soup):
        """Extract address from JSON-LD structured data"""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Look for address in various JSON-LD structures
                address = None
                if 'address' in data:
                    addr_obj = data['address']
                    if isinstance(addr_obj, str):
                        address = addr_obj
                    elif isinstance(addr_obj, dict):
                        # Combine address components
                        parts = []
                        for key in ['streetAddress', 'addressLocality', 'addressRegion']:
                            if key in addr_obj:
                                parts.append(str(addr_obj[key]))
                        address = ' '.join(parts) if parts else None
                
                if address:
                    cleaned = self.clean_address_text(address)
                    if self.is_valid_korean_address(cleaned):
                        return cleaned
                        
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        
        return None
    
    def find_contact_pages(self, soup, base_url):
        """Find contact or location pages that might have address info"""
        contact_urls = []
        
        # Look for contact/location links
        contact_keywords = [
            'contact', 'location', 'directions', 'address', 'find us', 'visit',
            '오시는길', '찾아오시는길', '위치', '연락처', '주소', '방문',
            'about', 'clinic-info', 'information'
        ]
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            link_text = link.get_text().strip().lower()
            
            # Check if link text or href contains contact keywords
            if any(keyword in link_text or keyword in href.lower() for keyword in contact_keywords):
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(base_url, '/' + href)
                
                # Avoid duplicates and external sites
                if full_url not in contact_urls and urlparse(full_url).netloc == urlparse(base_url).netloc:
                    contact_urls.append(full_url)
        
        return contact_urls
    
    def find_address_in_text_lenient(self, text):
        """More lenient address finding for debugging"""
        if not text or len(text) < 10:
            return None
            
        # Very broad patterns to catch addresses we're missing
        lenient_patterns = [
            # Any text with street number + "ro" + district/city indicators
            r'\b\d+,?\s*[A-Za-z가-힣-]+(?:ro|로)[^.]*?(?:gu|구|Seoul|서울|Gangnam|강남)',
            
            # Any text with known street numbers from the examples
            r'\b(?:835|640)[^.]*?(?:Nonhyeon|Samseong)[^.]*?(?:Gangnam|Seoul)',
            
            # Capture larger chunks that contain address elements
            r'[^.]*?\b\d+,?\s*[A-Za-z가-힣-]+(?:ro|로)[^.]*?(?:Seoul|서울)[^.]*',
        ]
        
        for pattern in lenient_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                cleaned = self.clean_address_text(match)
                print(f"    Debug - Lenient match: {cleaned}")
                if len(cleaned) > 20:
                    return cleaned
        
        return None
    
    def find_address_in_text(self, text):
        """Find Korean address patterns in any text"""
        if not text or len(text) < 10:
            return None
        
        # Clean the text first
        text = ' '.join(text.split())
        
        # Korean address patterns based on your examples
        patterns = [
            # Pattern 1: "Number, Street-name, District-gu, Seoul, Country" (note the comma after number)
            r'\d+,\s+[A-Za-z가-힣-]+(?:ro|로|Road|Street|Ave|Avenue),?\s+[A-Za-z가-힣-]+(?:gu|구|Gu|dong|Dong),?\s+(?:Seoul|서울),?\s*(?:South\s+Korea|Republic\s+of\s+Korea|대한민국)?',
            
            # Pattern 2: "Number Street-name, District-gu, Seoul, South Korea" (with optional floor info)
            r'\d+\s+[A-Za-z가-힣-]+(?:ro|로|Road|Street|Ave|Avenue),?\s+[A-Za-z가-힣-]+(?:gu|구|Gu|dong|Dong),?\s+(?:Seoul|서울),?\s*(?:South\s+Korea|Republic\s+of\s+Korea)?(?:\s*\([^)]+\))?',
            
            # Pattern 3: "Building Name Floor, Number Street-name, District-gu, Seoul"
            r'[A-Za-z가-힣\s]+(?:Building|Tower|Center|빌딩|타워|센터)\s+\d+(?:st|nd|rd|th)?\s+Floor,?\s+\d+,?\s*[A-Za-z가-힣-]+(?:ro|로|daero|대로),?\s+[A-Za-z가-힣-]+(?:gu|구|Gu),?\s+(?:Seoul|서울),?\s*(?:South\s+Korea|Republic\s+of\s+Korea)?',
            
            # Pattern 4: "Number Street-name, Floor info, District, Seoul" (Floor in middle)
            r'\d+,?\s*[A-Za-z가-힣-]+(?:ro|로|Road|Street),?\s+\d+(?:st|nd|rd|th)?\s+Floor,?\s+[A-Za-z가-힣-]+(?:gu|구|District|Disctrict),?\s+(?:Seoul|서울)',
            
            # Pattern 5: Korean format "Number Street-name, District, Seoul"
            r'\d+,?\s*[가-힣A-Za-z-]+(?:로|길|대로),?\s+[가-힣A-Za-z-]+(?:구|시|동),?\s+(?:서울|Seoul)(?:\s*,?\s*(?:South\s+Korea|Republic\s+of\s+Korea|대한민국))?',
            
            # Pattern 6: Full Korean address
            r'서울특?별?시\s+[가-힣]+구\s+[가-힣\s]+(?:로|길|대로)\s*\d+[-\d\s]*(?:[가-힣\s\d,()]+)?',
            
            # Pattern 7: Simple format "Number-ro, District-gu, Seoul"
            r'\d+,?\s*[A-Za-z가-힣-]+(?:ro|로|길),?\s+[A-Za-z가-힣-]+(?:gu|구),?\s+(?:Seoul|서울)',
            
            # Pattern 8: Address with building and floor in parentheses
            r'\d+,?\s*[A-Za-z가-힣-]+(?:ro|로),?\s+[A-Za-z가-힣-]+(?:gu|구),?\s+(?:Seoul|서울)(?:\s*\([^)]*[Ff]loor[^)]*\))?',
            
            # Pattern 9: Other major Korean cities
            r'\d+[-\d\s]*,?\s*[가-힣A-Za-z\s]+(?:로|길|Road|Street),?\s*[가-힣A-Za-z\s]+(?:구|시|동|District),?\s*(?:부산|대구|인천|광주|대전|울산|Busan|Daegu|Incheon)',
            
            # Pattern 10: Gangnam specific (very common for plastic surgery) - with comma variations
            r'\d+,?\s*[A-Za-z가-힣-]+(?:ro|로),?\s+강남(?:구|gu|Gu),?\s*(?:서울|Seoul)?',
            
            # Pattern 11: Flexible pattern with typos like "Disctrict" instead of "District"
            r'\d+,?\s*[A-Za-z가-힣-]+(?:ro|로|Road|Street),?\s*(?:\d+(?:st|nd|rd|th)?\s*Floor,?\s*)?[A-Za-z가-힣-]+(?:gu|구|District|Disctrict),?\s*(?:Seoul|서울|Gangnam|강남)',
            
            # Pattern 12: Very flexible catch-all pattern
            r'(?:\*\s*)?\d+,?\s*[A-Za-z가-힣-]+(?:ro|로),?\s*(?:\d+(?:st|nd|rd|th)?\s*Floor,?\s*)?[A-Za-z가-힣\s-]+(?:gu|구|District|Disctrict),?\s*(?:Seoul|서울)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cleaned = self.clean_address_text(match)
                if len(cleaned) > 15 and self.is_valid_korean_address(cleaned):
                    return cleaned
        
        return None
    
    def clean_address_text(self, text):
        """Clean and normalize address text"""
        if not text:
            return ''
        
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            '주소:', '위치:', 'Address:', 'Location:', '찾아오시는길:', '오시는길:',
            '주소', '위치', 'Address', 'Location', '*', '＊'
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        
        # Remove trailing punctuation
        text = text.rstrip('.,;:')
        
        # Remove phone numbers that might be mixed in
        text = re.sub(r'\b\d{2,3}[-.\s]?\d{3,4}[-.\s]?\d{4}\b', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove standalone Korean words that are not part of addresses
        non_address_words = ['전화번호', '연락처', '문의', '예약', '상담', '진료', '영업', '운영']
        for word in non_address_words:
            text = re.sub(r'\b' + word + r'[:\s]*[^,]*', '', text)
        
        # Clean up extra spaces and commas
        text = re.sub(r'\s*,\s*,\s*', ', ', text)  # Remove double commas
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = text.strip(', ')  # Remove leading/trailing commas and spaces
        
        return text.strip()
    
    def is_valid_korean_address(self, address):
        """Validate if the extracted text looks like a Korean address"""
        if not address or len(address) < 10:
            return False
        
        # Check for Korean address indicators
        korean_indicators = [
            # Administrative divisions
            '시', '도', '구', '군', '동', '면', '읍', '리',
            # Street types
            '로', '길', '대로', 'ro', 'Road', 'Street', 'Ave', 'Avenue',
            # Building types  
            '빌딩', '타워', '센터', '병원', '의원', 'Building', 'Tower', 'Center',
            # Floor/room indicators
            '층', '호', '실', 'Floor', 'floor',
            # Major cities and areas
            '서울', '부산', '대구', '인천', '광주', '대전', '울산', '경기', '강남',
            'Seoul', 'Busan', 'Daegu', 'Incheon', 'Gwangju', 'Daejeon', 'Ulsan',
            'Gangnam', 'gu', 'Gu', 'dong', 'Dong', 'South Korea', 'Republic of Korea',
            # Common area names in clinic addresses
            'Nonhyeon', 'Teheran', 'Samseong', 'Yanghwa', 'Mapo', 'Seocho',
            'District', 'Disctrict'  # Include common typo
        ]
        
        # Must contain at least one Korean address indicator
        has_address_indicator = any(indicator in address for indicator in korean_indicators)
        
        # Should not be too long (likely not an address if over 200 characters)
        is_reasonable_length = len(address) <= 200
        
        # Should contain Korean characters OR English address format with numbers
        has_korean_chars = any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7a3' for char in address)
        has_english_address_format = bool(re.search(r'\d+.*(?:ro|Road|Street|Ave|gu|Gu|Seoul)', address, re.IGNORECASE))
        has_numbers = bool(re.search(r'\d+', address))  # Addresses should have numbers
        
        # Check for obvious non-address content
        non_address_indicators = [
            'email', '@', 'http', 'www', '전화', '연락처', 'tel:', 'phone',
            '진료시간', '영업시간', '운영시간', 'hours', 'time', 'consultation',
            '예약', 'appointment', 'booking', '문의', 'inquiry', 'call', 'contact us'
        ]
        
        has_non_address_content = any(indicator in address.lower() for indicator in non_address_indicators)
        
        # Additional check: should look like an address structure
        # Either has comma separators OR Korean address structure
        has_address_structure = (',' in address or 
                               bool(re.search(r'\d+.*(?:로|ro|Road).*(?:구|gu|Seoul)', address, re.IGNORECASE)))
        
        return (has_address_indicator and is_reasonable_length and 
                (has_korean_chars or has_english_address_format) and 
                has_numbers and not has_non_address_content and has_address_structure)

    def extract_phone(self, soup):
        """Extract phone number from various locations"""
        # Common phone selectors including Korean patterns
        phone_selectors = [
            '.phone', '.tel', '.contact-phone', '[href^="tel:"]',
            '.contact-number', '.call', '.telephone', '[class*="phone"]',
            '[class*="tel"]', '[id*="phone"]', '[id*="tel"]'
        ]
        
        for selector in phone_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'a' and element.get('href'):
                    phone = element.get('href').replace('tel:', '')
                    return phone.strip()
                phone = element.get_text().strip()
                if phone:
                    return phone
        
        # Look for phone patterns in text
        text = soup.get_text()
        
        # Korean phone patterns
        phone_patterns = [
            r'\+82[-.\s]?\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}',  # International format
            r'0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}',  # Local format
            r'\d{2,3}[-.\s]?\d{3,4}[-.\s]?\d{4}',  # Basic format
            r'010[-.\s]?\d{4}[-.\s]?\d{4}',  # Mobile format
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return ''
    
    def extract_services(self, soup):
        """Extract services/procedures offered - improved for Korean sites"""
        services = []
        
        # Look for service lists with more selectors
        service_selectors = [
            '.services li', '.procedures li', '.treatments li',
            '.service-list li', '.treatment-list li', '.menu li',
            '.procedure-list li', '.surgery-list li', '.care-list li',
            '[class*="service"] li', '[class*="treatment"] li',
            '.nav-menu li a', '.main-menu li a'  # Sometimes in navigation
        ]
        
        for selector in service_selectors:
            elements = soup.select(selector)
            for el in elements:
                text = el.get_text().strip()
                if text and len(text) < 100:  # Avoid very long text
                    services.append(text)
        
        # Look for services in div/span elements too
        service_div_selectors = [
            '.service-item', '.treatment-item', '.procedure-item',
            '[class*="service-"]', '[class*="treatment-"]'
        ]
        
        for selector in service_div_selectors:
            elements = soup.select(selector)
            for el in elements:
                text = el.get_text().strip()
                if text and len(text) < 100:
                    services.append(text)
        
        # Look for common Korean plastic surgery terms
        if not services:
            text = soup.get_text()
            korean_procedures = [
                '성형외과', '피부과', '보톡스', '필러', '리프팅', '레이저',
                '쌍꺼풀', '코성형', '안면윤곽', '가슴성형', '지방흡입',
                'Botox', 'Filler', 'Lifting', 'Laser', 'Rhinoplasty',
                'Blepharoplasty', 'Breast', 'Liposuction', 'Facelift'
            ]
            
            for procedure in korean_procedures:
                if procedure in text:
                    services.append(procedure)
        
        # Remove duplicates and clean up
        services = list(set(services))
        services = [s for s in services if len(s.strip()) > 2]  # Remove very short items
        
        return services[:10]  # Limit to 10 services to avoid clutter
    
    def scrape_directory_page(self, directory_url):
        """Scrape a directory page to find clinic URLs"""
        try:
            response = self.session.get(directory_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find clinic links - customize based on directory structure
            clinic_links = []
            
            # Common patterns for clinic links
            link_selectors = [
                'a[href*="clinic"]',
                'a[href*="hospital"]',
                '.clinic-item a',
                '.listing a'
            ]
            
            for selector in link_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(directory_url, href)
                        clinic_links.append(full_url)
            
            return list(set(clinic_links))  # Remove duplicates
            
        except Exception as e:
            print(f"Error scraping directory {directory_url}: {str(e)}")
            return []
    
    def scrape_multiple_clinics(self, urls, delay=2):
        """Scrape multiple clinic URLs with delay"""
        for i, url in enumerate(urls):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            
            clinic_data = self.scrape_clinic_page(url)
            if clinic_data:
                self.clinics.append(clinic_data)
                print(f"✓ Scraped: {clinic_data['name']}")
                if clinic_data['address']:
                    print(f"  Address: {clinic_data['address']}")
                else:
                    print(f"  ⚠️ No address found")
            
            # Be respectful - add delay between requests
            if i < len(urls) - 1:  # Don't sleep after last request
                time.sleep(delay)
    
    def save_to_csv(self, filename='clinics.csv'):
        """Save scraped data to CSV"""
        if not self.clinics:
            print("No data to save")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'phone', 'address', 'services', 'description', 'url', 'scraped_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for clinic in self.clinics:
                # Convert services list to string
                clinic_copy = clinic.copy()
                clinic_copy['services'] = ', '.join(clinic['services']) if clinic['services'] else ''
                writer.writerow(clinic_copy)
        
        print(f"Saved {len(self.clinics)} clinics to {filename}")
    
    def save_to_json(self, filename='clinics.json'):
        """Save scraped data to JSON"""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.clinics, jsonfile, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.clinics)} clinics to {filename}")

# Example usage
if __name__ == "__main__":
    scraper = ClinicScraper()
    
    # Test URLs for Korean plastic surgery clinics
    test_urls = [
        "https://www.jkplastic.com/en/",
        "https://faceplusclinic.com/",
        "https://enlienjang.com/",
        "https://eng.banobagi.com/",
        "https://www.vippskorea.com/",
        "https://jwbeauty.net/",
        "https://cdubeauty.com/",
        "https://en.atopps.com/index.php",
        "https://braunps.com/",
        "https://www.nanaprs.com/",
        "https://www.girinpsen.com/",
        "https://jwbeauty.net/",
        "https://www.linkpskorea.com/",
        "https://www.viewplasticsurgery.com/",
        "http://biopskorea.com/global/eng.html",
        "https://seoulcosmeticsurgery.com/",
        "https://answerplasticsurgery.com/",
        "https://en.chiups.com/",
        "https://www.meclinic.net/",
        "https://abplasticsurgerykorea.com/",
        "https://wonjinbeauty.com/en/main/main.php",
        "https://en.stkorea.co.kr/",
        "https://eng.idhospital.com/",
        "https://en.1mmps.com/"
    
    ]
    
    scraper.scrape_multiple_clinics(test_urls)
    scraper.save_to_json('improved_test.json')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import re
import time
import csv
from urllib.parse import urljoin, urlparse
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class EmailScraperProwebline:
    def __init__(self, headless=True, use_threading=False):
        self.emails = {}
        self.visited_urls = set()
        self.company_data = {}
        self.use_threading = use_threading
        self.headless = headless
        self.lock = threading.Lock()
        if not use_threading:
            self.setup_driver(headless)
        else:
            self.driver = None
        
    def setup_driver(self, headless):
        print("[*] Setting up browser...")
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.cookies": 1,
            "profile.cookie_controls_mode": 0
        })
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("[+] Browser ready")
        except Exception as e:
            print(f"[X] Error setting up browser: {e}")
            raise
        
    def extract_emails(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = re.findall(email_pattern, text, re.IGNORECASE)
        
        filtered = []
        invalid_patterns = ['example.com', '@example', '.png', '.jpg', '.gif', 
                          'sampleemail', 'youremail', 'noreply', 'no-reply']
        
        common_prefixes = ['info', 'contact', 'kontakt', 'hello', 'hi', 
                          'mail', 'office', 'support', 'service', 'sales']
        
        for email in found_emails:
            email_lower = email.lower()
            if not any(inv in email_lower for inv in invalid_patterns):
                prefix = email_lower.split('@')[0]
                if any(p in prefix for p in common_prefixes):
                    filtered.append(email)
        
        return filtered
    
    def extract_phone(self, text):
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return None

    def search_duckduckgo(self, query, max_results=5):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            params = {'q': query}
            resp = requests.get('https://duckduckgo.com/html/', params=params, headers=headers, timeout=12)
            urls = []
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for a in soup.select('a.result__a'):
                    href = a.get('href')
                    if not href:
                        continue
                    # DuckDuckGo sometimes wraps URLs with '/l/?' redirector
                    if href.startswith('/l/?'):
                        # Attempt to extract target URL from 'uddg' param
                        parsed = urlparse(href)
                        qs = dict([p.split('=') for p in parsed.query.split('&') if '=' in p])
                        target = qs.get('uddg')
                        if target:
                            href = requests.utils.unquote(target)
                    # Basic cleanup
                    href = href.split('#')[0]
                    skip_hosts = ['google.com', 'gstatic.com']
                    if not any(sh in href.lower() for sh in skip_hosts):
                        urls.append(href)
                    if len(urls) >= max_results:
                        break
            return urls
        except Exception:
            return []

    def scrape_page_for_emails(self, url, timeout=12):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code >= 200 and resp.status_code < 300:
                emails = self.extract_emails(resp.text)
                return emails
        except Exception:
            pass
        return []
    
    def scrape_google_maps(self, query, max_results=20):
        print(f"\n[*] Google Maps search: '{query}'")
        websites = []
        
        try:
            search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            self.driver.get(search_url)
            
            print("[*] Waiting for search results...")
            time.sleep(4)
            
            print("[*] Looking for company entries...")
            
            result_selectors = [
                "a[href*='/maps/place/']",
                "div.Nv2PK a",
                "a.hfpxzc",
                "div[role='article'] a"
            ]
            
            result_links = []
            for selector in result_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        result_links = links
                        print(f"   [+] Found with selector: {selector}")
                        break
                except:
                    continue
            
            print(f"[>] {len(result_links)} companies found")
            
            if len(result_links) > 0:
                try:
                    print("[*] Loading more results...")
                    for _ in range(2):
                        self.driver.execute_script("window.scrollBy(0, 1000)")
                        time.sleep(1)
                except:
                    pass
            
            for i, link in enumerate(result_links[:max_results], 1):
                try:
                    print(f"\n   Company {i}/{min(len(result_links), max_results)}")
                    
                    self.driver.execute_script("arguments[0].click();", link)
                    time.sleep(2)
                    
                    page_html = self.driver.page_source
                    
                    website_patterns = [
                        r'https?://(?!.*google\.com|.*facebook\.com|.*instagram\.com)[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s"<>]*)?',
                    ]
                    
                    website_url = None
                    for pattern in website_patterns:
                        matches = re.findall(pattern, page_html)
                        for match in matches:
                            skip = ['google', 'facebook', 'instagram', 'youtube', 'linkedin', 
                                   'twitter', 'gstatic', 'googleapis', 'schema.org']
                            if not any(s in match.lower() for s in skip):
                                website_url = match
                                break
                        if website_url:
                            break
                    
                    if not website_url:
                        try:
                            website_button = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                            website_url = website_button.get_attribute('href')
                        except:
                            pass
                    
                    if website_url:
                        if '/url?q=' in website_url:
                            website_url = website_url.split('/url?q=')[1].split('&')[0]
                        
                        skip = ['facebook.com', 'linkedin.com', 'instagram.com', 
                               'youtube.com', 'twitter.com']
                        
                        if not any(s in website_url.lower() for s in skip):
                            clean_url = website_url.split('?')[0].split('#')[0]
                            if clean_url not in websites:
                                websites.append(clean_url)
                                print(f"      [+] {clean_url}")
                    else:
                        # Fallback: try to find emails even if no website present
                        company_name = None
                        try:
                            company_name = link.get_attribute('aria-label') or link.text
                        except Exception:
                            pass
                        if not company_name:
                            try:
                                # Attempt to read company name from the opened place panel
                                name_candidates = self.driver.find_elements(By.CSS_SELECTOR, "h1.DUwDvf, h1[itemprop='name']")
                                if name_candidates:
                                    company_name = name_candidates[0].text
                            except Exception:
                                pass
                        if company_name:
                            fallback_query = f"{company_name} email"
                            fallback_urls = self.search_duckduckgo(fallback_query, max_results=5)
                            for furl in fallback_urls:
                                emails_from_page = self.scrape_page_for_emails(furl)
                                for em in emails_from_page:
                                    with self.lock:
                                        if em not in self.emails:
                                            self.emails[em] = furl
                                            if furl not in self.company_data:
                                                self.company_data[furl] = {
                                                    'emails': [],
                                                    'phone': None,
                                                    'address': None,
                                                    'website': furl
                                                }
                                            if em not in self.company_data[furl]['emails']:
                                                self.company_data[furl]['emails'].append(em)
                                            print(f"      [+] Fallback email: {em} ({company_name})")
                        else:
                            print(f"      [!] No website found")
                    
                except Exception as e:
                    print(f"      [X] Error: {e}")
                    continue
            
            print(f"\n[+] {len(websites)} websites extracted from Google Maps")
            
        except Exception as e:
            print(f"[X] Error with Google Maps: {str(e)}")
        
        return websites
    
    def scrape_website(self, url, driver=None):
        if url in self.visited_urls:
            return
        
        with self.lock:
            if url in self.visited_urls:
                return
            self.visited_urls.add(url)
        
        if driver is None:
            driver = self.driver
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"[*] Scanning: {url}")
                
                driver.set_page_load_timeout(30)
                driver.get(url)
                time.sleep(2)
                
                page_source = driver.page_source
                
                emails = self.extract_emails(page_source)
                phone = self.extract_phone(page_source)
                
                for email in emails:
                    if email not in self.emails:
                        with self.lock:
                            self.emails[email] = url
                            if url not in self.company_data:
                                self.company_data[url] = {
                                    'emails': [],
                                    'phone': phone,
                                    'address': None,
                                    'website': url
                                }
                            if email not in self.company_data[url]['emails']:
                                self.company_data[url]['emails'].append(email)
                            if phone and not self.company_data[url]['phone']:
                                self.company_data[url]['phone'] = phone
                        print(f"   [+] Email found: {email}")
                
                if not emails:
                    try:
                        contact_keywords = [
                            "Contact", "contact", "CONTACT",
                            "Kontakt", "kontakt",
                            "Contacto", "contacto",
                            "Contatto", "contatto",
                            "Contactez", "contactez",
                            "Impressum", "impressum",
                            "About", "about"
                        ]
                        
                        contact_links = []
                        for keyword in contact_keywords:
                            links = driver.find_elements(By.PARTIAL_LINK_TEXT, keyword)
                            contact_links.extend(links)
                        
                        for link in contact_links[:1]:
                            try:
                                href = link.get_attribute('href')
                                if href and href.startswith('http') and href not in self.visited_urls:
                                    with self.lock:
                                        self.visited_urls.add(href)
                                    driver.get(href)
                                    time.sleep(1)
                                    
                                    contact_emails = self.extract_emails(driver.page_source)
                                    for email in contact_emails:
                                        if email not in self.emails:
                                            self.emails[email] = href
                                            if href not in self.company_data:
                                                self.company_data[href] = {
                                                    'emails': [],
                                                    'phone': None,
                                                    'address': None,
                                                    'website': href
                                                }
                                            if email not in self.company_data[href]['emails']:
                                                self.company_data[href]['emails'].append(email)
                                            print(f"   [+] Email found: {email}")
                                    break
                            except:
                                continue
                    except:
                        pass
                
                break
                
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"   [!] Error, retrying ({retry_count}/{max_retries}): {str(e)}")
                    time.sleep(2)
                else:
                    print(f"   [X] Failed after {max_retries} attempts: {str(e)}")
                    break
    
    def run(self, queries, max_sites_per_query=10):
        all_websites = []
        
        if self.use_threading and self.driver is None:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.cookies": 1,
                "profile.cookie_controls_mode": 0
            })
            self.driver = webdriver.Chrome(options=chrome_options)
        
        print(f"\n[>] Collecting websites from {len(queries)} search queries...")
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'='*60}")
            print(f"Search Query {i}/{len(queries)}: {query}")
            print(f"{'='*60}")
            
            websites = self.scrape_google_maps(query, max_sites_per_query)
            all_websites.extend(websites)
            
            if i < len(queries):
                wait_time = random.uniform(3, 5)
                print(f"\n[*] Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
        
        unique_websites = list(set(all_websites))
        print(f"\n{'='*60}")
        print(f"[>] TOTAL: {len(unique_websites)} unique websites found")
        print(f"[>] Starting email extraction...")
        print(f"{'='*60}")
        
        if self.use_threading:
            print(f"[*] Using multi-threaded mode (faster)")
            
            def scrape_with_own_driver(url):
                chrome_options = Options()
                if self.headless:
                    chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                chrome_options.add_argument('--disable-notifications')
                chrome_options.add_argument('--disable-popup-blocking')
                chrome_options.add_experimental_option("prefs", {
                    "profile.default_content_setting_values.cookies": 1,
                    "profile.cookie_controls_mode": 0
                })
                
                thread_driver = webdriver.Chrome(options=chrome_options)
                try:
                    self.scrape_website(url, thread_driver)
                finally:
                    thread_driver.quit()
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(scrape_with_own_driver, url): url for url in unique_websites}
                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    if completed % 5 == 0:
                        print(f"\n[>] Progress: {completed}/{len(unique_websites)} websites scanned, {len(self.emails)} emails found")
        else:
            print(f"[*] Using single-threaded mode (slower but more stable)")
            for i, url in enumerate(unique_websites, 1):
                print(f"\n[>] Website {i}/{len(unique_websites)} ({int(i/len(unique_websites)*100)}%)")
                self.scrape_website(url)
                
                if i % 5 == 0:
                    print(f"\n[>] Progress: {len(self.emails)} emails found so far")
    
    def save_results(self, filename_prefix="recipients"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        
        valid_emails = {}
        
        for email, source_url in self.emails.items():
            email_lower = email.lower()
            prefix = email_lower.split('@')[0]
            common_prefixes = ['info', 'contact', 'kontakt', 'hello', 'hi', 
                             'mail', 'office', 'support', 'service', 'sales']
            if any(p in prefix for p in common_prefixes):
                valid_emails[email] = source_url
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            
            writer.writerow(['Name', 'Email', 'Company', 'Phone', 'Website'])
            
            for email, source_url in sorted(valid_emails.items()):
                try:
                    parsed_url = urlparse(source_url)
                    url_domain = parsed_url.netloc.replace('www.', '')
                    company_name = url_domain.split('.')[0].replace('-', ' ').title()
                except:
                    domain = email.split('@')[1]
                    company_name = domain.split('.')[0].replace('-', ' ').title()
                
                name = 'Contact'
                phone = ''
                website = source_url
                
                if source_url in self.company_data:
                    if self.company_data[source_url]['phone']:
                        phone = self.company_data[source_url]['phone']
                
                writer.writerow([name, email, company_name, phone, website])
        
        print(f"\n[+] {len(valid_emails)} business emails saved in: {filename}")
        return filename
    
    def close(self):
        if self.driver is not None:
            try:
                self.driver.quit()
            except:
                pass


def main():
    print("=" * 70)
    print("   EMAIL SCRAPER PROWEBLINE")
    print("   Google Maps Scraping with Browser Automation")
    print("=" * 70)
    
    print("\n[*] What would you like to search for?")
    print("Examples: 'Cleaning Service', 'Restaurant', 'Hotel', 'Law Firm', etc.")
    
    search_term = input("\n> Search term (optional): ").strip()
    
    preset_categories = [
        "Retail and eCommerce",
        "Healthcare and Medical Practices",
        "Education and Tutoring Services",
        "Professional Services (Lawyers, Accountants)",
        "Restaurants and Food Services",
        "Auto Repair Shops",
        "Cleaning Services",
        "Travel Agencies",
        "Freelancers (Design, Writing)",
        "Essential Businesses (Grocery, Pharmacies)",
        "Agriculture and Manufacturing",
        "Hotels and Hospitality",
        "Lawn Care and Landscaping",
        "Dance Instructors",
        "Software and SaaS",
        "Digital Marketing Agencies",
        "Web Design and Development",
        "Real Estate Agencies",
        "Gyms and Fitness",
        "Wedding Planners",
        "Photography Studios",
        "IT Services"
    ]
    
    print("\n[*] Include preset categories alongside your search term?")
    print("Press Enter to use ALL, or enter numbers comma-separated to choose.")
    for idx, cat in enumerate(preset_categories, 1):
        print(f"   {idx}. {cat}")
    cat_choice = input("> Categories (y/Enter=all, n=none, or e.g. '1,2,5'): ").strip().lower()
    include_categories = True
    selected_categories = preset_categories
    if cat_choice == 'n':
        include_categories = False
        selected_categories = []
    elif cat_choice and cat_choice != 'y':
        try:
            indices = [int(x.strip()) for x in cat_choice.split(',') if x.strip().isdigit()]
            selected_categories = [preset_categories[i-1] for i in indices if 1 <= i <= len(preset_categories)]
            include_categories = len(selected_categories) > 0
        except Exception:
            include_categories = True
            selected_categories = preset_categories
    
    if not search_term and not include_categories:
        print("[X] No search term or categories selected")
        return
    
    print("\n[*] Which region/country should be searched?")
    print("1. USA (New York, Los Angeles, Chicago, Houston, Miami)")
    print("2. UK (London, Manchester, Birmingham, Leeds)")
    print("3. Germany (Berlin, Munich, Hamburg, Frankfurt)")
    print("4. France (Paris, Lyon, Marseille, Toulouse)")
    print("5. Spain (Madrid, Barcelona, Valencia, Seville)")
    print("6. Italy (Rome, Milan, Naples, Turin)")
    print("7. Canada (Toronto, Montreal, Vancouver, Calgary)")
    print("8. Australia (Sydney, Melbourne, Brisbane, Perth)")
    print("9. Enter custom cities manually")
    print("10. Nigeria (Cities/States)")
    
    region = input("\n> Selection (1-10): ").strip()
    
    queries = []
    locations = []
    
    if region == '1':
        locations = ["New York", "Los Angeles", "Chicago", "Houston", "Miami", "Phoenix"]
    elif region == '2':
        locations = ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"]
    elif region == '3':
        locations = ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Stuttgart"]
    elif region == '4':
        locations = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"]
    elif region == '5':
        locations = ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"]
    elif region == '6':
        locations = ["Rome", "Milan", "Naples", "Turin", "Florence"]
    elif region == '7':
        locations = ["Toronto", "Montreal", "Vancouver", "Calgary", "Ottawa"]
    elif region == '8':
        locations = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"]
    elif region == '9':
        print("\n[*] Enter cities/regions (one per line, empty line to finish):")
        print("Tip: Include country if needed (e.g., 'Paris, France')")
        while True:
            city = input("> ").strip()
            if not city:
                break
            locations.append(city)
    elif region == '10':
        nigeria_cities = ["Lagos", "Abuja", "Port Harcourt", "Ibadan", "Kano", "Benin City", "Enugu", "Kaduna", "Abeokuta", "Owerri"]
        nigeria_states = ["Lagos State", "FCT Abuja", "Rivers State", "Oyo State", "Kano State", "Edo State", "Enugu State", "Kaduna State", "Ogun State", "Imo State", "Delta State", "Anambra State"]
        print("\n[*] Nigeria scope: 1=cities, 2=states, 3=both (default=1)")
        ng_scope = input("> Selection (1/2/3, default=1): ").strip()
        if ng_scope == '2':
            locations = nigeria_states
        elif ng_scope == '3':
            locations = nigeria_cities + nigeria_states
        else:
            locations = nigeria_cities
    else:
        print("[X] Invalid selection")
        return
    
    if search_term:
        queries.extend([f"{search_term} {loc}" for loc in locations])
    if include_categories and selected_categories:
        for cat in selected_categories:
            queries.extend([f"{cat} {loc}" for loc in locations])
    
    if not queries:
        print("[X] No search queries")
        return
    
    print("\n[*] How many companies per search query?")
    try:
        max_per_query = int(input("> Number (5-30): ").strip())
        max_per_query = max(5, min(30, max_per_query))
    except:
        max_per_query = 10
        print(f"[!] Using default: {max_per_query}")
    
    print("\n[*] Should the browser be visible?")
    show_browser = input("> (y/n, default=n): ").strip().lower() == 'y'
    
    print("\n[*] Use multi-threading for faster scraping?")
    print("Note: Threading is faster but uses more resources")
    use_threading = input("> (y/n, default=n): ").strip().lower() == 'y'
    
    scraper = None
    try:
        scraper = EmailScraperProwebline(headless=not show_browser, use_threading=use_threading)
        
        print(f"\n[*] Starting search...")
        print(f"[!] This may take 5-15 minutes...\n")
        
        print(f"\n[*] Scraping up to {max_per_query} companies per query across {len(queries)} queries...")
        
        scraper.run(queries, max_sites_per_query=max_per_query)
        output_file = scraper.save_results(filename_prefix="recipients")
        # Show absolute path and optionally open
        import os
        abs_path = os.path.abspath(output_file)
        print(f"\n[✓] Results saved to: {abs_path}")
        open_choice = input("Open the results file now? (y/N): ").strip().lower()
        if open_choice == 'y':
            try:
                if os.name == 'posix':
                    import subprocess
                    subprocess.run(['open', abs_path], check=False)
                else:
                    os.startfile(abs_path)
            except Exception as e:
                print(f"[!] Could not open file automatically: {e}")
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except Exception as e:
        print(f"[X] Error during scraping: {e}")
    finally:
        if scraper:
            scraper.close()
            print("\n[*] Browser closed")


if __name__ == "__main__":
    main()

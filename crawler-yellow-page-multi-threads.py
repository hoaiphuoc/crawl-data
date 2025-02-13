from bs4 import BeautifulSoup
import requests
import html
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Base headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

BASE_URL = "https://trangvangvietnam.com/categories/484645/logistics-dich-vu-logistics.html"

# Function to fetch a single page and extract company links
def get_company_links(page):
    url = f"{BASE_URL}?page={page}"
    print(f"📌 Crawling: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page {page}. Status Code: {response.status_code}")
            return []

        soup = BeautifulSoup(html.unescape(response.text), "html.parser")
        names = soup.find_all('h2', class_='p-1 fs-5 h2 m-0 pt-0 ps-0 text-capitalize')

        links = []
        for item in names:
            a_tag = item.find('a')
            if a_tag and "href" in a_tag.attrs:
                links.append(a_tag["href"].strip().replace("\t", "").replace("\n", "").replace(" ", ""))
        return links

    except requests.RequestException as e:
        print(f"❌ Error fetching page {page}: {e}")
        return []

# Function to fetch company details from a single company link
def crawl_company(link):
    try:
        comp_response = requests.get(link, headers=HEADERS, timeout=10)
        if comp_response.status_code != 200:
            print(f"⛔ Skipping {link} (Error {comp_response.status_code})")
            return None

        soup = BeautifulSoup(comp_response.content, "html.parser")

        name_tag = soup.find("h1", class_="fs-3 text-capitalize")
        phone_tag = soup.find("div", class_="pb-2 pt-0 ps-3 pe-3 m-0 fs-5") or soup.find("div", class_="p-2 ps-0 pt-0 m-0 fs-5")
        address_tag = soup.find("div", class_="pb-2 pt-0 ps-3 pe-3 m-0") or soup.find("div", class_="p-2 ps-0 pt-0 m-0")

        if not name_tag or not phone_tag or not address_tag:
            print(f"⛔ Skipping {link} (Missing Data)")
            return None

        name = name_tag.text.strip()
        phone = phone_tag.text.strip().replace("\t", "").replace("\n", "").replace(" ", "")
        address = address_tag.get_text(strip=True)

        print(f"✅ Crawled: {name}")
        return {"name": name, "phone": phone, "address": address}

    except requests.RequestException as e:
        print(f"❌ Error fetching {link}: {e}")
        return None

# Function to run multi-threaded crawling
def crawl_news_data(start_page, total_pages, max_threads=10):
    all_links = []
    
    # Fetch all links using ThreadPoolExecutor
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(get_company_links, page): page for page in range(start_page, total_pages + 1)}

        for future in as_completed(futures):
            all_links.extend(future.result())

    print(f"🔗 Total company links found: {len(all_links)}")

    # Fetch company details using ThreadPoolExecutor
    all_data = []
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(crawl_company, link): link for link in all_links}

        for future in as_completed(futures):
            result = future.result()
            if result:
                all_data.append(result)

    return all_data

# Function to export data to CSV
def export_csv(data, filename="companies-v2.csv"):
    if not data:
        print("❌ No data to export.")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'phone', 'address'])
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Extracted {len(data)} records. Data saved to {filename}")

# Run the scraper
if __name__ == "__main__":
    START_PAGE = 10
    TOTAL_PAGES = 10  # Crawl pages 1 to 19
    MAX_THREADS = 10  # Number of concurrent threads

    extracted_data = crawl_news_data(START_PAGE, TOTAL_PAGES, MAX_THREADS)
    export_csv(extracted_data)

from bs4 import BeautifulSoup
import requests
import html
import csv

def crawl_news_data(base_url, start_page, total_pages):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    all_data = []

    for page in range(start_page, total_pages + 1):
        url = f"{base_url}?page={page}"
        print(f"📌 Crawling: {url}")

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page {page}. Status Code: {response.status_code}")
            continue

        response.encoding = response.apparent_encoding  # Try auto-detecting encoding
        soup = BeautifulSoup(response.text, "html.parser")

        # Double decoding
        decoded_html = html.unescape(html.unescape(str(soup)))
        soup = BeautifulSoup(decoded_html, "html.parser")
        # print(soup.prettify())
        names = soup.find_all('h2', class_='p-1 fs-5 h2 m-0 pt-0 ps-0 text-capitalize')

        links = []
        for item in names:
            a_tag = item.find('a')
            if a_tag and "href" in a_tag.attrs:
                links.append(a_tag["href"].strip().replace("\t", "").replace("\n", "").replace(" ", ""))

        for link in links:
            try:
                comp_response = requests.get(link, headers=headers)
                if comp_response.status_code != 200:
                    print(f"⛔ Skipping {link} due to response error ({comp_response.status_code})")
                    continue

                soup = BeautifulSoup(comp_response.content, "html.parser")

                name_tag = soup.find("h1", class_="fs-3 text-capitalize")
                phone_tag = soup.find("div", class_="pb-2 pt-0 ps-3 pe-3 m-0 fs-5") or soup.find("div", class_="p-2 ps-0 pt-0 m-0 fs-5")
                address_tag = soup.find("div", class_="pb-2 pt-0 ps-3 pe-3 m-0") or soup.find("div", class_="p-2 ps-0 pt-0 m-0")

                if not name_tag or not phone_tag or not address_tag:
                    print(f"⛔ Skipping {link} due to missing data")
                    continue

                name = name_tag.text.strip()
                phone = phone_tag.text.strip().replace("\t", "").replace("\n", "").replace(" ", "")
                address = address_tag.get_text(strip=True)

                all_data.append({
                    "name": name,
                    "phone": phone,
                    "address": address,
                })
                print(f"✅ Crawled: {name}")

            except requests.RequestException as e:
                print(f"❌ Error fetching {link}: {e}")

    return all_data

def export_csv(data, filename="companies.csv"):
    if not data:
        print("❌ No data to export.")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'phone','address'])
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Extracted {len(data)} records. Data exported to {filename}")

if __name__ == "__main__":
    BASE_URL = "https://trangvangvietnam.com/categories/484645/logistics-dich-vu-logistics.html"
    START_PAGE = 1
    TOTAL_PAGES = 19  # Crawl from page 1 to 19

    extracted_data = crawl_news_data(BASE_URL, START_PAGE, TOTAL_PAGES)
    export_csv(extracted_data)

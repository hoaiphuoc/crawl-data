from bs4 import BeautifulSoup
import requests
import csv

def crawNewsData(baseUrl, url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    titles = soup.find_all('h3', class_='box-title-text')
    links = [link.find('a').attrs["href"] for link in titles]
    data = []
    for link in links:
        try:
            news = requests.get(baseUrl + link)
            soup = BeautifulSoup(news.content, "html.parser")
            title = soup.find("h1", class_="article-title").text
            abstract = soup.find("h2", class_="detail-sapo").text
            body = soup.find("div", class_="detail-content")
            content = ""
            try:
                content = body.findChildren("p", recursive=False)[0].text + body.findChildren("p", recursive=False)[1].text
            except:
                content = ""
            image = body.find("img").attrs["src"]
            data.append({
                "title": title,
                "abstract": abstract,
                "content": content,
                "image": image,
            })
            print("craw " + title)
        except:
            continue
    return data

def makeFastNews(data):
    with open('posts.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'image', 'abstract', 'content'])
        writer.writeheader()
        for post in data:
            writer.writerow(post)

    print(f"Extracted {len(data)} Data. Data exported to posts.csv")


if __name__ == "__main__":
    makeFastNews(crawNewsData("https://tuoitre.vn", "https://tuoitre.vn/tin-moi-nhat.htm"))
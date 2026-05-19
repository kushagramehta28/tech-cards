import requests
from bs4 import BeautifulSoup

TARGET_PUBLISHERS = {
    "ArsTechnica",
    "The Verge",
    "Bleeping Computer",
    "Phoronix"
}

# thebrutalistreport provides us with the daily links to our core publishers' articles
def scrape_brutalist_report():
    url = "https://brutalist.report/topic/tech"
    
    # Make a GET request to the URL and add a User-Agent header to mimic a browser
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    # Use html.parser to parse the HTML content of the page
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    # Main container
    brutal_grid = soup.find("div", class_="brutal-grid")

    if not brutal_grid: # If the main container is not found, return an empty list
        print("Main container not found.")
        return results
    
    # Each child div = one publisher section
    publisher_divs = brutal_grid.find_all("div", recursive=False)

    for publisher_div in publisher_divs:

        # Publisher name from h3
        h3 = publisher_div.find("h3")

        if not h3:
            continue

        publisher_name = h3.get_text(strip=True)

        # Skip unwanted publishers
        if publisher_name not in TARGET_PUBLISHERS:
            continue

        # Find all article links inside ul
        ul = publisher_div.find("ul")

        if not ul:
            continue

        links = ul.find_all("a", href=True)

        for link in links:

            title = link.get_text(strip=True)
            article_url = link["href"]

            results.append({
                "publisher": publisher_name,
                "title": title,
                "url": article_url
            })

    return results
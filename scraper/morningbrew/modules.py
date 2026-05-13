import sys
sys.path.append('../../CloudflareBypassForScraping-main')  # Go two levels up and then into the folder

from CloudflareBypasser import CloudflareBypasser 
from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup
from transformers import pipeline

def start_browser():
    # Initialize ChromiumPage
    driver = ChromiumPage()
    driver.get('http://www.morningbrew.com/tag/tech')

    # Bypass Cloudflare protection
    cf_bypasser = CloudflareBypasser(driver) 
    cf_bypasser.bypass()

    return driver 

def see_more(driver):
    # Find and click the 'See More' button by tag and text (5 times)
    for _ in range(5):
        see_more_btn = driver.ele('tag:button@class=Button__StyledButton-sc-44e5f0-0 cIZEHT btn btn-primary')
        if see_more_btn:
            print('See More button found, clicking...')
            see_more_btn.click()
        else:
            print('See More button not found.')

def get_links(driver):
    # Get all article links
    elements = driver.eles('tag:a@class=style__PreviewCardLink-sc-939db8c6-0 HcAsw preview')
    links = []
    for element in elements:
        href = element.attr('href')
        links.append(href)
    return links

def browser_quit(driver):
    driver.quit()

def read_html(driver, url):
    driver.get(url)
    html = driver.html
    return html

def parse_html(html):
    soup = BeautifulSoup(html, 'lxml')
    # extract title 
    title = soup.find('h1').text if soup.find('h1') else None
    # extract content
    content_div = soup.find('div', id = 'article-body-content')
    content = content_div.text.strip() if content_div else None
    # extract author
    article_info = soup.find('div', id = 'article-details')
    author = article_info.find('a').text if article_info and article_info.find('a') else None
    # extract date
    date = article_info.find('time').text if article_info and article_info.find('time') else None
    # source
    source = 'Morning Brew'
    # extract image url
    img_div = soup.find('figure') 
    img_url = img_div.find('img')['src'] if img_div else None

    #Let's contain it in dictionary
    all_info = {
        'title': title,
        'author': author,
        'date': date,
        'image_url': img_url,
        'source': source,
        'content': content
    }
    return all_info

def summarize_text(text):
    # Set up the summarization pipeline
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    # Generate summary between 80 to 110 tokens ~ 60-80 words
    summary = summarizer(text, max_length=110, min_length=80, do_sample=False)
    return summary[0]['summary_text']
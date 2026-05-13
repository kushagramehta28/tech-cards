import modules

# Start the browser and bypass Cloudflare
driver = modules.start_browser()

# Click the 'See More' button multiple times to load more articles
modules.see_more(driver)

# Extract article links
links = modules.get_links(driver)

# Extract HTML from each link
for link in links:
    html_content = modules.read_html(driver, link)
    info = modules.parse_html(html_content)
    summary = modules.summarize_text(info['content'])
    print("Title:", info['title'])
    print("Author:", info['author'])
    print("Date:", info['date'])
    print("Image URL:", info['image_url'])
    print("Source:", info['source'])
    print("Content Summary:", summary)

# Quit the browser
modules.browser_quit(driver)
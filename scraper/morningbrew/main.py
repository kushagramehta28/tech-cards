import modules

# Start the browser and bypass Cloudflare
driver = modules.start_browser()

# Click the 'See More' button to load more articles
modules.see_more(driver)

# Extract article links
links = modules.link_builder(driver)

# Fetch JSON data for each article and parse it
for link in links:
    json_data = modules.fetch_json(driver, link)
    # Parse and print the article details
    modules.json_parser(json_data)

# Quit the browser
modules.browser_quit(driver)
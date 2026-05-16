import modules

# Start the browser and bypass Cloudflare
driver = modules.start_browser()

# Click the 'See More' button to load more articles
modules.see_more(driver)

# Extract article links
links = modules.link_builder(driver)

# Fetch JSON data for each article and process it
for link in links:
    json_data = modules.fetch_json(driver, link)

    result = modules.controller(json_data)

    if result == "url_duplicate":
        print(f"Duplicate article found for URL: {link}")
        print("Stopping scraper.")
        break

    elif result == "semantic_duplicate":
        print(f"Semantic duplicate found for URL: {link}")
        print("Skipping article.")
        continue

    elif result == "inserted":
        print(f"Article inserted for URL: {link}")

# Quit the browser
modules.browser_quit(driver)
import requests
from bs4 import BeautifulSoup
import json
import os
import urllib.parse

# Configuration
DATA_FILE = "scraped_data.json"
ITEMS_FILE = "items.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1350036168875446292/Is8lBpcA9ByJLUO7rYW0-LJzl33fF6FEAnH_j3l4laUpsBay6N5tSTekqDrdFMZ2Xe7o"  # replace with your webhook URL

def load_data(filename):
    """Load previously scraped data from a JSON file."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_data(data, filename):
    """Save scraped data to a JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_items(filename):
    """Load the items configuration from a JSON file."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        print(f"Items file {filename} not found!")
        return {"search": [], "item": []}

def send_discord_notification(message, webhook_url):
    """Send a simple message to Discord via a webhook."""
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Notification sent successfully.")
    else:
        print("Failed to send notification:", response.text)

def format_price(price):
    """Ensure the price string starts with a '$'."""
    if price and not price.strip().startswith("$"):
        return "$" + price.strip()
    return price

def extract_product_id(url):
    """Extract the product id from a URL.
       For example, from '/pokemon/.../1754027' it returns '1754027'.
    """
    parts = url.strip("/").split("/")
    return parts[-1] if parts else None

def scrape_search_page(url):
    """
    Scrape a search‑based page.
    Iterates over each product card (div with class "product-col") and extracts:
      - Product name from <a class="card-text">
      - Product URL and product id (from the href)
      - Price from either the mobile container (div with class "product-add-container d-sm-none") 
        or, if not found, from the desktop container (div with class "buying-options-container")
      - Stock status determined by checking if a "btn-add-to-cart" button is present.
    """
    results = []
    while url:
        print("Scraping search page:", url)
        resp = requests.get(url)
        if resp.status_code != 200:
            print("Failed to retrieve page:", url)
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Find all product card containers
        product_cols = soup.find_all("div", class_="product-col")
        if not product_cols:
            print("No products found on this page, ending pagination.")
            break
        
        for col in product_cols:
            name_a = col.find("a", class_="card-text")
            if not name_a:
                continue
            product_name = name_a.get_text(strip=True)
            relative_url = name_a.get("href")
            full_url = "https://www.trollandtoad.com" + relative_url
            product_id = extract_product_id(relative_url)
            
            # Initialize price and stock
            price = None
            in_stock = False
            
            # Attempt to extract from mobile container first
            mobile_container = col.find("div", class_="product-add-container d-sm-none")
            if mobile_container:
                # Look for a div whose text starts with '$'
                for div in mobile_container.find_all("div"):
                    txt = div.get_text(strip=True)
                    if txt.startswith("$"):
                        price = txt
                        break
                if mobile_container.find("button", class_="btn-add-to-cart"):
                    in_stock = True
                else:
                    in_stock = False
            
            # Fallback to desktop container if price not found
            if not price:
                desktop_container = col.find("div", class_="buying-options-container")
                if desktop_container:
                    table = desktop_container.find("div", class_="buying-options-table")
                    if table:
                        for div in table.find_all("div"):
                            txt = div.get_text(strip=True)
                            if txt.startswith("$"):
                                price = txt
                                break
                        select = table.find("select", attrs={"name": "qtyToBuy"})
                        if select and select.has_attr("disabled"):
                            in_stock = False
                        else:
                            in_stock = True

            results.append({
                "product_id": product_id,
                "name": product_name,
                "product_url": full_url,
                "price": price,
                "in_stock": in_stock
            })
        
        # Handle pagination: Look for the "nextPage" div
        next_page_div = soup.find("div", class_="nextPage")
        if next_page_div and next_page_div.has_attr("data-page"):
            if "hide2" in next_page_div.get("class", []):
                print("Next page link is hidden (only one page). Stopping pagination.")
                break
            next_page_number = next_page_div["data-page"]
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "page-no" in qs:
                qs["page-no"] = [next_page_number]
            elif "page" in qs:
                qs["page"] = [next_page_number]
            else:
                qs["page"] = [next_page_number]
            new_query = urllib.parse.urlencode(qs, doseq=True)
            new_url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            if new_url == url:
                print("Next page URL is the same as current. Stopping pagination.")
                break
            url = new_url
        else:
            url = None

    return results

def scrape_item_page(url):
    """
    Scrape an item‑based page.
    It extracts:
      - The item name (from the h1 with class "product-name"),
      - The price (from the span with id "sale-price"),
      - The stock status (by checking the presence of the "addToCart" button),
      - And the card picture (from the div with id "main-prod-img").
    """
    print("Scraping item page:", url)
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Failed to retrieve page:", url)
        return None
    soup = BeautifulSoup(resp.text, "html.parser")

    name_elem = soup.find("h1", class_="product-name")
    name = name_elem.get_text(strip=True) if name_elem else "Unknown"

    price_elem = soup.find("span", id="sale-price")
    price = price_elem.get_text(strip=True) if price_elem else None

    in_stock = True if soup.find("button", class_="addToCart") else False

    picture_url = None
    img_div = soup.find("div", id="main-prod-img")
    if img_div:
        img_tag = img_div.find("img")
        if img_tag and img_tag.has_attr("src"):
            picture_url = img_tag["src"]

    product_id = extract_product_id(url)
    return {
        "product_id": product_id,
        "name": name,
        "price": price,
        "in_stock": in_stock,
        "product_url": url,
        "picture": picture_url
    }

def compare_and_notify(old_data, new_data):
    """
    Compare old scraped data with new data.
    If a price drop or a change from out‑of‑stock to in‑stock is detected,
    send a notification that includes additional data (like name and picture if available).
    Also, when a product is new (not found in the stored data), send a notification
    to indicate that we are now watching the new product.
    """
    for pid, new_info in new_data.items():
        old_info = old_data.get(pid)
        stock_str_new = "Available" if new_info["in_stock"] else "None"
        
        if old_info:
            try:
                # Remove "$" and commas from the price string
                old_price = float(old_info["price"].replace("$", "").replace(",", "")) if old_info["price"] else None
                new_price = float(new_info["price"].replace("$", "").replace(",", "")) if new_info["price"] else None
            except Exception:
                old_price, new_price = None, None

            price_dropped = (old_price and new_price and new_price < old_price)
            became_in_stock = (not old_info["in_stock"] and new_info["in_stock"])
            if price_dropped or became_in_stock:
                header = "# Product Update"
                stock_str_old = "Available" if old_info["in_stock"] else "None"
                new_price_formatted = format_price(new_info["price"])
                old_price_formatted = format_price(old_info["price"])
                message = (
                    f"{header}\n"
                    f"**{new_info['name']}**\n"
                    f"* Price: {new_price_formatted} (was {old_price_formatted})\n"
                    f"* Stock: {stock_str_new} (was {stock_str_old})\n\n"
                    f"Link: {new_info['product_url']}"
                )
                send_discord_notification(message, DISCORD_WEBHOOK_URL)
        else:
            header = "# Watching New Product"
            new_price_formatted = format_price(new_info["price"])
            message = (
                f"{header}\n"
                f"**{new_info['name']}**\n"
                f"* Price: {new_price_formatted}\n"
                f"* Stock: {stock_str_new}\n\n"
                f"Link: {new_info['product_url']}"
            )
            send_discord_notification(message, DISCORD_WEBHOOK_URL)

def main():
    # Load previously stored scraped data and items to monitor
    stored_data = load_data(DATA_FILE)
    items = load_items(ITEMS_FILE)
    new_data = {}

    # ---- Search-based variant ----
    for search_url in items.get("search", []):
        search_results = scrape_search_page(search_url)
        for item in search_results:
            new_data[item["product_id"]] = item

    # ---- Item-based variant ----
    for item_url in items.get("item", []):
        item_result = scrape_item_page(item_url)
        if item_result:
            new_data[item_result["product_id"]] = item_result

    # Compare stored data with new data and notify if changes are detected
    compare_and_notify(stored_data, new_data)

    # Save new data for the next run
    save_data(new_data, DATA_FILE)

if __name__ == "__main__":
    main()

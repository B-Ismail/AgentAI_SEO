import json
import re
import requests
import time

from streamlit import session_state

# Extract domain from user prompt
def extract_domain(user_input: str) -> str:
    pattern = r"https?://[a-zA-Z0-9./-]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    matches = re.findall(pattern, user_input)
    return matches[0] if matches else None

# Make the API request to fetch SEO data
def make_api_request(domain):
    url = "https://similarweb-insights.p.rapidapi.com/similar-sites"
    querystring = {"domain": domain}
    headers = {
        "x-rapidapi-key": "15fdc58102mshfcda37031cb00d7p1a6b47jsn12d8c5ac4e67",
        "x-rapidapi-host": "similarweb-insights.p.rapidapi.com"
    }
    start_time = time.time()
    response = requests.get(url, headers=headers, params=querystring)
    response_time = time.time() - start_time
    response.raise_for_status()
    return response.json(), response_time

# Parse the main site information from the response
def parse_main_site_info(site_data):
    return {
        "domain": site_data.get("Domain", "Unknown domain"),
        "title": site_data.get("Title", "No title found"),
        "description": site_data.get("Description", "No description found"),
        "category": site_data.get("Category", "No category found"),
        "visits": site_data.get("Visits", 0),
        "tags": site_data.get("Tags", [])
    }

# Parse similar sites from the response
def parse_similar_sites(site_data):
    similar_sites = []
    for site in site_data.get("SimilarSites", []):
        similar_sites.append({
            "domain": site.get("Domain", "Unknown domain"),
            "title": site.get("Title", "No title"),
            "description": site.get("Description", "No description"),
            "visits": site.get("Visits", 0),
            "top_country": site.get("TopCountry", {}).get("CountryName", "Unknown country"),
        })
    return similar_sites

# Parse image data from the response
def parse_image_data(site_data):
    images = site_data.get("Images", {})
    return {
        "favicon": images.get("Favicon", "No favicon"),
        "desktop": images.get("Desktop", "No desktop image"),
        "smartphone": images.get("Smartphone", "No smartphone image")
    }

# Save SEO data to a text file
def save_seo_data_to_file(seo_data: dict, file_name: str = "seo_data.txt"):
    try:
        with open(file_name, "w") as file:
            file.write("SEO Data Summary\n")
            file.write("=================\n")
            file.write(f"Domain: {seo_data.get('domain', 'Unknown domain')}\n")
            file.write(f"Title: {seo_data.get('title', 'No title found')}\n")
            file.write(f"Description: {seo_data.get('description', 'No description found')}\n")
            # Format tags as a comma-separated string
            tags = ", ".join(seo_data.get('tags', [])) if seo_data.get('tags') else "No tags found"
            file.write(f"Key Words: {tags}\n")
            file.write(f"Category: {seo_data.get('category', 'No category found')}\n")
            file.write(f"Visits: {seo_data.get('visits', 0)}\n")
            file.write(f"Response Time: {seo_data.get('response_time', 0):.2f} seconds\n")
            file.write("\nSimilar Sites:\n")
            for site in seo_data.get("similar_sites", []):
                file.write(f"- {site['domain']}: {site['title']}\n")
        return True
    except Exception as e:
        return False

# Main function to fetch and extract SEO data
def fetch_seo_data(user_prompt, session_state, save_to_file: bool = False):
    try:
        domain = extract_domain(user_prompt)
        if domain:
            # Make API request and measure response time
            site_data, response_time = make_api_request(domain)

            # Process site data
            main_info = parse_main_site_info(site_data)
            similar_sites = parse_similar_sites(site_data)
            #images = parse_image_data(site_data)

            seo_data = {
                **main_info,
                #"images": images,
                "similar_sites": similar_sites,
                "response_time": response_time  # Include response time in the data
            }

            # Save to file if requested
            if save_to_file:
                saved = save_seo_data_to_file(seo_data)
                if not saved:
                    session_state["last_seo_data"] = None
                    return {"error": "Failed to save SEO data to file."}

            # Update session state
            session_state["last_seo_data"] = seo_data

            return seo_data  # Return the dictionary directly

        # If no domain is found
        session_state["last_seo_data"] = None
        return None

    except requests.exceptions.RequestException as e:
        session_state["last_seo_data"] = None
        return {"error": f"Failed to fetch data from API: {e}"}

    except Exception as e:
        session_state["last_seo_data"] = None
        return {"error": f"Failed to process site data: {e}"}


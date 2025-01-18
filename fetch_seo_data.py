import re
import requests
import time

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

# Main function to fetch and extract SEO data
def fetch_seo_data(user_prompt):
    try:
        domain = extract_domain(user_prompt)
        site_data, response_time = make_api_request(domain)

        main_info = parse_main_site_info(site_data)
        similar_sites = parse_similar_sites(site_data)
        images = parse_image_data(site_data)

        return {
            **main_info,
            "images": images,
            "similar_sites": similar_sites,
            "response_time": response_time  # Add response time to the output
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch data from API: {e}"}
    except Exception as e:
        return {"error": f"Failed to process site data: {e}"}

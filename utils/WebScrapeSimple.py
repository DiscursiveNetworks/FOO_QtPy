import requests
from bs4 import BeautifulSoup

def scrape_clean_text(url, output_file):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'iframe', 'noscript', 'svg']):
            tag.decompose()
        
        # Remove elements that are likely ads
        for ad_class in ['ad', 'advert', 'sponsor', 'promotion', 'banner']:
            for tag in soup.find_all(class_=lambda c: c and ad_class in c.lower()):
                tag.decompose()
        
        # Extract remaining text
        text = soup.get_text(separator='\n', strip=True)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(text)
        
        print(f"Clean content saved to {output_file}")
    else:
        print(f"Failed to retrieve page. Status code: {response.status_code}")

# Example usage
if __name__ == "__main__":
    url = "https://plasmodb.org/plasmo/app/static-content/PlasmoDB/mahpic.html"
    output_file = "WebScrapeSimple.txt"
    scrape_clean_text(url, output_file)

import requests
from bs4 import BeautifulSoup


def get_html_content(url):
    """
    Retrieves the HTML content of the provided webpage, and 
    returns it. If the status code is not 200, returns None.
    """
    response = requests.get(url)
    return response.content if response.status_code == 200 else None


def parse_html_content(html_content):
    """
    Parses the HTML content using BeautifulSoup, and
    returns it. If the HTML content is empty, returns None.
    """
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    return None


def extract_experiences(soup):
    """
    Extracts the experiences from the parsed HTML content, and
    returns a list of dictionaries, where each dictionary contains
    the following keys:
    - link: URL of the experience.
    - image: URL of the image of the experience.
    - title: Title of the experience.
    - brand: Brand of the experience.
    - status: Status of the experience (Available or Sold Out).
    - points: Points required to redeem the experience.
    """
    if soup:
        # Section that contains a list of all experiences.
        sf_main_section = soup.find('section', class_='sf-main')
        
        if sf_main_section:
            # List of experiences.
            sf_list = sf_main_section.find('ul', class_='sf-list')
            
            if sf_list:
                # List items with class 'sf-item'.
                sf_items = sf_list.find_all('li', class_='sf-item')
                experiences = []
                
                for item in sf_items:
                    link_tag = item.find('a', class_='sf-item-wrapper')
                    link = link_tag['href'] if link_tag else 'N/A'
                    
                    image_tag = item.find('img', class_='sf-item-image')
                    image = image_tag['src'] if image_tag else 'N/A'
                    
                    title_tag = item.find('h2', class_='font-semibold')
                    title = title_tag.text if title_tag else 'N/A'
                    
                    brand_tag = item.find('div', class_='sf-item-brand')
                    brand = brand_tag.text.strip() if brand_tag else 'N/A'
                    
                    status_tag = item.find('span', class_='label-color-sold-out')
                    status = status_tag.text if status_tag else 'Available'
                    
                    points_tag = item.find('p', class_='sf-item-details')
                    points = points_tag.find('span').text if points_tag and points_tag.find('span') else 'N/A'
                    
                    experience = {
                        'link': link,
                        'image': image,
                        'title': title,
                        'brand': brand,
                        'status': status,
                        'points': points
                    }
                    
                    experiences.append(experience)
                
                return experiences
            else:
                return None
        else:
            return None
    else:
        return None
    

url = 'https://loja.meo.pt/sensacoes-meos'

def main():
    html_content = get_html_content(url)
    soup = parse_html_content(html_content)
    experiences = extract_experiences(soup)
    
    if experiences:
        for exp in experiences:
            # Print the extracted experiences
            print(f"Title: {exp['title']}")
            print(f"Brand: {exp['brand']}")
            print(f"Status: {exp['status']}")
            print(f"Points: {exp['points']}")
            print(f"Link: {exp['link']}")
            print(f"Image: {exp['image']}")
            print('-' * 20)
    else:
        print('No experiences found!')


if __name__ == '__main__':
    main()

import requests
from bs4 import BeautifulSoup
import json


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

                    #----------------------------------------------------
                    # Body 
                    #----------------------------------------------------
                    item_body = item.find('div', class_='sf-item-body')
                    
                    item_image = item_body.find('div', class_='sf-item-image')
                    image = item_image.find('img')['src'] if item_image else 'N/A'
                    
                    item_details = item_body.find('div', class_='sf-item-details')

                    item_brand = item_details.find('div', class_='sf-item-brand')
                    brand = item_brand.find('p')['title'] if item_brand else 'N/A'

                    item_title = item_details.find('div', class_='sf-item-name')
                    title = item_title.find('h2')['title'] if item_title else 'N/A'
                    #----------------------------------------------------

                    status_tag = item.find('span', class_='label-color-sold-out')
                    status = status_tag.text if status_tag else 'Disponível'
                    
                    #----------------------------------------------------
                    # Footer
                    #----------------------------------------------------
                    item_footer = item.find('div', class_='sf-item-footer')

                    item_points = item_footer.find('p', class_='sf-item-details')
                    points = item_points.find('span').text if item_points and item_points.find('span') else 'N/A'
                    #----------------------------------------------------

                    experience = {
                        'link': link,
                        'title': title,
                        'image': image,
                        'brand': brand,
                        'status': status,
                        'points': f"{points} MEOS"
                    }
                    
                    experiences.append(experience)

                # Sort experiences such that the available ones come first
                experiences = sorted(experiences, key=lambda x: x['status'] == 'Esgotado')
                
                return experiences
            else:
                return None
        else:
            return None
    else:
        return None


def save_experiences_to_json(experiences, filename):
    """
    Saves the list of experiences to a JSON file.
    """
    data = {'experiences': experiences}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    

url = 'https://loja.meo.pt/sensacoes-meos'

def main():
    html_content = get_html_content(url)
    soup = parse_html_content(html_content)
    experiences = extract_experiences(soup)
    
    if experiences:
        save_experiences_to_json(experiences, 'experiences.json')
    else:
        print('No experiences found!')


if __name__ == '__main__':
    main()

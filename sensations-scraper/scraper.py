import requests
import discord
import asyncio
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv


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


def get_current_experiences():
    """
    Retrieves the current experiences from the MEO Sensations webpage,
    and returns them as a list of dictionaries.
    """
    html_content = get_html_content(URL)
    soup = parse_html_content(html_content)
    experiences = extract_experiences(soup)
    
    return experiences


def save_experiences_to_json(experiences, filename):
    """
    Saves the list of experiences to a JSON file.
    """
    data = {'experiences': experiences}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    

def get_new_experiences(experiences_old, experiences_new):
    """
    Returns the experiences that are not present in the old experiences list.
    """
    old_links = {experience['link'] for experience in experiences_old}
    new_experiences = [experience for experience in experiences_new if experience['link'] not in old_links]
    
    return new_experiences


class MeoSensationsBot(discord.Client):
    async def on_ready(self):
        self.channel = self.get_channel(CHANNEL_ID)
        await self.check_new_experiences()


    def create_experience_embed(self, exp):
        embed = discord.Embed(
            title=exp['title'],
            url=exp['link'],
            description=f"{exp['points']} - {exp['status']}",
            color=discord.Color.green() if exp['status'] == 'Disponível' else discord.Color.red()
        )
        embed.set_author(name=exp['brand'])
        embed.set_image(url=exp['image'])
        embed.set_footer(text="Check out this new experience!")

        return embed


    async def check_new_experiences(self):
        while True:
            experiences_new = get_current_experiences()
            
            if experiences_new:
                try:
                    with open('experiences.json', 'r', encoding='utf-8') as f:
                        experiences_old = json.load(f)['experiences']
                except (FileNotFoundError, json.JSONDecodeError):
                    experiences_old = []

                new_experiences = get_new_experiences(experiences_old, experiences_new)
                
                if new_experiences:
                    save_experiences_to_json(experiences_new, 'experiences.json')
                    for exp in new_experiences:
                        embed = self.create_experience_embed(exp)
                        await self.channel.send(embed=embed)
            else:
                print('No experiences found!')

            await asyncio.sleep(12 * 3600)  # Check every 12 hours


# Load environment variables
load_dotenv(dotenv_path='./discord.env')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
URL = 'https://loja.meo.pt/sensacoes-meos'


if __name__ == '__main__':
    bot = MeoSensationsBot(intents=discord.Intents.default())
    bot.run(DISCORD_TOKEN)

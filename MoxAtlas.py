import requests
import re
import math
from io import BytesIO
from PIL import Image

def parse_card_list(card_list_text):
    pattern = re.compile(r'\d+\s+.*?\(([^)]+)\)\s+(\S+)')
    identifiers = []
    for line in card_list_text.strip().split('\n'):
        match = pattern.search(line)
        if match:
            set_code, collector_number = match.groups()
            collector_number = re.sub(r'[^\w\d-]', '', collector_number)  # remove any trailing letters like 'F'
            identifiers.append({"set": set_code.lower(), "collector_number": collector_number})
    return identifiers

def bulk_fetch_cards(identifiers):
    url = "https://api.scryfall.com/cards/collection"
    fetched_cards = []
    for i in range(0, len(identifiers), 75):
        batch = identifiers[i:i+75]
        response = requests.post(url, json={"identifiers": batch})
        if response.status_code == 200:
            fetched_cards.extend(response.json().get('data', []))
        else:
            print("Error fetching cards:", response.status_code, response.text)
    return fetched_cards

def create_atlas(cards, card_width=488, card_height=680):
    cols = math.ceil(math.sqrt(len(cards)))
    rows = math.ceil(len(cards) / cols)
    atlas = Image.new('RGBA', (cols * card_width, rows * card_height))

    for idx, card in enumerate(cards):
        img_url = card['image_uris']['png'] if 'image_uris' in card else card['card_faces'][0]['image_uris']['png']
        img_response = requests.get(img_url)
        card_image = Image.open(BytesIO(img_response.content)).resize((card_width, card_height))
        x = (idx % cols) * card_width
        y = (idx // cols) * card_height
        atlas.paste(card_image, (x, y))

    return atlas

# Example usage
card_list_text = """Deck list go here"""
identifiers = parse_card_list(card_list_text)
cards_data = bulk_fetch_cards(identifiers)
atlas_image = create_atlas(cards_data)
atlas_image.save("processeddeck.png")

print("Card atlas saved as processeddeck.png")

import re
import random
import string
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_invitation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def format_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %B, %Y')

def create_progress_bar(iterations):
    return st.progress(0)

def create_invitation(guest_name, couple_names, date, venue, output_path):
    try:
        # Create image
        img = Image.new('RGB', (800, 1200), color='#FFF8E1')
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 60)
            body_font = ImageFont.truetype("arial.ttf", 40)
            small_font = ImageFont.truetype("arial.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Gold border
        gold = '#D4AF37'
        draw.rectangle([20, 20, 780, 1180], outline=gold, width=10)
        
        # Corner decorations
        draw.ellipse([30, 30, 100, 100], fill=gold)
        draw.ellipse([700, 30, 770, 100], fill=gold)
        draw.ellipse([30, 1100, 100, 1170], fill=gold)
        draw.ellipse([700, 1100, 770, 1170], fill=gold)
        
        # Text
        y = 200
        draw.text((400, y), "YOU ARE INVITED", fill='#8B4513', font=title_font, anchor='mm')
        y += 100
        draw.text((400, y), couple_names, fill='#D4AF37', font=body_font, anchor='mm')
        y += 80
        draw.text((400, y), format_date(date), fill='#333', font=body_font, anchor='mm')
        y += 60
        draw.text((400, y), venue, fill='#333', font=body_font, anchor='mm')
        y += 100
        draw.text((400, y), f"Dear {guest_name}", fill='#8B4513', font=small_font, anchor='mm')
        
        img.save(output_path)
        return True
    except Exception as e:
        print(f"Error creating invitation: {e}")
        return False

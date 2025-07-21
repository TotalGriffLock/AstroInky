from inky.auto import auto
inky_display = auto()
from PIL import Image, ImageFont, ImageDraw, ImageOps
import cairosvg
import io
import requests
import re


#region BACKGROUND & COLOR HANDLING
display_height, display_width = inky_display.resolution                             #defines a canvas
base_img = Image.new("RGB", (display_width, display_height), (255, 255, 255))           #creates the initial background object (img) - mode, size, color
draw = ImageDraw.Draw(base_img)
#square = ((display_width - 10), (display_width - 10))  
bottom = (display_width)  
INKY_COLORS = {
    "BLACK":  (0, 0, 0),
    "WHITE":  (255, 255, 255),
    "YELLOW":    (255, 0, 0),
    "RED":  (0, 255, 0),
    "BLUE":   (0, 0, 255),
    "GREEN": (255, 255, 0),
}
BLACK  = INKY_COLORS["BLACK"]
WHITE  = INKY_COLORS["WHITE"]
RED    = INKY_COLORS["RED"]
GREEN  = INKY_COLORS["GREEN"]
BLUE   = INKY_COLORS["BLUE"]
YELLOW = INKY_COLORS["YELLOW"]
bw_palette = [
    0, 0, 0,         # Black
    255, 255, 255    # White
] + [0, 0, 0] * 254
bw_palette_img = Image.new("P", (16, 16))
bw_palette_img.putpalette(bw_palette)         
color_palette = [
    0, 0, 0,         # 0: Black
    255, 255, 255,   # 1: White
    255, 0, 0,       # 2: Red
    0, 255, 0,       # 3: Green
    0, 0, 255,       # 4: Blue
    255, 255, 0      # 5: Yellow
] + [0, 0, 0] * (250)  # Fill the rest with black
color_palette_img = Image.new("P", (16, 16))
color_palette_img.putpalette(color_palette)  
#endregion
#region TEXT, FONT & ICON SETTINGS
#FONTS
font = ImageFont.truetype("fonts/Merriweather-VariableFont_opsz,wdth,wght.ttf", 18)
font_path = "fonts/Merriweather-VariableFont_opsz,wdth,wght.ttf"
font_large = ImageFont.truetype("fonts/Merriweather-VariableFont_opsz,wdth,wght.ttf", 24)
ascent, descent = font.getmetrics()                                                 #gets the height (ascent and descent) of the font
font_height = ascent + descent 
line_spacing = font_height * 2
#ICONS
icon_size_lg = (font_height * 2, font_height * 2)
icon_size_sm = (font_height, font_height)
icon_size_xl = (font_height * 10, font_height * 10)
#TEXTWRAPPING
def wrap_text(text, font, draw, max_width, max_lines):
    words = text.split()
    lines = []
    line = ""

    for word in words:
        test_line = line + word + " "
        if draw.textlength(test_line, font=font) <= max_width:
            line = test_line
        else:
            lines.append(line.rstrip())
            line = word + " "
        if len(lines) >= max_lines:
            break

    if line and len(lines) < max_lines:
        lines.append(line.rstrip())
    elif len(lines) == max_lines:
        # Join all visible lines so far
        full_text = " ".join(lines) + " " + line

        # Find the last full sentence ending
        match = list(re.finditer(r'([.!?])\s+', full_text))
        if match:
            last_end = match[-1].end()
            clean_text = full_text[:last_end].strip()
        else:
            clean_text = full_text.strip()

        # Re-wrap from clean_text
        lines = []
        line = ""
        for word in clean_text.split():
            test_line = line + word + " "
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
                lines.append(line.rstrip())
                line = word + " "
                if len(lines) >= max_lines - 1:
                    break
        if line:
            lines.append(line.rstrip())

        # Append ellipsis if the original text was longer
        if not full_text.strip().endswith(clean_text.strip()):
            lines[-1] = lines[-1].rstrip(".!? ") + "..."

    return lines

# endregion
#region SVG Handler

def load_svg_icon(svg_path, size=(24, 24)):
    # Render SVG to PNG in memory
    png_data = cairosvg.svg2png(url=svg_path, output_width=size[0], output_height=size[1]) 
    icon_rgba = Image.open(io.BytesIO(png_data)).convert("RGBA")
    icon_bg = Image.new("RGBA", size, (255, 255, 255, 255))
    icon_flat = Image.alpha_composite(icon_bg, icon_rgba)
    icon_final = icon_flat.convert("RGB").quantize(palette=color_palette_img)  
    icon = Image.new("RGBA", icon_rgba.size)
    icon.paste(icon_final)
    return icon
#endregion
#region NAVIGATION BUTTONS
nav_refresh = load_svg_icon("icons/refresh.svg", size=icon_size_sm)
nav_solar = load_svg_icon("icons/solar.svg", size=icon_size_sm)
nav_star = load_svg_icon("icons/planet.svg", size=icon_size_sm)
nav_about = load_svg_icon("icons/nose.svg", size=icon_size_sm)
nav_phase = load_svg_icon("icons/moon.svg", size=icon_size_sm)
nav_y = 10
xA = ((display_width // 4) // 2) - (icon_size_sm[0] // 2)
xB = ((display_width // 4) // 2) * 3 - (icon_size_sm[0] // 2)
xC = ((display_width // 4) // 2) * 5 - (icon_size_sm[0] // 2)
xD = ((display_width // 4) // 2) * 7 - (icon_size_sm[0] // 2)
base_img.paste(nav_phase, (xA, nav_y))
base_img.paste(nav_star, (xB, nav_y))
base_img.paste(nav_solar, (xC, nav_y))
base_img.paste(nav_about, (xD, nav_y))
#endregion


#RANDOM APOD IMAGE
API_KEY = 'YOUR API HERE'
URL = 'https://api.nasa.gov/planetary/apod'
SAVE_PATH = '/home/path/to/apod_picture.jpg'

# --- GET RANDOM IMAGE DATA ---
while True:
    response = requests.get(URL, params={'api_key': API_KEY, 'count': 1})
    response.raise_for_status()
    data = response.json()[0]

    if data['media_type'] == 'image':
        image_url = data['url']
        title = data['title']
        explanation = data['explanation']
        break  # exit loop if it's an image

# --- DOWNLOAD IMAGE ---
response = requests.get(image_url)
response.raise_for_status()
with open(SAVE_PATH, 'wb') as f:
    f.write(response.content)

#PROCESS THE IMAGE FOR INKY

apod = Image.open(SAVE_PATH).convert("RGBA")
apod_crop = ImageOps.contain(apod, (display_width, display_width))  # resize to max width x width
image_frame = Image.new("RGBA", (display_width, apod_crop.height), (255, 255, 255, 255))
x = (display_width - apod_crop.width) // 2
y = 0
image_frame.paste(apod_crop, (x, y))  # <-- paste resized image here


margin = 10
# --- TITLE PLACEMENT BELOW NAV BUTTONS ---
title_y = nav_y + icon_size_sm[1] + margin
title_x = (display_width - draw.textlength(title.replace('\n', ' '), font=font)) // 2
draw.text((title_x, title_y), title.replace('\n', ' '), RED, font=font)

# --- IMAGE PLACEMENT BELOW TITLE ---
image_x = (display_width - image_frame.width) // 2
image_y = title_y + font_height + margin # margin + space for title
base_img.paste(image_frame, (image_x, image_y))


text_block_width = display_width - 40
text_block_height = display_height - image_frame.height - title_y - nav_y - margin
max_lines = text_block_height // font_height
lines = wrap_text(explanation, font, draw, text_block_width, max_lines)
max_text_start_y = display_height - text_block_height - 20
text_start_y = image_y + image_frame.height + margin


for line in lines:
    line_width = draw.textlength(line, font=font)
    x = (display_width - line_width) // 2
    draw.text((x, text_start_y), line, GREEN, font=font)
    text_start_y += font_height


#FINAL DISPLAY
final_img = base_img.rotate(90, expand=True)
final_img = final_img.quantize(palette=color_palette_img)
inky_display.set_image(final_img)
inky_display.show() 

# --- DEBUG INFO ---
print(f"URL: {image_url}")


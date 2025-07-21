from inky.auto import auto
inky_display = auto()
from PIL import Image, ImageFont, ImageDraw
import cairosvg
import io
import json
import random
import re

#region BACKGROUND & COLOR HANDLING
display_height, display_width = inky_display.resolution                             #defines a canvas
base_img = Image.new("RGB", (display_width, display_height), (255, 255, 255))           #creates the initial background object (img) - mode, size, color
draw = ImageDraw.Draw(base_img)
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

# Load JSON data
with open("moons.json", "r", encoding="utf-16") as f:
    moons = json.load(f)

# Pick a random moon entry
moon = random.choice(moons)
moon_name = moon["moon"]
planet_name = moon.get("planet", "Unknown planet")


# Pick 3 random fact pairs (or fewer if not enough)
fact_items = list(moon["facts"].items()) if moon["facts"] else []
selected_facts = random.sample(fact_items, min(3, len(fact_items))) if fact_items else [("Fact", "N/A")]

# Combine the selected facts into a single string with line breaks
facts_text = "\n".join(f"{key}: {val}" for key, val in selected_facts)

# Pick a random extra fact string
extra_fact = random.choice(moon["extra_facts"]) if moon["extra_facts"] else "No extra facts available."

# Measure heights for centering
moon_name_height = font.getbbox(moon_name)[3] - font.getbbox(moon_name)[1]
facts_lines = facts_text.split('\n')
facts_height = len(facts_lines) * font_height

planet_height = font.getbbox(planet_name)[3] - font.getbbox(planet_name)[1]
total_height = moon_name_height + planet_height + facts_height + font_height  # extra for spacing
start_y = (display_height - total_height) // 2
# Draw moon name centered horizontally
moon_name_x = (display_width - draw.textlength(moon_name, font=font)) // 2
draw.text((moon_name_x, start_y), moon_name, GREEN, font=font)



planet_y = start_y + moon_name_height + font_height // 2
planet_x = (display_width - draw.textlength(planet_name, font=font)) // 2
draw.text((planet_x, planet_y), planet_name, BLUE, font=font)



# Draw the combined facts block centered horizontally, stacked lines
facts_y = planet_y + planet_height + font_height // 2
for i, line in enumerate(facts_lines):
    line_x = (display_width - draw.textlength(line, font=font)) // 2
    line_y = facts_y + i * font_height
    draw.text((line_x, line_y), line, BLACK, font=font)

# Wrap and draw extra fact below the facts block
extra_start_y = facts_y + facts_height + font_height // 2
max_width = display_width - 10  # leave some margin
max_lines = 4                   # how many lines to show for extra_fact
wrapped_lines = wrap_text(extra_fact, font, draw, max_width, max_lines)

y = extra_start_y
for line in wrapped_lines:
    draw.text((5, y), line, RED, font=font)  # small left margin of 5px
    y += font_height

#FINAL DISPLAY
final_img = base_img.rotate(90, expand=True)
final_img = final_img.quantize(palette=color_palette_img)
inky_display.set_image(final_img)
inky_display.show()

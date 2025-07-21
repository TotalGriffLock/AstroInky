from inky.auto import auto
inky_display = auto()
from PIL import Image, ImageFont, ImageDraw
import cairosvg
import io

#region BACKGROUND & COLOR HANDLING
display_height, display_width = inky_display.resolution                             #defines a canvas
base_img = Image.new("RGB", (display_width, display_height), (255, 255, 255))           #creates the initial background object (img) - mode, size, color
draw = ImageDraw.Draw(base_img)
square = ((display_width - 10), (display_width - 10))  
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
font_large = ImageFont.truetype("fonts/Merriweather-VariableFont_opsz,wdth,wght.ttf", 24)
ascent, descent = font.getmetrics()                                                 #gets the height (ascent and descent) of the font
font_height = ascent + descent 
line_spacing = font_height * 2
#ICONS
icon_size_lg = (font_height * 2, font_height * 2)
icon_size_sm = (font_height, font_height)
icon_size_xl = (font_height * 10, font_height * 10)

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
base_img.paste(nav_refresh, (xD, nav_y))
#endregion

#image
image = load_svg_icon("icons/heart.svg", size=icon_size_xl)
base_img.paste(image, ((display_width // 2) - (icon_size_xl[0] // 2), (display_height // 2) - (icon_size_xl[0] // 2)))

#message
align_center = display_width // 2
message_top = "Custom top message"
top_center = align_center - (draw.textlength(message_top, font=font) / 2)
message_bottom = "Custom middle message"
bottom_center = align_center - (draw.textlength(message_bottom, font=font) / 2)
message_footer = "Custom footer message"
footer_center = align_center - (draw.textlength(message_footer, font=font) / 2)



draw.text((top_center, 200), message_top, RED, font=font) 
draw.text((bottom_center, 550), message_bottom, RED, font=font) 
draw.text((footer_center, display_height - (font_height * 2)), message_footer, BLACK, font=font) 

#FINAL DISPLAY
final_img = base_img.rotate(90, expand=True)
final_img = final_img.quantize(palette=color_palette_img)
inky_display.set_image(final_img)
inky_display.show() 
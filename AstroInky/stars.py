from inky.auto import auto
inky_display = auto()
from PIL import Image, ImageFont, ImageDraw
import ephem
from datetime import datetime, timedelta
import cairosvg
import io
from zoneinfo import ZoneInfo
import math

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
#region EMPHEM

#LOCALTIME
def to_singapore_time(ephem_date):
    return ephem_date.datetime() + timedelta(hours=8)

#TIME
now_utc = datetime.utcnow()
now_local = now_utc + timedelta(hours=0) #YOUR TIMEZONE
timezone = ZoneInfo("Europe/London") #YOUR TIMEZONE



#POSITION
observer = ephem.Observer()
observer.lat = '0.0' #YOUR LATITUDE
observer.lon = '0.0' #YOUR LONGITUDE
observer.elevation = 0 #YOUR ELEVATION
observer.date = now_local
observer.temperature = 36

#STARS
stars = [
    'Sirius', 'Canopus', 'Arcturus', 'Vega', 'Capella', 'Rigel',
    'Procyon', 'Betelgeuse', 'Altair', 'Aldebaran', 'Spica',
    'Antares', 'Pollux', 'Fomalhaut', 'Deneb', 'Regulus'
]

visible_stars = []

for name in stars:
    star = ephem.star(name)
    star.compute(observer)
    if star.alt > 0:  
        visible_stars.append((name, star.alt, star.az, star.mag))

#PLANETS
planets = {
    'Mercury': ephem.Mercury(),
    'Venus': ephem.Venus(),
    'Mars': ephem.Mars(),
    'Jupiter': ephem.Jupiter(),
    'Saturn': ephem.Saturn(),
    'Uranus': ephem.Uranus(),
    'Neptune': ephem.Neptune(),
    'Pluto': ephem.Pluto()
}
visible_planets = []

for name, planet in planets.items():
    planet.compute(observer)
    
    if planet.alt > 0:  # Above the horizon
        visible_planets.append((name, planet.alt, planet.az, planet.mag))

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
base_img.paste(nav_refresh, (xB, nav_y))
base_img.paste(nav_solar, (xC, nav_y))
base_img.paste(nav_about, (xD, nav_y))
#endregion

#DATE TITLE
date_short = datetime.now(timezone).strftime('%a %-d/%m/%y %H:%M')
date = datetime.now(timezone).strftime('%A %d %B %Y')
title = "Stars and Planets"
date_width = draw.textlength(date_short, font=font)
x_title = (icon_size_sm[0] // 2)
y_title = (icon_size_sm[0] * 2)
x_date = display_width - date_width - 10
y_date = (icon_size_sm[0] * 2) + (font_height // 2)

draw.text((x_title, y_title), title, BLACK, font=font_large) 
draw.text((x_date, y_date), date_short, RED, font=font) 

#GRID TITLE
title_Name = "Name"
title_Mag = "Mag"
title_Alt = "Alt"
title_Az = "Az"
x_Name = 10
x_Mag = ((display_width // 4) // 2) * 3 - (icon_size_sm[0] // 2)
x_Alt = ((display_width // 4) // 2) * 5 - (icon_size_sm[0] // 2)
x_Az = ((display_width // 4) // 2) * 7 - (icon_size_sm[0] // 2)
y_Name = (icon_size_sm[0] * 3) + 30
y_Mag = (icon_size_sm[0] * 3) + 30
y_Alt = (icon_size_sm[0] * 3) + 30
y_Az = (icon_size_sm[0] * 3) + 30
draw.text((x_Name, y_Name), title_Name, BLACK, font=font) 
draw.text((x_Mag, y_Mag), title_Mag, GREEN, font=font) 
draw.text((x_Alt, y_Alt), title_Alt, RED, font=font) 
draw.text((x_Az, y_Az), title_Az, BLUE, font=font) 

#LIST PLANETS
x_offset = 10
y_offset = (icon_size_sm[0] * 4) + 40
for i, (name, alt, az, mag) in enumerate(visible_planets):
    y = y_offset + i * line_spacing
    draw.text((x_Name, y), f"{name}", BLACK, font=font) 
    draw.text((x_Mag, y), f"{mag:.1f}", GREEN, font=font) 
    draw.text((x_Alt, y), f"{math.degrees(alt):.1f}°", RED, font=font) 
    draw.text((x_Az, y), f"{math.degrees(az):.1f}°", BLUE, font=font) 

#LIST STARS
x_offset = 10
y_offset = (display_height // 2) + 10
for i, (name, alt, az, mag) in enumerate(visible_stars):
    y = y_offset + i * line_spacing
    draw.text((x_Name, y), f"{name}", BLACK, font=font) 
    draw.text((x_Mag, y), f"{mag:.1f}", GREEN, font=font) 
    draw.text((x_Alt, y), f"{math.degrees(alt):.1f}°", RED, font=font) 
    draw.text((x_Az, y), f"{math.degrees(az):.1f}°", BLUE, font=font) 

#FINAL DISPLAY
final_img = base_img.rotate(90, expand=True)
final_img = final_img.quantize(palette=color_palette_img)
inky_display.set_image(final_img)
inky_display.show() 
import ephem
from datetime import datetime, timedelta
import math
from zoneinfo import ZoneInfo
import cairosvg
import io
from PIL import Image, ImageDraw, ImageFont # Font import still needed for Image, but not used for text drawing
from inky.auto import auto
inky_display = auto()


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

#region DIAGRAM PARAMETERS

# --- Diagram Parameters ---
WIDTH = display_width
HEIGHT = display_height
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
SUN_OUTER_RADIUS = 10
SUN_INNER_RADIUS = 6
PLANET_DOT_SIZE = 6 # Radius of planet dots

# --- Configuration ---
# Your location (Singapore) - though not strictly needed for heliocentric view
MY_LATITUDE = 0.00 #YOUR LATITUDE
MY_LONGITUDE = 0.00 #YOUR LONGITUDE
MY_ELEVATION = 0 #YOUR ELEVATION

#TIME
now_utc = datetime.utcnow()
now_local = now_utc + timedelta(hours=8) #YOUR TIMEZONE
timezone = ZoneInfo("Europe/London") #YOUR TIMEZONE (IANA)

#ORBIT RINGS
ORBIT_RADII = {
    "Mercury": 20,
    "Venus": 32,
    "Earth": 48,
    "Mars": 70,
    "Jupiter": 133,
    "Saturn": 165,
    "Uranus": 199,
    "Neptune": 221,
}

#PLANETS
PLANETS_TO_DRAW = {
    "Mercury": ephem.Mercury(),
    "Venus": ephem.Venus(),
    "Earth": None,
    "Mars": ephem.Mars(),
    "Jupiter": ephem.Jupiter(),
    "Saturn": ephem.Saturn(),
    "Uranus": ephem.Uranus(),
    "Neptune": ephem.Neptune(),
}

#PLANET COLORS



PLANET_COLORS = {
    "Mercury": RED,
    "Venus":   YELLOW,
    "Earth":   GREEN,
    "Mars":    RED,
    "Jupiter": RED,
    "Saturn":  YELLOW,
    "Uranus":  BLUE,
    "Neptune": BLUE,
}

#endregion

#region DRAWING

    
latitude=MY_LATITUDE
longitude=MY_LONGITUDE
elevation=MY_ELEVATION
date=now_local    

if date is None:
    observer_date = datetime.utcnow()
else:
    observer_date = date

obs = ephem.Observer()
obs.lat = str(latitude)
obs.lon = str(longitude)
obs.elevation = elevation
obs.date = observer_date

# --- 1. Draw the Sun ---
draw.ellipse(
(CENTER_X - SUN_OUTER_RADIUS, CENTER_Y - SUN_OUTER_RADIUS,
    CENTER_X + SUN_OUTER_RADIUS, CENTER_Y + SUN_OUTER_RADIUS),
fill=inky_display.YELLOW
)
draw.ellipse(
(CENTER_X - SUN_INNER_RADIUS, CENTER_Y - SUN_INNER_RADIUS,
    CENTER_X + SUN_INNER_RADIUS, CENTER_Y + SUN_INNER_RADIUS),
fill=inky_display.YELLOW
)

# --- 2. Draw Orbital Rings and Planets ---
for name, planet_obj in PLANETS_TO_DRAW.items():
    if name not in ORBIT_RADII:
        continue

    orbit_radius = ORBIT_RADII[name]
    dot_color = PLANET_COLORS.get(name, inky_display.WHITE)

    # Draw the orbital rings in the planet's color
    if (CENTER_X - orbit_radius >= 0 and CENTER_Y - orbit_radius >= 0 and
        CENTER_X + orbit_radius <= WIDTH and CENTER_Y + orbit_radius <= HEIGHT):
        RING_THICKNESS = 3  # change to 2, 4, etc. if desired
        for offset in range(-(RING_THICKNESS // 2), (RING_THICKNESS // 2) + 1):
            draw.ellipse(
                (CENTER_X - orbit_radius - offset, CENTER_Y - orbit_radius - offset,
                CENTER_X + orbit_radius + offset, CENTER_Y + orbit_radius + offset),
                outline=dot_color
            )

    # Compute planet's heliocentric position
    if name == "Earth":
        sun = ephem.Sun(obs)
        sun_hlon = float(sun.hlon)
        planet_h_lon = (sun_hlon + math.pi) % (2 * math.pi)
    else:
        planet_obj.compute(obs)
        planet_h_lon = float(planet_obj.hlon)

    # Calculate planet's (x, y) coordinates on its ring
    planet_x = CENTER_X + int(orbit_radius * math.cos(planet_h_lon))
    planet_y = CENTER_Y + int(orbit_radius * math.sin(planet_h_lon))

    # Draw the planet dot
    draw.ellipse(
        (planet_x - PLANET_DOT_SIZE, planet_y - PLANET_DOT_SIZE,
        planet_x + PLANET_DOT_SIZE, planet_y + PLANET_DOT_SIZE),
        fill=dot_color
    )
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
base_img.paste(nav_refresh, (xC, nav_y))
base_img.paste(nav_about, (xD, nav_y))
#endregion

    
#FINAL DISPLAY
final_img = base_img.rotate(90, expand=True)
final_img = final_img.quantize(palette=color_palette_img)
inky_display.set_image(final_img)
inky_display.show() 




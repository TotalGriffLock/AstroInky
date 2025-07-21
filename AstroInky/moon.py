from inky.auto import auto
inky_display = auto()
from PIL import Image, ImageFont, ImageDraw
import ephem
from datetime import datetime, timedelta
import cairosvg
import io
from zoneinfo import ZoneInfo

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
#region LOCALTIME
def to_local_time(ephem_date):
    return ephem_date.datetime() + timedelta(hours=0) #CHANGE TO LOCAL TZ
now_utc = datetime.utcnow()
now_sgt = now_utc + timedelta(hours=8)
timezone = ZoneInfo("Europe/London")
#endregion
#region EMPHEM
#POSITION
observer = ephem.Observer()
observer.lat = '0.0' #YOURLATITUDE
observer.lon = '0.0' #YOURLONGITUDE
observer.elevation = 0 #YOURELEVATION
observer.date = now_utc

#WAX OR WANE
def get_precise_moon_phase(observer):
    moon = ephem.Moon(observer)
    sun = ephem.Sun(observer)
    illumination = moon.phase
    elongation = ephem.separation(moon, sun)  # angle between moon and sun

    # Calculate waxing or waning
    moon.compute(observer)
    sun.compute(observer)

    # Difference in ecliptic longitude (positive if waxing)
    waxing = (moon.elong > 0 and moon.elong < ephem.pi)

    if illumination == 0:
        return "New Moon"
    elif 0 < illumination < 50:
        return "Waxing Crescent" if waxing else "Waning Crescent"
    elif 50 <= illumination < 99:
        if elongation < ephem.pi:
            return "First Quarter" if waxing else "Last Quarter"
        else:
            return "Waxing Gibbous" if waxing else "Waning Gibbous"
    elif illumination >= 99.5:
        return "Full Moon"
    else:
        return "Unknown Phase"
    
#MOON IMAGE
moon_img_path = "/home/path/to/phases"
def get_moon_phase_img(phase):
    match phase.lower():
        case "new moon":
            return f"{moon_img_path}/new_moon.png"
        case "waxing crescent":
            return f"{moon_img_path}/waxing_crescent.png"
        case "first quarter":
            return f"{moon_img_path}/first_quarter.png"
        case "waxing gibbous":
            return f"{moon_img_path}/waxing_gibbous.png"
        case "full moon":
            return f"{moon_img_path}/full_moon.png"
        case "waning gibbous":
            return f"{moon_img_path}/waning_gibbous.png"
        case "last quarter" | "third quarter":
            return f"{moon_img_path}/last_quarter.png"
        case "waning crescent":
            return f"{moon_img_path}/waning_crescent.png"
        case _:
            return "Unknown moon phase."
    
# MOONPHASE
moon_phase = get_precise_moon_phase(observer) # Returns phase as text
moon_phase_image = get_moon_phase_img(moon_phase) # Returns the phase image path

moon = ephem.Moon()
moon.compute(observer)

#MOON FINDER
moon_azimuth = azimuth_deg = float(moon.az) * (180.0 / ephem.pi)
moon_altitude = altitude_deg = float(moon.alt) * (180.0 / ephem.pi)

#MOONRISE & SET
try:
    moonrise = observer.next_rising(moon)
    moonrise_time = to_local_time(moonrise).strftime('%H:%M %a')
except (ephem.AlwaysUpError, ephem.NeverUpError):
    moonrise_time = "Not visible today"
try:
    moonset = observer.next_setting(moon)
    moonset_time = to_local_time(moonset).strftime('%H:%M %a')
except (ephem.AlwaysUpError, ephem.NeverUpError):
    moonset_time = "Not visible today"
#endregion

#MOON IMAGE
moon = Image.open(moon_phase_image).convert("RGBA").resize(square)   
white_bg = Image.new("RGBA", moon.size, (255, 255, 255, 255))
flattened_moon = Image.alpha_composite(white_bg, moon)
moon_img = flattened_moon.convert("RGB").quantize(palette=bw_palette_img, dither=Image.Dither.FLOYDSTEINBERG)  
center_moon = (display_width // 2) - (moon_img.height // 2)
base_img.paste(moon_img.convert("RGB"), (center_moon, (font_height * 3 + icon_size_lg[0])))

#TEXTAREAS
text_area_top = (moon_img.height + line_spacing)                                             #defines the top of the text area (moon height + 100 padding)
text_area_bottom = (display_height - 10) - font_height                              #defines the top of the text area (total height - 10 padding, -font height as padding)
text_area_height = text_area_bottom - text_area_top                                 #defubes the difference between top and bottom as the total height

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
base_img.paste(nav_refresh, (xA, nav_y))
base_img.paste(nav_star, (xB, nav_y))
base_img.paste(nav_solar, (xC, nav_y))
base_img.paste(nav_about, (xD, nav_y))
#endregion

#DATE TITLE
date = datetime.now(timezone).strftime('%A %d %B %Y')
title_width = draw.textlength(date, font=font_large)
x_title = icon_size_lg[0] + 10
y_title = (display_width // 2) - (title_width // 2)
draw.text((y_title, x_title), date, GREEN, font=font_large) 


#LEFT COLUMN
left_icon = 10 
left_icon_text = left_icon + icon_size_lg[0] + 10
left_text_lines = [
    (moon_phase,"icons/phase.svg"), 
    (f"{azimuth_deg:.2f}°", "icons/azimuth.svg"),
    (moonrise_time, "icons/moonrise.svg"),
]
for i, (text_data, icon_path) in enumerate(left_text_lines):
    y = text_area_bottom - (i * line_spacing) - icon_size_lg[0]
    left_text_data = left_icon_text + 10
    icon = load_svg_icon(icon_path, size=icon_size_lg)
    base_img.paste(icon, (left_icon, y))
    draw.text((left_text_data, y + (font_height*0.5)), text_data, GREEN, font=font)
   
#RIGHT COLUMN
blank = ""
right_icon = (display_width // 2) 
right_icon_text = right_icon + icon_size_lg[0] + 10
right_text_lines = [ 
    (blank,"icons/blank.svg"),
    (f"{altitude_deg:.2f}°", "icons/height.svg"),
    (moonset_time, "icons/moonset.svg"),
]
for i, (text_data, icon_path) in enumerate(right_text_lines):
    y = text_area_bottom - (i * line_spacing) - icon_size_lg[0]
    right_text_data = right_icon_text + 10
    icon = load_svg_icon(icon_path, size=icon_size_lg)
    base_img.paste(icon, (right_icon, y))
    draw.text((right_text_data, y + (font_height*0.5)), text_data, GREEN, font=font)

#FINAL DISPLAY
final_img = base_img.rotate(90, expand=True)
final_img = final_img.quantize(palette=color_palette_img)
inky_display.set_image(final_img)
inky_display.show() 
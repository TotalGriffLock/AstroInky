import astro_constants
import astro_functions

# Initialise display
inky_display, base_img, display_height, display_width, draw = astro_functions.init_display()

#image
image = astro_functions.load_svg_icon(astro_functions.config['about']['image'], size=astro_constants.icon_size_xl)
base_img.paste(image, ((display_width // 2) - (astro_constants.icon_size_xl[0] // 2), (display_height // 2) - (astro_constants.icon_size_xl[0] // 2)))

#message
align_center = display_width // 2
message_top = astro_functions.config['about']['top_msg']
top_center = align_center - (draw.textlength(message_top, font=astro_constants.font) / 2)
message_mid = astro_functions.config['about']['mid_msg']
mid_center = align_center - (draw.textlength(message_mid, font=astro_constants.font) / 2)
message_footer = astro_functions.config['about']['low_msg']
footer_center = align_center - (draw.textlength(message_footer, font=astro_constants.font) / 2)

draw.text((top_center, 200), message_top, astro_constants.RED, font=astro_constants.font)
draw.text((mid_center, 550), message_mid, astro_constants.RED, font=astro_constants.font)
draw.text((footer_center, display_height - (astro_constants.font_height * 2)), message_footer, astro_constants.BLACK, font=astro_constants.font)

#FINAL DISPLAY
astro_functions.astro_display(base_img, inky_display)

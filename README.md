# 🌙 Inky Impression Moon Phase Display

A Python project for Raspberry Pi that displays various astronomical information pages on a **6-color Inky Impression e-ink display**, using **PyEphem** for precise astronomical calculations.

This is currently not a particularly easy project to customise - mainly because this is my first real python/Inky project and I didn't write it with other people using it in mind. However, it is possible if you follow the steps in the Customising section

ChatGPT (OpenAI) was used fairly extensively to write and debug and, as such, the commenting is a bit sporadic and inconsistent.

## ✨ Features

- Button-driven interface using the Inky Impression’s 4 hardware buttons
- Shows the current **moon phase** as an image, as well as:
  - Moonrise & moonset times
  - Azimuth and altitude of the moon (based on a configurable latitude/longitude)
- Displays **visible stars and planets** (updates on refresh)
- Renders an accurate visual representation of the **solar system** with the planets in their approximate current positions
- Shows an **"About"** page with a personal message

### Long Button Press Functions

- Pulls a **random NASA Astronomy Picture of the Day** (with title and description)
- Displays a **random named moon** of a planet with fun facts
- **Shuts the system down** and displays a shutdown message
- Shows an **"Instructions"** page

> Everything is designed to be displayed in **portrait** orientation (not landscape)

---

## 🔧 Hardware Requirements

- Raspberry Pi (any model with GPIO support)
- [Inky Impression (7-color, 5.7")](https://shop.pimoroni.com/products/inky-impression-5-7)
- SD card, power supply, and network access for the Pi

---

## 🧰 Software Requirements and Dependencies

- Python 3.7+
- [PyEphem](https://pypi.org/project/ephem/)
- [Pillow](https://pypi.org/project/Pillow/)
- [Pimoroni Inky library](https://github.com/pimoroni/inky/)
- `gpiozero`

---

## ▶️ Usage

A `systemd` service runs on startup, activates a virtual environment, and executes `handler.py` (which in turn launches `about.py` as the startup screen).

Long-pressing the **A** button (which, unintuitively, is on the right side) will **shut down** the system and display a shutdown message.

---

## ⚙️ Customising

- **Location**: Set your latitude, longitude, elevation, and timezone in `moon.py`, `solar.py`, and `stars.py` (anywhere PyEphem is used).
- **NASA API**: You’ll need an API key for `picture.py`. Sign up at [api.nasa.gov](https://api.nasa.gov).
- **Pi Pins**: The button GPIO pins are mapped for the Raspberry Pi Zero W. If you're using another model, update them in `handler.py`.
- **Custom Message**: The #image and #message sections in about.py need to be updated
- **Absolute Paths**: There are a number of absolute paths which you will need to change (instructions.py, moon.py, picture.py, ) - search for /home/path/to
- **Font**: The scripts call an absolute path to a font - you will need to update every script if you want to change it
- **AutoRun**: You need to create a systemmd file to run at boot to load the venv and run handler.py - the example is incldued but you will need to change the path and username under "[Service]"
- **Instructions**: These just show the button mapping - you can expand on this (or replace it entirely - you'll need to understand and edit handler.py)
---

## 🛠️ To Do

- Move shared functions to a single utility script (e.g., text/font/icon handling, navigation buttons, image processing)
- Create a centralized positioning/layout system
- Replace all personal data with placeholders or move them into a config file
- Fix all the commenting

## 3D Printed Case

- Three part (OK, 4 if you count the legs seperately... OK, 8 if you also count the buttons seperately...) 3D printed case
- Printed in PLA with default settings - you will need supports for the back piece
- Uses 4 x M2.5mm bolts that screw into the Inky Impression - I used some filed down standoffs to make everything a bit more rigid but it probably isn't needed
- Uses 4 x M2 bolts and nuts to hold the front face on
- STL files: https://www.printables.com/model/1363758-inky-impression-spectra-73-case

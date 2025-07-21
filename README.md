# 🌙 Inky Impression Moon Phase Display

A Python project for Raspberry Pi that displays various astronomical information pages on a **6-color Inky Impression e-ink display**, using **PyEphem** for precise astronomical calculations.

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

---

## 🛠️ To Do

- Move shared functions to a single utility script (e.g., text/font/icon handling, navigation buttons, image processing)
- Create a centralized positioning/layout system
- Replace all personal data with placeholders or move them into a config file

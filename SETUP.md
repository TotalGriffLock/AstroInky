# These are just my rough notes for now

Install rpi os 64-bit lite and boot your pi

```
sudo rpi-update
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
```

add
dtoverlay=spi0-0cs
to /boot/firmware/config.txt
```
sudo reboot
```

Add some packages
```
sudo apt install python3-ephem python3-gpiozero python3-numpy git python3-tzlocal python3-smbus python3-dev python3-cairosvg python3-flatbuffers
```

Add a user for AstroInky to run as. By default the pi user is a sudoer and has all sorts of other permissions, or you might have renamed it, or any numerous other things. We will have a separate user for this service.
```
sudo useradd -m -s /bin/bash -G spi,i2c,gpio -c "AstroInky User" -d /opt/astroinky astrouser
```
Switch to that user
```
sudo -i
su - astrouser
```

Create a venv for all the python bits and pieces to live in
```
python3 -m venv --system-site-packages $HOME
source ~/bin/activate
pip install inky
pip install timezonefinder
```
If you are planning on using the pimoroni GPS breakout module:
```
pip install pa1010d
```
Clone this repo:
```
git clone https://github.com/TotalGriffLock/AstroInky
cd AstroInky
```
Update config.ini appropriately. If you are using the GPS breakout module, you can leave the longitude, latitude and elevation blank, and set use_gps to y

Set up some system bits, as root:
```
mv ~astrouser/AstroInky/supporting_files/AstroInky.service /etc/systemd/system/
mv ~astrouser/AstroInky/supporting_files/astrouser /etc/sudoers.d/
systemctl daemon-reload
systemctl enable --now AstroInky
```

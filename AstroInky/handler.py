from gpiozero import Button
from signal import pause
import subprocess
import os
import signal
import threading
import time
import sys

# default startup script
last_script_key = 'a_short'  

# Define buttons with long press detection
button_a = Button(5, hold_time=2)
button_b = Button(6, hold_time=2)
button_c = Button(16, hold_time=2)
button_d = Button(24, hold_time=2)

# Define script paths
scripts = {
    'a_short': 'about.py',
    'a_long': 'shutdown.py',
    'b_short': 'solar.py',
    'b_long': 'picture.py',
    'c_short': 'stars.py',
    'c_long': 'othermoons.py',
    'd_short': 'moon.py',
    'd_long': 'instructions.py'
}

# Keep track of currently running script
current_process = None

def stop_current_script():
    global current_process
    if current_process and current_process.poll() is None:
        try:
            print(f"Stopping PID {current_process.pid}")
            os.kill(current_process.pid, signal.SIGTERM)
        except Exception as e:
            print(f"Failed to stop process: {e}")
    current_process = None

def run_script(script_key):
    global current_process, last_script_key
    last_script_key = script_key
    stop_current_script()
    print(f"Starting {scripts[script_key]}")
    current_process = subprocess.Popen([sys.executable, scripts[script_key]])

def shutdown_system():
    print("Long press on A: Preparing to shut down...")
    stop_current_script()
    
    print(f"Running shutdown script: {scripts['a_long']}")
    try:
        # Run shutdown.py and wait for it to complete
        subprocess.run([sys.executable, scripts['a_long']], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Shutdown script failed: {e}")
    
    print("Shutdown script finished. Shutting down system now...")
    subprocess.call("sudo shutdown -h now", shell=True)


def hourly_refresher():
    global last_script_key
    while True:
        time.sleep(3600)  # wait 1 hour
        print("Refreshing current script...")
        run_script(last_script_key)

# Button bindings
button_a.when_pressed = lambda: run_script('a_short')
button_a.when_held = shutdown_system

button_b.when_pressed = lambda: run_script('b_short')
button_b.when_held = lambda: run_script('b_long')

button_c.when_pressed = lambda: run_script('c_short')
button_c.when_held = lambda: run_script('c_long')

button_d.when_pressed = lambda: run_script('d_short')
button_d.when_held = lambda: run_script('d_long')

if __name__ == "__main__":
    print("Button launcher active. Short presses switch scripts. Hold About to shutdown.")
    run_script('a_short')
    threading.Thread(target=hourly_refresher, daemon=True).start()
    pause()


import os
import subprocess
import time
from dotenv import load_dotenv

def create_and_activate_venv(venv_path):
    if not os.path.exists(venv_path):
        os.system(f'python3 -m venv {venv_path}')
    subprocess.run([f'{venv_path}/bin/pip', 'install', '-r', 'requirements.txt'])

def start_pigpiod():
    result = subprocess.run(['pgrep', 'pigpiod'], capture_output=True, text=True)
    if result.returncode != 0:
        subprocess.run(['sudo', 'pigpiod'])
        time.sleep(2)  # Add a delay to ensure pigpiod has time to start
    else:
        print("pigpiod is already running")

def load_environment_variables():
    load_dotenv()
    return os.getenv('SECRET_KEY')

def cleanup():
    """
    Cleanup function to stop pigpiod and perform other necessary cleanup.
    """
    subprocess.run(['sudo', 'killall', 'pigpiod'])
    print("Cleanup completed.")
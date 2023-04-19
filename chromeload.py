import requests
import os
import platform
import zipfile
from io import BytesIO

def download_chromedriver():
    system = platform.system()
    chromedriver_url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    response = requests.get(chromedriver_url)
    version_number = response.text.strip()
    if system == 'Windows':
        
        
        download_url = f'https://chromedriver.storage.googleapis.com/{version_number}/chromedriver_win32.zip'
        driver_filename = 'chromedriver.exe'
    elif system == 'Darwin':
        system_type = 'chromedriver_linux64.zip'
        download_url = f'https://chromedriver.storage.googleapis.com/{version_number}/{system_type}'
        driver_filename = 'chromedriver'
    elif system == 'Linux':
        system_type = 'chromedriver_linux64.zip'
        download_url = f'https://chromedriver.storage.googleapis.com/{version_number}/{system_type}}'
        driver_filename = 'chromedriver'
    else:
        raise ValueError(f'Unsupported operating system: {system}')
    
    print(f'Downloading ChromeDriver {version_number} for {system}...')
    response = requests.get(download_url)
    zipped_file = BytesIO(response.content)
    
    with zipfile.ZipFile(zipped_file) as z:
        z.extract(driver_filename)
    
    print(f'ChromeDriver {version_number} downloaded and saved as {driver_filename}.')
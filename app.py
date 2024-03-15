from flask import Flask, render_template, request
from flask import Flask, send_from_directory
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import os
import urllib.parse
import time

app = Flask(__name__, static_url_path='/static')

def download_images(url, folder_path, limit=10):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img')

        os.makedirs(folder_path, exist_ok=True)

        for i, img_tag in enumerate(images[:limit]):
            img_url = img_tag.get('src')
            if img_url:
                img_url = urllib.parse.urljoin(url, img_url)
                img_response = requests.get(img_url)

                if img_response.status_code == 200:
                    img_name = f'image_{i + 1}.{img_url.split(".")[-1]}'
                    img_name = "".join([c for c in img_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()

                    with open(os.path.join(folder_path, img_name), 'wb') as img_file:
                        img_file.write(img_response.content)
    else:
        print(f'Failed to fetch the URL. Status code: {response.status_code}')

def search_and_download_images(query, output_folder, limit=10):
    driver = webdriver.Chrome()
    driver.get("https://www.google.com/imghp")

    search_bar = driver.find_element("name", "q")
    search_bar.send_keys(query)
    search_bar.send_keys(Keys.RETURN)

    time.sleep(5)
    download_images(driver.current_url, output_folder, limit)
    driver.quit()

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        search_query = request.form['query']
        output_folder = 'static/downloaded_images'  # 'static' folder for Flask to serve static files

        # Call the function to search and download images
        search_and_download_images(search_query, output_folder, limit=10)

        # Get the list of downloaded image filenames
        image_files = os.listdir(output_folder)
        image_files.sort()

        # Render the template with the list of image filenames
        return render_template('index.html', image_files=image_files)

    return render_template('index.html', image_files=None)

if __name__ == '__main__':
    app.run(debug=True)

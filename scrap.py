"""This is the scrapping file where to extract the images or some specific data for the specific requirements"""
import os
import requests
from bs4 import BeautifulSoup
from database import get_database
from log import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.request import urlretrieve

# ✅ Connect to MongoDB
db = get_database()
search_collection = db["user_searches"]

# ✅ Image save directory
IMAGE_DIR = "static/images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def scrape_images(query, num_images=5):
    """Scrapes images from Google based on the user's query"""
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    images = []

    for img in soup.find_all("img")[1:num_images+1]:  # Skip the first Google logo image
        img_url = img["src"]
        img_filename = f"{IMAGE_DIR}/{query.replace(' ', '_')}_{len(images)+1}.jpg"
        
        urlretrieve(img_url, img_filename)
        images.append(img_filename)
    
    # ✅ Store in MongoDB
    search_collection.insert_one({"type": "image", "query": query, "results": images})
    
    return images

def scrape_videos(query, num_videos=5):
    """Scrapes YouTube videos based on the user's query"""
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # ✅ Run without opening the browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(search_url)
    video_links = []

    for video in driver.find_elements(By.XPATH, "//a[@href]"):
        href = video.get_attribute("href")
        if "watch?v=" in href and href not in video_links:
            video_links.append(href)
        
        if len(video_links) >= num_videos:
            break
    
    driver.quit()
    
    # ✅ Store in MongoDB
    search_collection.insert_one({"type": "video", "query": query, "results": video_links})
    
    return video_links

# ✅ Test Scraper
if __name__ == "__main__":
    choice = input("Do you want to scrape images or videos? ").strip().lower()
    
    if choice == "images":
        category = input("Enter a category (animals, places in India): ").strip().lower()
        images = scrape_images(category)
        print(f"✅ Scraped {len(images)} images for '{category}'.")

    elif choice == "videos":
        category = input("Enter a category (animals, places): ").strip().lower()
        videos = scrape_videos(category)
        print(f"✅ Scraped {len(videos)} videos for '{category}'.")

    else:
        print("⚠️ Invalid choice. Please enter 'images' or 'videos'.")
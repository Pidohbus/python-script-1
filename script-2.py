import requests
from bs4 import BeautifulSoup


def get_page_content(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title of the page
    title = soup.title.string if soup.title else 'No title found'
    return title


# Testing this script with a sample URL
title = get_page_content("https://www.indiatoday.in")

print("Page Title:", title)
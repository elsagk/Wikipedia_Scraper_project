import requests
from bs4 import BeautifulSoup
import re
import json

def get_the_cookies(cookie_url):
    cookies = requests.get(cookie_url).cookies.get_dict()
    return cookies

def get_the_countries(countries_url, cookies):
    countries = requests.get(countries_url, cookies=cookies).json()
    return countries


def get_leaders():
    root_url = "https://country-leaders.onrender.com"
    status_url = "status"
    
    # Check if the website is accessible
    req = requests.get(f"{root_url}/{status_url}")
    if req.status_code != 200:
        print(f"Error accessing the website: {req.status_code}")
        return {}
    
    print(req.text)
    
    # Fetch the countries and cookie
    countries_url = "countries"
    cookie_url = "cookie"
    cookie = requests.get(f"{root_url}/{cookie_url}").cookies
    countries_response = requests.get(f"{root_url}/{countries_url}", cookies=cookie)
    
    if countries_response.status_code != 200:
        print(f"Error fetching countries: {countries_response.status_code}")
        return {}
    
    countries = countries_response.json()
    
    leaders_url = 'leaders'
    leaders_per_country = {}
    for country in countries:
        # Get leaders for each country
        leader_r = requests.get(f"{root_url}/{leaders_url}", cookies=cookie, params={"country": country})
        
        if leader_r.status_code == 200:
            leaders = leader_r.json()
            country_leaders = {}
            
            for leader in leaders:
                full_name = f"{leader.get('first_name')} {leader.get('last_name')}"
                wikipedia_url = leader.get('wikipedia_url')
                
                if wikipedia_url:
                    first_paragraph = get_first_paragraph(wikipedia_url)
                    country_leaders[full_name] = first_paragraph
                    print(f"Leader of {country}: {full_name}, First Paragraph: {first_paragraph}")
            
            leaders_per_country[country] = country_leaders
    
    return leaders_per_country

def get_first_paragraph(wikipedia_url):
    print(wikipedia_url)
    r = requests.get(wikipedia_url)
    
    # Parse HTML content
    soup = BeautifulSoup(r.text, 'html.parser')
    paragraphs = soup.find_all('p')
      #get the 1st paragraph
    first_paragraph = None
    for paragraph in paragraphs:
        text = paragraph.get_text(separator=" ",strip=True)# this fix the words problem
        if text:  #check non-empty paragraphs
            first_paragraph = text
            break
        # clean up the text
    if first_paragraph: 
        first_paragraph = re.sub(r'\(\[\s?.*?\s?\]\s?\/.*?;?\)|\[\s?[a-zA-Z0-9]\s?\]', '', first_paragraph) #  remove like [1], [a]
    
    return first_paragraph

leaders_file = get_leaders()

def save(leaders_per_country):
    with open('leaders.json', 'w') as file:
        json.dump(leaders_per_country, file)


#call the save function
save(leaders_file)


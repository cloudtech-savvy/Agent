from urllib import response
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import requests
from openai import OpenAI
from scholarly import scholarly
import csv
import logging
from django.template.loader import render_to_string
from bs4 import BeautifulSoup



def chat_view(request):
    return render(request, 'chatapp/chat.html')

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        bot_reply = None

        # Try Ollama (llama2) first
        try:
            ollama_url = "http://localhost:11434/api/generate"
            ollama_payload = {
                "model": "llama2",
                "prompt": user_message,
                "stream": False
            }
            ollama_response = requests.post(ollama_url, json=ollama_payload, timeout=30)
            if ollama_response.status_code == 200:
                ollama_data = ollama_response.json()
                bot_reply = ollama_data.get("response", "").strip()
        except Exception:
            bot_reply = None

        # Fallback to OpenAI if Ollama fails
        if not bot_reply:
            try:
                api_key = os.environ.get('OPENAI_API_KEY')
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_reply = response.choices[0].message.content.strip()
            except Exception as e:
                bot_reply = f"[OpenAI error] {str(e)}"

        return JsonResponse({'reply': bot_reply})
    return JsonResponse({'error': 'Invalid request'}, status=400)






logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#########################################################
import requests
from bs4 import BeautifulSoup

# Step 1: Get your API key from the ScraperAPI dashboard
API_KEY = os.environ.get('SCRAPERAPI_KEY')

# Step 2: Define the target URL for your search
# This example searches for authors affiliated with the Catholic University of America
target_url = 'https://scholar.google.com/scholar?q=mauthors:%22Catholic+University+of+America%22'

# Step 3: Construct the ScraperAPI request URL
scraperapi_url = f'http://api.scraperapi.com?api_key={API_KEY}&url={target_url}'

try:
    # Send the request through ScraperAPI
    response = requests.get(scraperapi_url)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Example parsing: Find all researcher profiles on the page
    # The structure might change, so this is an example
    profile_sections = soup.find_all('div', class_='gs_scl')

    if not profile_sections:
        print("No researcher profiles found. The selector might have changed.")

    for profile in profile_sections:
        # Extract the researcher's name
        name_tag = profile.find('h3', class_='gs_ai_name')
        name = name_tag.text.strip() if name_tag else 'Name not found'

        # Extract the researcher's affiliation
        affiliation_tag = profile.find('div', class_='gs_ai_aff')
        affiliation = affiliation_tag.text.strip() if affiliation_tag else 'Affiliation not found'
        
        # Extract paper descriptions (you may need to get the user profile for full details)
        # This is an example of scraping paper snippets from the search results
        paper_snippets = profile.find_all('div', class_='gs_a')
        paper_desc = [s.text.strip() for s in paper_snippets] if paper_snippets else ['No paper snippets found']

        print(f"Researcher: {name}")
        print(f"Affiliation: {affiliation}")
        print(f"Paper Snippets: {paper_desc}")
        print("-" * 20)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")


# ... (Continuing from the previous example)

# Assuming you have the URL for a specific researcher's profile
# You would get this URL by parsing the initial search result
researcher_id = 'INSERT_RESEARCHER_ID_HERE'  # Replace with actual ID
profile_url = f'https://scholar.google.com/citations?user={researcher_id}'

# Make a new request using ScraperAPI
profile_scraperapi_url = f'http://api.scraperapi.com?api_key={API_KEY}&url={profile_url}'
profile_response = requests.get(profile_scraperapi_url)

if profile_response.status_code == 200:
    profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
    
    # Example parsing: Find all articles on the profile page
    articles = profile_soup.find_all('tr', class_='gsc_a_tr')
    
    for article in articles:
        title_tag = article.find('a', class_='gsc_a_at')
        title = title_tag.text.strip() if title_tag else 'Title not found'
        
        description_tag = article.find('span', class_='gsc_a_t_desc')
        description = description_tag.text.strip() if description_tag else 'Description not found'
        
        print(f"Title: {title}")
        print(f"Description: {description}")
        print("-" * 20)


##########################################################
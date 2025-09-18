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

#try semantic scholar api

import requests
import urllib.parse

# Function to search authors by affiliation
def search_authors_by_affiliation(affiliation, limit=10):
    encoded_affiliation = urllib.parse.quote(affiliation)
    url = f"https://api.semanticscholar.org/graph/v1/author/search?query={encoded_affiliation}&limit={limit}&fields=name,affiliations,paperCount,hIndex,url"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    
    data = response.json()
    return data.get("data", [])


# Function to fetch latest papers by author ID
def get_latest_papers(author_id, limit=5):
    url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?limit={limit}&fields=title,year,venue,url"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching papers for {author_id}: {response.status_code}")
        return []
    
    data = response.json()
    return data.get("data", [])


@csrf_exempt
def scholar_profiles(request):
    if request.method == 'GET':
        university = request.GET.get('ViewIt@CatholicU', '').strip()
        if not university:
            return JsonResponse({'error': 'University query parameter is required.'}, status=400)
        limit = int(request.GET.get('limit', 5))
        authors = search_authors_by_affiliation(university, limit=limit)
        results = []
        for author in authors:
            name = author.get("name")
            affils = author.get("affiliations", [])
            papers_count = author.get("paperCount")
            hindex = author.get("hIndex")
            profile_url = author.get("url")
            author_id = author.get("authorId")
            # Fetch latest papers
            latest_pubs = get_latest_papers(author_id, limit=3)
            pubs = []
            for pub in latest_pubs:
                pubs.append({
                    'title': pub.get('title'),
                    'year': pub.get('year'),
                    'venue': pub.get('venue'),
                    'url': pub.get('url'),
                })
            results.append({
                'name': name,
                'affiliations': affils,
                'paperCount': papers_count,
                'hIndex': hindex,
                'profile_url': profile_url,
                'papers': pubs
            })
        return JsonResponse({'results': results})
    return JsonResponse({'error': 'Invalid request'}, status=400)

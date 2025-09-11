from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import requests
from openai import OpenAI
from scholarly import scholarly

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

# --------------- # For Google Scholar scraping-------------


def scholar_profiles(request):
    query = request.GET.get('university', 'The Catholic University of America')
    results = []
    search_query = scholarly.search_author(query)
    for author in search_query:
        profile = {
            'name': author.get('name'),
            'affiliation': author.get('affiliation'),
            'interests': author.get('interests'),
            'scholar_id': author.get('scholar_id'),
            'email_domain': author.get('email_domain'),
        }
        # Fill author to get publications
        author_filled = scholarly.fill(author)
        publications = []
        for pub in author_filled.get('publications', []):
            pub_info = pub.get('bib', {})
            publications.append({
                'title': pub_info.get('title'),
                'year': pub_info.get('pub_year'),
                'venue': pub_info.get('venue'),
            })
        profile['publications'] = publications
        results.append(profile)
        # Limit to first 3 authors for demo purposes
        if len(results) >= 3:
            break
    return JsonResponse({'results': results})
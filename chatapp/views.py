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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def scholar_profiles(request):
    response = request.GET.get('ViewIt@CatholicU', '').strip()
    if not response:
        return JsonResponse({'error': 'University query parameter is required.'}, status=400)

    file_format = request.GET.get('format', 'json').lower()
    results = []
    logger.info(f"Searching for authors with query: {response}")

    try:
        search_query = scholarly.search_author(response)
        authors_found = list(search_query)
        if not authors_found:
            logger.warning(f"No authors found for query: {response}")
            return JsonResponse({'error': 'No authors found for the given query.'}, status=404)

        for author in authors_found:
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
                    'citations': pub.get('num_citations', 0),
                })
            profile['publications'] = publications
            results.append(profile)
            # Limit to first 2 authors for demo purposes
            if len(results) >= 2:
                break
    except Exception as e:
        return JsonResponse({'error': f'Failed to fetch data: {str(e)}'}, status=500)

    if file_format == 'csv':
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{response}_researchers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Affiliation', 'Interests', 'Scholar ID', 'Email Domain', 'Publication Title', 'Year', 'Venue', 'Citations'])
        for profile in results:
            for pub in profile['publications']:
                writer.writerow([
                    profile['name'],
                    profile['affiliation'],
                    ', '.join(profile['interests']),
                    profile['scholar_id'],
                    profile['email_domain'],
                    pub['title'],
                    pub['year'],
                    pub['venue'],
                    pub['citations'],
                ])
        return response

    # Default to JSON response
    return JsonResponse({'results': results})

# --------------- # End of Google Scholar scraping-------------


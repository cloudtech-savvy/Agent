# --------------- # For Google Scholar scraping-------------

from django.http import HttpResponse, JsonResponse
import logging
from scholarly import scholarly
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def scholar_profiles(request):
    response = request.GET.get('ViewIt@CatholicU', 'The Catholic University of America').strip()
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
                'affiliation': author.get('affiliation', 'N/A'),
                'interests': author.get('interests', []),
                'scholar_id': author.get('scholar_id', 'N/A'),
                'email_domain': author.get('email_domain', 'N/A'),
            }

            # Fetch detailed author information
            try:
                author_filled = scholarly.fill(author)
                # Log detailed author data for debugging
                try:
                    logger.info(f"Detailed author data: {author_filled}")
                except Exception as e:
                    logger.error(f"Error logging detailed author data: {str(e)}")

                publications = []
                for pub in author_filled.get('publications', []):
                    pub_info = pub.get('bib', {})
                    publications.append({
                        'title': pub_info.get('title', 'N/A'),
                        'year': pub_info.get('pub_year', 'N/A'),
                        'venue': pub_info.get('venue', 'N/A'),
                        'citations': pub.get('num_citations', 0),
                        'description': pub_info.get('abstract', 'N/A'),  # Add description field
                    })
                profile['publications'] = publications
            except Exception as e:
                logger.error(f"Error fetching detailed author info: {str(e)}")
                profile['publications'] = []

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
        writer.writerow(['Name', 'Affiliation', 'Interests', 'Scholar ID', 'Email Domain', 'Publication Title', 'Year', 'Venue', 'Citations', 'Description'])
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
                    pub['description'],# Include description in CSV
                ])
        return response

    
    return JsonResponse({'results': results})

# --------------- # End of Google Scholar scraping-------------
# --------------- # For Semantic Scholar API -------------

#####################################################################

#try google  scholarly

# Configure logging to capture raw HTML responses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace the `search_authors_by_affiliation` function to use `scholarly`
def search_authors_by_affiliation(affiliation, limit=10):
    search_query = scholarly.search_author(affiliation)
    authors = []
    for author in search_query:
        try:
            # Log the raw HTML response for debugging
            logger.info(f"Raw HTML response for author: {author}")
            authors.append(author)
            if len(authors) >= limit:
                break
        except Exception as e:
            logger.error(f"Error while processing author: {str(e)}")
    return authors


def get_latest_papers(author, limit=5):
    author_filled = scholarly.fill(author)
    papers = []
    for pub in author_filled.get('publications', []):
        pub_info = pub.get('bib', {})
        papers.append({
            'title': pub_info.get('title', 'N/A'),
            'year': pub_info.get('pub_year', 'N/A'),
            'venue': pub_info.get('venue', 'N/A'),
            'url': pub_info.get('url', 'N/A'),
        })
        if len(papers) >= limit:
            break
    return papers


@csrf_exempt
def scholar_profiles(request):
    if request.method == 'GET':
        university = request.GET.get('university', '').strip() or request.GET.get('ViewIt@CatholicU', '').strip()
        if not university:
            return JsonResponse({'error': 'University query parameter is required.'}, status=400)

        # Log the received parameters for debugging
        logger.info(f"Received parameters: {request.GET}")

        # Use Semantic Scholar to fetch profiles
        authors = search_authors_by_affiliation_semantic_scholar(university, limit=5)
        if not authors:
            return JsonResponse({'error': 'No profiles found for the given university.'}, status=404)

        results = []
        for author in authors:
            results.append({
                'name': author.get('name', 'N/A'),
                'affiliations': author.get('affiliations', 'N/A'),
                'paperCount': author.get('paperCount', 'N/A'),
                'hIndex': author.get('hIndex', 'N/A'),
                'url': author.get('url', 'N/A')
            })

        return JsonResponse({'profiles': results})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def scholar_profiles_csv(request):
    if request.method == 'GET':
        university = request.GET.get('ViewIt@CatholicU', '').strip()
        if not university:
            return JsonResponse({'error': 'University query parameter is required.'}, status=400)
        # Search for authors by university
        search_query = scholarly.search_author(university)
        authors_found = list(search_query)
        if not authors_found:
            return JsonResponse({'error': 'No authors found for the given university.'}, status=404)
        
        # Prepare CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{university}_scholar_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['Profile Name', 'Affiliation', 'Interests', 'Scholar ID', 'Email Domain', 'Paper Title', 'Citations', 'Abstract', 'Venue', 'Paper Description'])
        for author in authors_found:
            try:
                author_filled = scholarly.fill(author)
                profile_name = author_filled.get('name', 'N/A')
                affiliation = author_filled.get('affiliation', 'N/A')
                interests = ', '.join(author_filled.get('interests', []))
                scholar_id = author_filled.get('scholar_id', 'N/A')
                email_domain = author_filled.get('email_domain', 'N/A')
                for pub in author_filled.get('publications', []):
                    pub_info = pub.get('bib', {})
                    title = pub_info.get('title', 'N/A')
                    citations = pub.get('num_citations', 0)
                    abstract = pub_info.get('abstract', 'N/A')
                    venue = pub_info.get('venue', 'N/A')
                    description = pub_info.get('abstract', 'N/A') 
                    writer.writerow([
                        profile_name,
                        affiliation,
                        interests,
                        scholar_id,
                        email_domain,
                        title,
                        citations,
                        abstract,
                        venue,
                        description
                    ])
            except Exception as e:
                continue
        return response
    return JsonResponse({'error': 'Invalid request'}, status=400)

#try semantic scholar api
# Configure logging to capture raw HTML responses

def search_authors_by_affiliation_semantic_scholar(affiliation, limit=20):
    url = f"https://api.semanticscholar.org/graph/v1/author/search?query={affiliation}&limit={limit}&fields=name,affiliations,paperCount,hIndex,url"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Semantic Scholar API error: {response.status_code}")
        return []
    data = response.json()
    return data.get("data", [])

@csrf_exempt
def scholar_profiles_with_fallback(request):
    if request.method == 'GET':
        # Handle both `university` and `ViewIt@CatholicU` parameters
        university = request.GET.get('university', '').strip() or request.GET.get('ViewIt@CatholicU', '').strip()
        if not university:
            return JsonResponse({'error': 'University query parameter is required.'}, status=400)

        # Log the received parameters for debugging
        logger.info(f"Received parameters: {request.GET}")

        # Try Google Scholar first
        authors = search_authors_by_affiliation(university, limit=5)
        if not authors:
            logger.warning("Google Scholar returned no results. Falling back to Semantic Scholar.")

            # Fallback to Semantic Scholar
            authors = search_authors_by_affiliation_semantic_scholar(university, limit=10)

        if not authors:
            return JsonResponse({'error': 'No authors found for the given university.'}, status=404)

        results = []
        for author in authors:
            results.append({
                'name': author.get('name', 'N/A'),
                'affiliations': author.get('affiliations', 'N/A'),
                'paperCount': author.get('paperCount', 'N/A'),
                'hIndex': author.get('hIndex', 'N/A'),
                'url': author.get('url', 'N/A')
            })  

        return JsonResponse({'results': results})
    return JsonResponse({'error': 'Invalid request'}, status=400)


######################################################################
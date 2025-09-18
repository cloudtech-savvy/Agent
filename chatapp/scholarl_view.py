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
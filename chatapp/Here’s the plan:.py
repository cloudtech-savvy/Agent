Here’s the plan:

1. Use Django's `RequestFactory` to simulate a GET request to the `scholar_profiles` view.
2. Mock the `scholarly.search_author` and `scholarly.fill` functions since they interact with Google Scholar and require external data.
3. Verify the response status and ensure the returned JSON contains the
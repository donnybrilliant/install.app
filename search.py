def search_packages(packages_data, query):
    # Ensure the query is a lowercase string for case-insensitive comparison
    query = query.lower()
    # Filter packages based on the query matching any part of the package name or description
    return [pkg for pkg in packages_data if query in pkg['name'].lower() or query in (pkg.get('desc') or '').lower()]

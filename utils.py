import os
import sys
def get_resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

def search_packages(packages_data, query):
    # Ensure the query is a lowercase string for case-insensitive comparison
    query = query.lower()
    # Filter packages based on the query matching any part of the package name or description
    return [pkg for pkg in packages_data if query in pkg['name'].lower() or query in (pkg.get('desc') or '').lower()]

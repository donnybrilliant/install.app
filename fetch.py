import requests

def fetch_homebrew_data():
    formulae_url = "https://formulae.brew.sh/api/formula.json"
    casks_url = "https://formulae.brew.sh/api/cask.json"

    formulae_response = requests.get(formulae_url)
    casks_response = requests.get(casks_url)

    formulae_data = formulae_response.json() if formulae_response.ok else []
    casks_data = casks_response.json() if casks_response.ok else []

    

    combined_data = [{"name": f["name"], "type": "formulae", "desc": f.get("desc", "No description available"), "homepage": f.get("homepage", "No homepage available"), "license": f.get("license", "No license information available"), "stable_version": f['versions'].get('stable') if 'versions' in f and isinstance(f['versions'], dict) else 'Not available'} for f in formulae_data] + \
                    [{"name": c["token"], "type": "cask", "desc": c.get("desc", "No description available"), "homepage": c.get("homepage", "No homepage available"), "license": c.get("license", "No license information available"), "stable_version": c['versions'].get('stable') if 'versions' in c and isinstance(c['versions'], dict) else 'Not available'} for c in casks_data]

    return combined_data

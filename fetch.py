import requests

def fetch_homebrew_data():
    formulae_url = "https://formulae.brew.sh/api/formula.json"
    casks_url = "https://formulae.brew.sh/api/cask.json"

    formulae_response = requests.get(formulae_url)
    casks_response = requests.get(casks_url)

    formulae_data = formulae_response.json() if formulae_response.ok else []
    casks_data = casks_response.json() if casks_response.ok else []

    combined_data = [{"name": f["name"], "desc": f.get("desc", "No description available"), "homepage": f.get("homepage", ""), "license": f.get("license", "")} for f in formulae_data] + \
                    [{"name": c["token"], "desc": c.get("desc", "No description available"), "homepage": c.get("homepage", ""), "license": c.get("license", "")} for c in casks_data]

    return combined_data

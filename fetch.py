import requests
import os
import tempfile
from utils import get_resource_path

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

def generate_homebrew_install_commands(selected_packages):
    # Lists to hold selected formulae and casks
    selected_formulae = [package for package, package_type in selected_packages.items() if package_type == 'formulae']
    selected_casks = [package for package, package_type in selected_packages.items() if package_type == 'cask']

    # Generate a single command for installing all formulae, and another for all casks
    formulae_install_command = f"brew install {' '.join(selected_formulae)}" if selected_formulae else ""
    cask_install_command = f"brew install --cask {' '.join(selected_casks)}" if selected_casks else ""

    # Combine the commands into a single script section, separating them by a newline if both are present
    script_section = "\n".join(filter(None, [formulae_install_command, cask_install_command]))
    return script_section

def update_install_script_with_homebrew_commands(selected_packages):
    homebrew_install_commands = generate_homebrew_install_commands(selected_packages)
    placeholder = "#BREWPACKAGES#"

    template_path = get_resource_path("install.sh")

    with open(template_path, "r") as template_file:
        script_content = template_file.read()

    updated_script_content = script_content.replace(placeholder, homebrew_install_commands)

    temp_dir = tempfile.gettempdir()
    install_script_path = os.path.join(temp_dir, "install_script.sh")
    with open(install_script_path, "w") as script_file:
        script_file.write(updated_script_content)

    return install_script_path
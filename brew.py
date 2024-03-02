import subprocess

def fetch_casks_from_brew(query):
    command = ["brew", "search", query]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        casks = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return casks
    except subprocess.CalledProcessError as e:
        print(f"Error fetching casks: {e}")
        return []
import json
import requests
import re
from urllib.parse import urlparse
import urllib.request

# Replace with your GitHub credentials or personal access token
GITHUB_TOKEN = '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'
GH_SESSION_TOKEN = 'sBvEmWUm786UjzuFqJ2aOOebk5YeiwLtUboUdko_aDD9GHl5'
# REPO_PROJS = {'AntennaPod':['AntennaPod']}
REPO_PROJS={ 'AntennaPod':['AntennaPod']}


# Headers for API requests
headers = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'ngimhana'
}

def get_number_of_pages(ISSUES_URL):
    response = requests.get(ISSUES_URL, headers=headers)
    if response.status_code == 200:
        pages = response.headers.get('link')
        if pages == None:
            return 1
        pages = int(pages.split(',')[1].split(';')[0].split('=')[2].split('>')[0])
        return pages
    else:
        return 1

def download_mp4(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    else:
        print(f"Failed to download: {url}")

def save_issue_data(repo, project, issue_json):
    ## save json to file
    with open(f"src/experiments/json/{repo}_{project}_issue_{issue_json['number']}.json", 'w') as file:
        file.write(json.dumps(issue_json, indent=4))


def main():
    
        # Headers for API requests
        headers = {
            'Authorization': f'Bearer {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent' : 'ngimhana'
        }
        page_dict = {}
        for repo_owner in REPO_PROJS.keys():
            for repo_name in REPO_PROJS[repo_owner]: 
                # API endpoint URLs
                BASE_URL = f'https://api.github.com/repos/{repo_owner}/{repo_name}'
                ISSUES_URL = f'{BASE_URL}/issues?state=all'

                ## read experiment.json file if it is not empty
                current_page = 1
                with open("src/experiments/experiment.json", 'r') as file:
                    data = file.read()
                    if data:
                        data = json.loads(data)
                        if f"{repo_owner}/{repo_name}" in data.keys():
                            current_page = data[f"{repo_owner}/{repo_name}"]
                            print(f"Current page: {current_page}")

                pages = get_number_of_pages(ISSUES_URL=ISSUES_URL)
                
                for i in range(current_page, pages+1):
                    ISSUES_URL_PAGE= f'{ISSUES_URL}&page={i}'
                    # Fetch issues from the repository
                    response = requests.get(ISSUES_URL_PAGE, headers=headers)

                    if response.status_code == 200:
                        issues = response.json()
                        ## remove issues with pull_request key
                        issues = [issue for issue in issues if 'pull_request' not in issue]
                        
                        for issue in issues:
                            content_to_check = f"{issue['title']} {issue['body']}"
                            
                            ## Fetch comments for the issue
                            # comments_url = f"{BASE_URL}/issues/{issue['number']}/comments"
                            # comments_response = requests.get(comments_url, headers=headers)
                            # comments = comments_response.json()
                            
                            # for comment in comments:
                            #     content_to_check += f" {comment['body']}"
                            
                            ## download the mp4 from links
                            if re.search(r'\.(mp4|avi)', content_to_check, re.IGNORECASE):
                                print(f"Processing Issue #{issue['number']}: {issue['title']}")

                                ## find all the mp4 links
                                mp4_links = re.findall(r'(https?://[^\s]+\.mp4)', content_to_check, re.IGNORECASE) 
                            
                                for index, mp4_link in enumerate(mp4_links):
                                    mp4_filename = f"issue_{issue['number']}_video_{index+1}.{mp4_link.split('.')[-1]}"
                                    print(f"  Downloading video: {mp4_link}")
                                    download_mp4(mp4_link, "src/experiments/videos/" + repo_owner + "_" + repo_name + "_" + mp4_filename)
                                    save_issue_data(repo_owner, repo_name, issue)
                        
                            
                            ## download the mp4 from assets links
                            pattern = r'https://github.com/\S+/assets/\S+/[a-z0-9A-Z\-]+'
                            mp4_links = re.findall(pattern, content_to_check, re.IGNORECASE)
                        
                            for url in mp4_links:
                                headers = {
                                    "cookie": f"user_session={GH_SESSION_TOKEN};",
                                    'User-Agent': 'ngimhana'
                                }
                                req = urllib.request.Request(url, headers=headers)
                                with urllib.request.urlopen(req) as u:
                                    if u.getcode() != 200:
                                        print(f"Failed to download: {url}")
                                        continue
                                    # Get the file name from the URL
                                    filename = urlparse(u.geturl()).path.split('/')[-1]
                                    
                                    if filename.endswith('.mp4') or filename.endswith('.avi'):
                                        print(f"  Downloading video: {filename}")
                                        download_mp4(u.geturl(), "src/experiments/videos/"+ repo_owner+"_"+repo_name + "_" + filename)
                                        save_issue_data(repo_owner, repo_name, issue)

                        page_dict[f"{repo_owner}/{repo_name}"]= i

                        ## write the current page number
                        with open("src/experiments/experiment.json", 'r') as file:
                            data = file.read()
                            if data:
                                data = json.loads(data)
                                data.update(page_dict)
                                with open("src/experiments/experiment.json", 'w') as file:
                                    file.write(json.dumps(data, indent=4))
                            else:
                                with open("src/experiments/experiment.json", 'w') as file:
                                    file.write(json.dumps(page_dict, indent=4))

                                    
                    else:
                        print(str(response.status_code) + " " + response.content.decode())
                        break    
 

if __name__ == "__main__":
    main()
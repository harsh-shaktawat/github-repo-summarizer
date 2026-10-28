from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import os
import asyncio, httpx, random

load_dotenv()

class RepoInfo(BaseModel):
    name: str
    stars: int
    language: str | None
    openIssues: int
    publishDate: str
    
links = ["https://api.github.com/repos/encode/httpx",
         "https://api.github.com/repos/psf/requests",
         "https://api.github.com/repos/pallets/flask",
         "https://api.github.com/repos/pydantic/pydantic",
         "https://api.github.com/repos/django/django",
         "https://api.github.com/repos/django/harsh",
         ]

github_token = os.environ["GITHUB_TOKEN"]

async def get_with_backoff(client:httpx.AsyncClient, link:str, headers=None, max_retries=4):
    delay = 1                                    # first wait: 1 second
    for attempt in range(max_retries + 1):
        response = await client.get(link, headers=headers)
        if response.status_code != 429 or attempt == max_retries:
            return response                      # success, a different error, or out of retries
        wait = float(response.headers.get("Retry-After", delay))  # obey the server if it says
        wait += random.uniform(0, 0.5)           # jitter
        print(f"attempt {attempt + 1}: got 429, waiting {wait:.1f}s")
        await asyncio.sleep(wait)                # asyncio.sleep, not time.sleep
        delay *= 2                               # 1 -> 2 -> 4 -> 8

async def fetch(link:str, client:httpx.AsyncClient, sem:asyncio.Semaphore)-> RepoInfo|None:
    try:
        async with sem:
            response = await get_with_backoff( 
                client, link, headers={"Authorization": f"Bearer {github_token}"}
                )
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {link}: {e}")
        return None
    if response.status_code == 200:
        try:
            data = response.json()
            repo_info = RepoInfo(
                name=data["name"],
                stars=data["stargazers_count"],
                language=data["language"],
                openIssues=data["open_issues_count"],
                publishDate=data["created_at"]
            )
            return repo_info
        except (KeyError, ValueError,ValidationError) as e:
            print(f"An error occurred while processing data for {link}: {e}")
            return None
    elif response.status_code == 404:
        print(f"Repository not found for {link}")
        return None
    elif response.status_code == 429:
        print(f"Rate limit exceeded for {link}. Please try again later.")
        return None
    else:
        print(f"Failed to fetch data for {link}: {response.status_code}")
        return None

async def main():
    sem=asyncio.Semaphore(3)  # Limit concurrent requests to 3
    async with httpx.AsyncClient(timeout=30) as client:
        tasks= (fetch(link,client,sem) for link in links)
        results = await asyncio.gather(*tasks)

    repos = [repo for repo in results if repo is not None]
    repos.sort(key=lambda x: x.stars, reverse=True)
    print("Top repositories by stars:")
    for repo in repos:
        print(f"{repo.name}: {repo.stars} stars, Language: {repo.language}, Open Issues: {repo.openIssues}, Published on: {repo.publishDate}")
asyncio.run(main())
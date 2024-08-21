#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
from urllib.parse import urlparse
import subprocess
import time

# List of blacklisted GitHub path segments or owner names
BLACKLISTED_OWNERS = [
    "features",
    "login",
    "explore",
    "marketplace",
    "topics",
    "collections",
    "enterprise",
    "solutions",
    "sponsors",
]


def check_rate_limit(response):
    """
    Check the rate limit from the response headers and sleep if the limit is reached.
    """
    limit = int(response.headers.get("X-RateLimit-Limit", 60))
    remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))

    if remaining == 0:
        sleep_time = max(reset_time - time.time(), 0)
        print(f"Rate limit reached. Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)
        return True
    return False


def is_valid_github_repo_url(url):
    """
    Check if the URL is a valid GitHub repository URL and not in the blacklist.
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")

    # Check if the URL is in the form of github.com/{owner}/{repo}
    if parsed_url.netloc == "github.com" and len(path_parts) == 2:
        owner = path_parts[0]

        # Exclude blacklisted owners
        if owner not in BLACKLISTED_OWNERS:
            return True

    return False


def extract_github_links(url):
    """
    Given a URL, this function fetches all valid GitHub repository links from the page.

    Args:
    url (str): The URL of the webpage to scrape.

    Returns:
    list: A list of valid GitHub repository URLs found on the page.
    """
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    all_links = soup.find_all("a", href=True)

    # Filter links to only include valid GitHub repository URLs
    github_links = [
        (
            link["href"]
            if link["href"].startswith("http")
            else f"https://github.com{link['href']}"
        )
        for link in all_links
        if is_valid_github_repo_url(link["href"])
    ]

    return github_links


def get_github_auth_token():
    """
    Check if the user is authenticated with GitHub CLI and retrieve the token.
    If not authenticated, return None.
    """
    try:
        # Run the command to check if the user is authenticated with GitHub CLI
        result = subprocess.run(
            ["gh", "auth", "status", "--show-token"], capture_output=True, text=True
        )

        if result.returncode == 0:
            # Look for the line that contains the token in the output
            for line in result.stdout.splitlines():
                if line.strip().startswith("- Token:"):
                    return line.split(":", 1)[1].strip()  # Extract and return the token
        else:
            print("GitHub CLI not authenticated. Using unauthenticated requests.")
    except FileNotFoundError:
        print("GitHub CLI not found. Using unauthenticated requests.")

    return None


def get_github_repo_popularity(github_urls, max_failures=5):
    """
    Given a list of GitHub repository URLs, this function fetches the popularity metrics (stars, forks, watchers)
    from the GitHub API.

    Args:
    github_urls (list): List of GitHub repository URLs.
    max_failures (int): Maximum number of consecutive failures allowed before exiting.

    Returns:
    dict: A dictionary with the repository URL as the key and another dictionary with stars, forks, and watchers count as the value.
    """
    repo_popularity = {}
    base_api_url = "https://api.github.com/repos"
    consecutive_failures = 0

    # Check if the user is authenticated with GitHub CLI and get the token
    token = get_github_auth_token()

    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        print("Sending authenticated requests using the GitHub CLI token.")
    else:
        print("Sending unauthenticated requests.")

    for url in github_urls:
        print(f"Attempting to ingest data from: {url}")

        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip("/").split("/")

            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo_name = path_parts[1]
                api_url = f"{base_api_url}/{owner}/{repo_name}"
                response = requests.get(api_url, headers=headers)

                if check_rate_limit(response):
                    response = requests.get(
                        api_url, headers=headers
                    )  # Retry after sleeping

                if response.status_code == 200:
                    data = response.json()
                    stars = data.get("stargazers_count", 0)
                    forks = data.get("forks_count", 0)
                    watchers = data.get("watchers_count", 0)

                    repo_popularity[url] = {
                        "stars": stars,
                        "forks": forks,
                        "watchers": watchers,
                    }
                    consecutive_failures = (
                        0  # Reset the failure count after a successful request
                    )
                else:
                    print(
                        f"Failed to retrieve data for {url}. Status code: {response.status_code}"
                    )
                    consecutive_failures += 1
            else:
                print(f"Invalid GitHub URL format: {url}")
                consecutive_failures += 1

            if consecutive_failures >= max_failures:
                print(
                    f"Exceeded the maximum number of consecutive failures ({max_failures}). Exiting."
                )
                break
        except Exception as e:
            print(f"An error occurred while processing {url}: {str(e)}")
            consecutive_failures += 1

            if consecutive_failures >= max_failures:
                print(
                    f"Exceeded the maximum number of consecutive failures ({max_failures}). Exiting."
                )
                break

    return repo_popularity


def save_to_json(data, file_path):
    """
    Save a dictionary or list as a JSON file.

    Args:
    data (dict or list): The data to be saved as JSON.
    file_path (str or Path): The file path where the JSON file will be saved.
    """
    file_path = Path(file_path)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")


def generate_output_path_from_url(url):
    """
    Generate a file path based on the given URL.

    Args:
    url (str): The URL to generate the file path from.

    Returns:
    str: The generated file path.
    """
    parsed_url = urlparse(url)
    path = Path(parsed_url.netloc) / parsed_url.path.strip("/")
    return str(path) + ".json"


def main():
    parser = argparse.ArgumentParser(
        description="Ingest data from a URL and save GitHub repo popularity metrics as JSON."
    )
    parser.add_argument(
        "url", type=str, help="The URL of the webpage to scrape for GitHub links."
    )
    parser.add_argument(
        "--output",
        type=str,
        help="The file path to save the output JSON file. If not provided, the path is derived from the URL.",
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=5,
        help="The maximum number of consecutive failures allowed before exiting. Default is 5.",
    )

    args = parser.parse_args()

    print(f"Extracting GitHub links from {args.url}...")
    github_links = extract_github_links(args.url)

    if not github_links:
        print("No valid GitHub repository links found on the page.")
        return

    print("Fetching popularity metrics for the GitHub repositories...")
    popularity_data = get_github_repo_popularity(
        github_links, max_failures=args.max_failures
    )

    output_path = (
        args.output if args.output else generate_output_path_from_url(args.url)
    )

    print(f"Saving data to {output_path}...")
    save_to_json(popularity_data, output_path)


if __name__ == "__main__":
    main()

"""Fetch posts from Reddit for the Reddit feed page."""
import requests


def get_reddit_posts(subreddit="python"):
    """
    Fetch posts from a given subreddit.

    Parameters
    ----------
    subreddit : str, optional
        The subreddit to fetch posts from. Defaults to "python".

    Returns
    -------
    list
        A list of dictionaries, each containing the title, author, and URL
        of a post from the given subreddit.
    """
    # Build the URL for the subreddit's JSON feed
    url = f"https://www.reddit.com/r/{subreddit}/.json"
    headers = {"User-Agent": "DjangoEcommerceApp/1.0"}  # Required by Reddit

    # Make the request
    response = requests.get(url, headers=headers)

    # Handle errors
    if response.status_code != 200:
        print("Failed to fetch data.")
        return None

    # Parse the JSON response
    data = response.json()
    posts = []

    # Extract useful fields from each post
    for item in data["data"]["children"]:
        post = item["data"]
        posts.append({
            "title": post["title"],
            "author": post["author"],
            "url": post["url"]
        })

    return posts

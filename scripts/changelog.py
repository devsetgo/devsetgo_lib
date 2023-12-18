# -*- coding: utf-8 -*-
import httpx
import json
from datetime import datetime
import pytz


async def get_github_releases():
    url = f"https://api.github.com/repos/devsetgo/devsetgo_lib/releases"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    # Raise an exception if the request was unsuccessful
    return response.json()


def set_date_time(published_at):
    published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")

    # Make it aware in UTC
    published_at = pytz.utc.localize(published_at)

    # Convert to US Eastern Time
    published_at = published_at.astimezone(pytz.timezone("US/Eastern"))

    # Format it to a more human-readable format
    return published_at.strftime("%Y %B %d, %H:%M")


async def main():
    # Fetch releases from a GitHub repository
    releases = await get_github_releases()

    # Reverse the list of releases
    # releases.reverse()

    # Read the markdown file into memory
    with open("CHANGELOG.md", "r") as f:
        lines = f.readlines()

    # Find the line with "## Latest Changes"
    index = lines.index("## Latest Changes\n") + 1

    # Slice the list of lines at the index of "## Latest Changes"
    lines = lines[:index]

    # Loop over the releases
    for release in releases:
        # Extract the release name, tag name, release date, and release URL
        name = release["name"]
        tag_name = release["tag_name"]
        published_at = set_date_time(release["published_at"])
        body = release["body"]
        release_url = release["html_url"]

        # Format the release information into markdown
        markdown = f"### <span style='color:blue'>{name}</span> ([{tag_name}]({release_url}))\n\n{body}\n\nPublished Date: {published_at}\n\n"

        # Append the markdown to the list of lines
        lines.append(markdown)

    # Write the modified content back to the file
    with open("CHANGELOG.md", "w") as f:
        f.writelines(lines)


# Run the main function
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

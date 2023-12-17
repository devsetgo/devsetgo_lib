import httpx
import json

async def get_github_releases():
    url = f"https://api.github.com/repos/devsetgo/devsetgo_lib/releases"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
     # Raise an exception if the request was unsuccessful
    return response.json()

async def main():
    # Fetch releases from a GitHub repository
    releases = await get_github_releases()

    # Reverse the list of releases
    # releases.reverse()

    # Read the markdown file into memory
    with open('CHANGELOG.md', 'r') as f:
        lines = f.readlines()

    # Find the line with "## Latest Changes"
    index = lines.index('## Latest Changes\n') + 1

    # Slice the list of lines at the index of "## Latest Changes"
    lines = lines[:index]

    # Loop over the releases
    for release in releases:
        # Extract the release name, tag name, and release date
        name = release['name']
        tag_name = release['tag_name']
        published_at = release['published_at']
        body = release['body']
        # Add three more # to the start of the body if it starts with #
        if body.startswith('#'):
            body = '###' + body
        # Format the release information into markdown
        markdown = f"### {name} ({tag_name})\n\n{body}\n\nPublished at: {published_at}\n\n"

        # Append the markdown to the list of lines
        lines.append(markdown)

    # Write the modified content back to the file
    with open('CHANGELOG.md', 'w') as f:
        f.writelines(lines)

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
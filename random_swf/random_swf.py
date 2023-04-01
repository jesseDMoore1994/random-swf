import random
import os
import subprocess
from bs4 import BeautifulSoup
from returns.io import IO, impure_safe
from returns.pipeline import flow
import requests
from typing import List, Tuple
from typing_extensions import Protocol
from returns.context import RequiresContext


class _Settings(Protocol):
    blacklist: List[str]


def flatten(items: list) -> list:
    for i, _ in enumerate(items):
        while i < len(items) and isinstance(items[i], list):
            items[i : i + 1] = items[i]
    return items


def parse_url(url: str) -> RequiresContext[List[str], _Settings]:
    def get_page(url: str) -> dict:
        session = requests.Session()
        res = session.get(
            url,
            headers={
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    ' (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
                )
            }
        )
        res.raise_for_status()
        return {
            "base_url": url,
            "content": res.content.decode("utf-8")
        }

    def _return_file(settings):
        return url

    def _recurse_dirs(settings):
        page = get_page(url)
        links = [
            f"{page['base_url']}{link.get('href')}"
            for link in BeautifulSoup(page["content"], "html.parser").find_all('a')
            if link.get('href') not in settings["blacklist"]
        ]
        return [parse_url(x)(settings) for x in links]

    if os.path.basename(url):
        return RequiresContext(_return_file)
    return RequiresContext(_recurse_dirs)


def get_swf(url: str):
    with open(f"/tmp/{os.path.basename(url)}", 'wb') as f:
        f.write(requests.get(url).content)


def main():
    swf = random.choice(flatten(parse_url("https://locker.phinugamma.org/swf/")({
        "blacklist": [
            "../",
            "addictinggames/",
            "armorgames/",
            "miniclip/",
        ]
    })))
    get_swf(swf)
    print(f"/tmp/{os.path.basename(swf)}")


if __name__ == "__main__":
    main()

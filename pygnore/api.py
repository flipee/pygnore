import os

from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin

from pygnore.exceptions import UnsupportedTemplateError
from cachetools import cached, TTLCache

GITIGNORE_SERVER = os.environ.get("GITIGNORE_SERVER", "https://gitignore.io/api/")

gitignore_api = (
    GITIGNORE_SERVER if GITIGNORE_SERVER.endswith("/") else GITIGNORE_SERVER + "/"
)


cache = TTLCache(maxsize=1, ttl=300)


@cached(cache)
def get_templates():
    request = urljoin(gitignore_api, "list")
    try:
        response = urlopen(request).read().decode()
    except (HTTPError, URLError, ValueError):
        raise

    template_list = [y for i in response.split("\n") for y in i.split(",")]
    return template_list


def get_gitignore(templates):
    template_list = get_templates()

    for i in templates:
        if i.lower() not in template_list:
            raise UnsupportedTemplateError(i)

    formated_templates = ",".join(templates)

    request = urljoin(gitignore_api, formated_templates)
    try:
        response = urlopen(request).read().decode()
    except (HTTPError, URLError, ValueError):
        raise

    return response.strip()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import StringIO
from markdown import Markdown
from urllib.parse import urlparse
from urllib.error import URLError
import scripts.scrap_github_api as scraper

def get_contributing_file(repository_url):
    """Scraps the text in a CONTRIBUTING file of a repository hosted on GitHub.

    Args:
        owner: String representing the organization or user owner of the repository.
        name: String representing the repository name.
    Returns:
        A list of paragraphs containing the text content of the documentation file.
    """

    repository_owner, repository_name = parse_repository_from_url(repository_url)

    github_api = scraper.Create()

    try:
        # The community profile is used to get documentation resources of a repository. 
        # The definition of community profile is available at the API documentation:
        # developer.github.com/v3/repos/community.
        community_profile_url = 'https://api.github.com/repos/{}/{}/community/profile'.format(repository_owner,repository_name)
        community_profile = github_api.request(community_profile_url)
        
        # From the community profile, we get the path where the description of the CONTRIBUTING file
        # is located. Different projects may define a CONTRIBUTING file in different ways (e.g. CONTRIBUTING.md, CONTRIBUTING.rst),
        # and that's why we take this ellaborated approach.
        contributing_url = community_profile['files']['contributing']['url']
        contributing_description = github_api.request(contributing_url)
        
        # From the description of the CONTRIBUTING file, we use the download URL to get the raw version of it.
        contributing_download_url = contributing_description['download_url']
        contributing_file = github_api.request(contributing_download_url, file_type='text')
    except TypeError as e:
        raise TypeError("The community profile of the requested project does not contain a CONTRIBUTING.md file.")
    except Exception as e:
        raise Exception(e)

    escaped_contributing_file = escape_markdown_from_file(contributing_file)
    paragraphs = escaped_contributing_file.splitlines()

    return paragraphs

def parse_repository_from_url(repository_url):
    path_elements = (urlparse(repository_url).path).split('/')

    if len(path_elements) >= 3 and len(path_elements[2]) > 0:
        return path_elements[1], path_elements[2]
    else:
        raise URLError('The URL must refer to a public repository on GitHub (e.g. https://github.com/atom/atom/).')

def markdown_to_plain_text(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        markdown_to_plain_text(sub, stream)
    if element.tail:
        stream.write(element.tail)

    return stream.getvalue()

def escape_markdown_from_file(contributing_file):
    """ Escape the markdown syntax and leave only plain-text.

    All the code used in this method is based on this answer from StackOverflow:
    https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text/
    All credits to Pavel Vorobyov, who shared with the community this beautiful and simple solution!

    PS: In my original solution (used to train the classifier), I used c-mark-gfm to convert the documents
    to plain-text. It required the developer to have a build of c-mark-gfm installed locally, which could be problematic.
    Hopefully, this solution will have the same effect as c-mark-gfm. Thanks again Pavel!
    """
    Markdown.output_formats["plain"] = markdown_to_plain_text
    converter = Markdown(output_format="plain")
    converter.stripTopLevelTags = False

    return converter.convert(contributing_file)
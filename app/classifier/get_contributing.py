#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import platform
import subprocess
from urllib.parse import urlparse
import classifier.scrap_github_api as scraper

def get_contributing_file(repository_url):
    """Scraps the text in a CONTRIBUTING file of a repository hosted on GitHub.

    Args:
        owner: String representing the organization or user owner of the repository.
        name: String representing the repository name.
    Returns:
        A list of paragraphs containing the text content of the documentation file.
    """

    repository_owner, repository_name = parse_repository_from_url(repository_url)

    if repository_owner == None or repository_name == None:
        return None

    project_filepath = os.path.join('temp', repository_owner + '_' + repository_name + '.txt')

    if not os.path.isdir('temp'):
        os.mkdir('temp')

    github_api = scraper.Create()

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

    with open(project_filepath, 'w', encoding='utf-8') as project_file:
        project_file.write(contributing_file)

    contributing_file = escape_markdown_from_file(project_filepath)
    # Delete file once it is used
    os.remove(project_filepath)

    paragraphs = split_file_into_paragraphs(contributing_file)

    return paragraphs

def parse_repository_from_url(repository_url):
    try:
        path_elements = (urlparse(repository_url).path).split('/')

        if len(path_elements) >= 3:
            return path_elements[1], path_elements[2]
    except:
        raise("Invalid arguments in URL.")
    
    return None, None
    
def split_file_into_paragraphs(content):
    """Splits the content of a documentation file into paragraphs.

    To organize the content of a documentation file into a spreadsheet, first we
    divide it in paragraphs. We consider as paragraphs "one or more consecutive
    lines of text, separated by one or more blank lines (A blank line is any line
    that looks like a blank line — a line containing nothing but spaces or tabs is
    considered blank)". 

    The only exception are the un/ordered lists, which we consider separately as
    paragraphs. We did it because we noticed that some lists contained a significant
    amount of relevant information per item, and dividing it could help us to 
    increase the number of instances for analysis.

    Args:
        content: A string containing the content of a documentation file, including
            empty spaces, line breaks, etc.
    Returns:
        A list of strings, where each string represents a paragraph of the 
        documentation file.
    References:
        Markdown Syntax, by Jhon Gruber:
            daringfireball.net/projects/markdown/syntax
        GitHub Flavored Markdown Spec:
            github.github.com/gfm
    """

    lines = content.splitlines()
    text = []
    paragraph = []

    for line in lines:
        line = line.strip()

        # If line is empty, create a new paragraph
        if not line:
            if len(paragraph) > 0:
                text.append('\n'.join(paragraph))
                paragraph = []
        # If line is a list item, create a new paragraph:
        elif line.startswith(('-','+','*'))\
             or re.match(r"\d{1,9}\..*", line)\
             or re.match(r"\d{1,9}\).*", line):
             
            if len(paragraph) > 0:
                text.append('\n'.join(paragraph))
                paragraph = []                
            paragraph.append(line)
        # Else, append line to paragraph
        else:
            paragraph.append(line)
    
    if len(paragraph) > 0:
        text.append('\n'.join(paragraph))
        paragraph = []

    return text

def escape_markdown_from_file(project_filepath):
    """ Escape the markdown syntax and leave only plaintext. 

    To train the classifier, we locally installed the GitHub Flavored Markdown and
    converted the content of each documentation to plaintext. I've tried to use more
    simplistic approaches in here (e.g. BeautifulSoup), but none of them are as clear as
    this local alternative so far. I am open to suggestions!
    """

    if "Windows" in platform.system():
        # Redefine this variable with your own filepath to cmark-gfm.exe
        cmark_gfm_exe_path = 'C:\\Users\\fronchettl\\Documents\\cmark-gfm\\cmark-gfm-master\\build\\src\\cmark-gfm.exe'

        if os.path.isfile(cmark_gfm_exe_path):
            plaintext = subprocess.run([cmark_gfm_exe_path, project_filepath, '--to', 'plaintext'], stdout=subprocess.PIPE).stdout.decode('utf-8')

            with open(project_filepath, 'w', encoding='utf-8') as project_file:
                project_file.write(plaintext)
        else:
            print('Please, update the filepath to the `cmark-gfm.exe` file inside the\
                get_contributing.py file')
            print('If you do not have cmark-gfm installed, please visit their\
                repository and install it: github.com/github/cmark-gfm')
            raise Exception('The cmark-gfm.exe path is undefined')
    elif "Linux" in platform.system():
        try:
            plaintext = subprocess.run(['cmark-gfm', project_filepath, '--to', 'plaintext'], stdout=subprocess.PIPE).stdout.decode('utf-8')

            with open(project_filepath, 'w', encoding='utf-8') as project_file:
                project_file.write(plaintext)
        except: 
            raise Exception('There is a problem with cmark-gfm. Make sure you have it\
                            installed on your machine.')
    else:
        raise Exception('At the moment, we do not support your operating system\
                    because of our local execution of cmark-gfm. Feel free to work\
                    on it in the get_contributing.py file, escape_markdown_from_file method.\
                    Pull-requests are appreciated.')       

    return plaintext

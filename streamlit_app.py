#!/usr/bin/env python
# -*- coding: utf-8 -*-

import streamlit as page
from about_section import write_about_section
from motivation_section import write_motivation_section
from classifier_section import write_contributing_analysis

page.set_page_config(
     page_title="CONTRIBUTING.info",
     page_icon="📋",
     layout="centered",
     initial_sidebar_state="collapsed",
 )

page.markdown(
    """
    <style>
    .custom-page-header {
        font-size: 30px !important;
        font-weight: bold;
    }

    .custom-page-title {
        font-size: 22px !important;
        font-weight: bold;
    }

    .custom-container { 
        padding: 15px;
        border-radius: 5px;
        background-color: #ebebeb;
    }

    .custom-percentage { 
        padding: 15px;
        text-align: center;
        border-radius: 5px;
        background-color: #ebebeb;
    }

    .container-dominant { 
        padding: 15px;
        text-align: center;
        border-radius: 5px;
        background-color: #b6cfae;
    }

    .container-missing { 
        padding: 15px;
        text-align: center;
        border-radius: 5px;
        background-color: #d9a89c ;
    }

    .container-warning { 
        padding: 15px;
        text-align: center;
        border-radius: 5px;
        background-color: #e3e3e3;
    }

    a { 
        color: #47809e !important;
        text-decoration: none;
    }

    * {
        font-size: 20px !important;
    }

    hr {
        border: 1px solid #d1d1d1;
        border-radius: 5px;
        padding: 0px !important;
        margin: 0px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

page.markdown('<p class="custom-page-header">CONTRIBUTING.info</p>', unsafe_allow_html=True)

about, motivation, classifier = page.tabs(["About", "Motivation", "Classifier"])

with about:
    write_about_section(page)

with motivation:
    write_motivation_section(page)

with classifier:
    repository_url = page.text_input("What GitHub repository would you like to\
                 analyse?", help="The URL must refer to a public repository hosted on GitHub with a CONTRIBUTING.md file.", 
                 placeholder="https://github.com/github/docs/", max_chars=2048)

    with page.spinner("Parsing documentation file..."):
        write_contributing_analysis(page, repository_url)

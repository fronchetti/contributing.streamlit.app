#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import pandas
import streamlit as st

@st.cache
def get_reasons_for_exclusion():
    return pandas.read_csv('https://github.com/fronchetti/contributing.info/blob/main/resources/reasons_for_exclusion.csv?raw=true')

def write_motivation_section(page):
    page.markdown("To train a classification model capable of identifying information relevant for newcomers in CONTRIBUTING.md files, a set of projects were selected from GitHub to compose our dataset. The most popular projects from the top ten most popular languages on GitHub were selected to compose our sample. The list of programming languages included: JavaScript, Python, Java, PHP, C#, C++, TypeScript, Shell, C and Ruby.")
    page.markdown("The first evidence that not all open source projects actually support newcomers with CONTRIBUTING.md files was found during the extraction of these documentation files from GitHub. Researchers noticed that from the 9.514 projects selected for study, only 2.915 projects had a valid CONTRIBUTING.md file in their repository, about 30\% of the original dataset. Check out Table 1 for a complete overview of the selected projects.")
    page.markdown("**Table 1. Set of projects extracted from GitHub**")

    reasons_for_exclusion = copy.deepcopy(get_reasons_for_exclusion())
    page.dataframe(reasons_for_exclusion, use_container_width=True)

    page.markdown("After extracting the CONTRIBUTING.md files from the remaining 2.915 projects, researchers performed a qualitative analysis on the documentation files of 500 projects using the six categories of information known to be important for newcomers. A total of 20.733 paragraphs extracted from these projects were coded by the researchers, with 13.272 of them (64\%) being identified as part of one of the six categories of information. From the qualitative analysis, researchers found out that:")
    page.markdown("* **Most projects do not cover the six categories of information in their CONTRIBUTING.md files**")

    col1, col2, col3 = page.columns(3)
    col1.markdown('<p class="custom-percentage">74% of the files discuss two to four categories of information</p>', unsafe_allow_html=True)
    col2.markdown('<p class="custom-percentage">16% of the files present only one category of information</p>', unsafe_allow_html=True)
    col3.markdown('<p class="custom-percentage">And only 10% of the files included more than five categories</p>', unsafe_allow_html=True)
    page.markdown("* **Most CONTRIBUTING.md files are focused on the final stages of the contribution process**")

    col1, col2, col3 = page.columns(3)
    col1.markdown('<p class="custom-percentage">79% of the files discuss how newcomers should submit their changes</p>', unsafe_allow_html=True)
    col2.markdown('<p class="custom-percentage">Only 23% of the files explain how outsiders can choose a task to contribute</p>', unsafe_allow_html=True)
    col3.markdown('<p class="custom-percentage">Only one paragraph per file explains how newcomers can contact the community</p>', unsafe_allow_html=True)
    page.markdown("Based on these findings, the researchers implemented a classification model using the data obtained from the qualitative analysis. This model was implemented to investigate a bigger sample of projects without the need of a manual annotation of CONTRIBUTING.md files, and also to build a tool capable of reporting the coverage of such files to project maintainers. Our future goal is to support maintainers on the implementation of better CONTRIBUTING.md files, and newcomers on finding essential information.")
    page.markdown("🎯 Click on the classifier tab available on the navigation bar to try out our tool!")

    page.markdown("For more detailed information about our study and the classifier, please read our paper:")
    page.markdown('<p class="custom-container">(unavailable due double-blind review policy)<p>', unsafe_allow_html=True)
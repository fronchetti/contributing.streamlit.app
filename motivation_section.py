#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas 

def write_motivation_section(page):
    page.markdown("To train a classification model capable of identifying information relevant for newcomers in CONTRIBUTING.md files, a set of projects were selected from GitHub to compose our dataset. The most popular projects from the top ten most popular languages on GitHub were selected to compose our sample. The list of programming languages included: JavaScript, Python, Java, PHP, C#, C++, TypeScript, Shell, C and Ruby.")
    page.markdown("The first evidence that not all open source projects actually support newcomers with CONTRIBUTING.md files was found during the extraction of these documentation files from GitHub. Researchers noticed that from the 9.514 projects selected for study, only 2.915 projects had a valid CONTRIBUTING.md file in their repository, about 30\% of the original dataset. Check out the table below for a complete overview of the selected projects:")
    page.markdown("**Table 1. Set of projects extracted from GitHub**")
    reasons_for_exclusion = pandas.read_csv('reasons_for_exclusion.csv')
    page.dataframe(reasons_for_exclusion, use_container_width=True)
    page.markdown("After extracting the CONTRIBUTING.md files from the remaining 2.915 projects, researchers performed a qualitative analysis on the documentation files of 500 projects using the six categories of information known to be important for newcomers. A total of 20.733 paragraphs extracted from these projects were coded by the researchers, with 13.272 of them (64\%) being identified as part of one of the six categories of information. From the qualitative analysis, researchers found out that:")
    page.markdown("* **Most projects do not cover the six categories of information in their CONTRIBUTING.md files**")
    col1, col2, col3 = page.columns(3)
    col1.markdown('<p class="custom-percentage">74% of the files discuss two to four categories of information</p>', unsafe_allow_html=True)
    col2.markdown('<p class="custom-percentage">16% of the files presents only one category of information</p>', unsafe_allow_html=True)
    col3.markdown('<p class="custom-percentage">And only 10% of the files includes more than five categories</p>', unsafe_allow_html=True)
    page.markdown("* **Most CONTRIBUTING.md files are focused on the final stages of the contribution process**")
    col1, col2, col3 = page.columns(3)
    col1.markdown('<p class="custom-percentage">79% of the files discuss how newcomers should submit their changes</p>', unsafe_allow_html=True)
    col2.markdown('<p class="custom-percentage">Only 23% of the files explains how outsiders can choose a task to contribute</p>', unsafe_allow_html=True)
    col3.markdown('<p class="custom-percentage">Only one paragraph per file explains how newcomers can contact the community</p>', unsafe_allow_html=True)
    page.markdown("Based on these findings, the researchers implemented a classification model using the data obtained from the qualitative analysis. This model was implemented to investigate a bigger sample of projects without the need of a manual annotation of CONTRIBUTING.md files, and also to built a tool capable of reporting the quality of such files to project maintainers. Our future goal is to support maintainers on the implementation of better documentation files, and newcomers on finding essential information.")
    page.markdown("🎯 Click on the classifier tab available on the navigation bar to try out our tool!")
    page.markdown("For more detailed information about this study, feel free to read our paper:")
    page.markdown('<p class="custom-container">(unavailable due double-blind review policy)<p>', unsafe_allow_html=True)
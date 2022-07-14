#!/usr/bin/env python
# -*- coding: utf-8 -*-

def write_about_section(page):
    with page.expander("About this website"):
        page.markdown("The retention of newcomers is essential for the longevity\
                       of open source projects. To better receive new contributors,\
                       open source projects usually provide CONTRIBUTING  files\
                       as a primary source of documentation for outsiders.")

        page.markdown("Our goal with this website is to promote better documentation\
                      files for newcomers in open source projects. We offer a tool\
                      that project maintainers can use to evaluate the quality of\
                      their CONTRIBUTING files. A classification model analyses\
                      six categories of information known to be relevant for\
                      newcomers in the documentation files provided as input.\
                      From the identification of these categories, our website\
                      suggests for project maintainers how they can improve their\
                      documentation by knowning what is missing in their files.")

        page.markdown("We highlight the categories of information analysed below:")
        
        page.markdown("* **Contribution Flow**: Defines the set of steps that a\
                     newcomer needs to follow in order to make a contribution to\
                     the project. This category should appear as, for example, an\
                     ordered list of steps to follow or as a set of paragraphs\
                     describing the current workflow of the project.")

        page.markdown("* **Choose a task**: Specifies the set of information\
                     that describes how new contributors can find a task to\
                     contribute with the project. It may also contain descriptions\
                     of different types of tasks designed for newcomers and\
                     guidelines on how to perform a new contribution.")

        page.markdown("* **Talk to the community**: Comprehends information\
                     on  how a newcomer can get in touch with the community\
                     members. This category is related to, for example, links\
                     for communication channels, communication etiquettes,\
                     community guidelines and tutorials on how to start a\
                     conversation.")

        page.markdown("* **Build local workspace**: Determines the steps that a\
                     newcomer needs to follow in order to build the prerequirements\
                     of the local workspace. It may include setup instructions such\
                     as bash commands and modifications on computer settings.")

        page.markdown("* **Deal with the code**: Includes information describing\
                     how newcomers should deal with the source code. This category\
                     may contain, in particular, code conventions, descriptions\
                     of the source code and guidelines on how to write code\
                     for the project.")

        page.markdown("* **Submit the changes**: Represents information about\
                     how newcomers should submit a contribution back to the project.\
                     Besides the information about the submission process, it may\
                     also include information about platforms and tools used during\
                     the submission and software testing tutorials.")

        page.markdown("For more information, please visit our repository.")
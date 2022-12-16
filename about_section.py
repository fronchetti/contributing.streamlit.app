#!/usr/bin/env python
# -*- coding: utf-8 -*-

def write_about_section(page):

    page.markdown("Retaining new contributors is essential for the longevity\
                    of open-source projects. To better receive newcomers,\
                    open source projects tend to provide [CONTRIBUTING.md](https://mozillascience.github.io/working-open-workshop/contributing/) files\
                    in their repositories, a type of documentation file considered as a primary source of documentation for outsiders. Although these files\
                    may be essential for new contributors, related studies have shown that not all projects\
                    provide the necessary information about the contribution process in their CONTRIBUTING.md files.")

    page.markdown("This website offers a machine learning classifier that maintainers can\
                   use to evaluate the quality of\
                   CONTRIBUTING.md files.  Our model looks for\
                    six categories of information relevant for\
                    newcomers in the documentation files of projects provided as input.\
                    From the identification of these categories, our website\
                    suggests to maintainers how they can improve their\
                    CONTRIBUTING.md files and highlights the categories identified in their paragraphs.")

    page.markdown("🎯 Click on the classifier tab available on the navigation bar to try out our tool!")

    page.markdown('<p class="custom-page-title">Categories of information</p>', unsafe_allow_html=True)
    page.markdown("The six categories of information analysed by our classifier are:")
    
    page.markdown("* **Contribution Flow**: Defines the set of steps that a\
                    newcomer needs to follow in order to make a contribution to\
                    the project. This category should appear as, for example, an\
                    ordered list of steps to follow or as a set of paragraphs\
                    describing the current workflow of the project.")

    page.markdown('<p class="custom-container">Example of <b>Contribution Flow</b> from <a href="https://github.com/alibaba/sentinel">Sentinel</a>:<br>\
                "<i>Here are the workflow for contributors:<br>\
                1.  Fork to your own<br>\
                2.  Clone fork to local repository<br>\
                3.  Create a new branch and work on it<br>\
                4.  Keep your branch in sync<br>\
                5.  Commit your changes (make sure your commit message concise)<br>\
                6.  Push your commits to your forked repository<br>\
                7.  Create a pull request</i>"\
                </p>', unsafe_allow_html=True)

    page.markdown("* **Choose a task**: Specifies the set of information\
                    that describes how new contributors can find a task to\
                    contribute with the project. It may also contain descriptions\
                    of different types of tasks designed for newcomers and\
                    guidelines on how to perform a new contribution.")

    page.markdown('<p class="custom-container">Example of <b>Choose a task</b> from <a href="https://github.com/ampproject/amphtml">Amp</a>:<br>\
            "<i>The community has created a list of Good First Issues specifically<br>\
             for new contributors to the project. Feel free to find one of the unclaimed<br>\
             Good First Issues that interests you, claim it by adding a comment to it and jump in!</i>"</p>', unsafe_allow_html=True)

    page.markdown("* **Talk to the community**: Comprehends information\
                    on  how a newcomer can get in touch with the community\
                    members. This category is related to, for example, links\
                    for communication channels, communication etiquettes,\
                    community guidelines and tutorials on how to start a\
                    conversation.")

    page.markdown('<p class="custom-container">Example of <b>Talk to the community</b> from <a href="https://github.com/darktable-org/darktable">Darktable</a>:<br>\
            "<i>Before you spend a lot of time working on a new feature, it is always best to<br>\
            discuss your proposed changes with us first.  The best place to do that is in<br>\
            our IRC channel on irc.freenode.net, channel #darktable or the<br>\
            development mailing list, see here for more information.  This will dramatically<br>\
            improve your chances of having your code merged, especially if we think you will<br>\
            hang around to maintain it."</i></p>', unsafe_allow_html=True)

    page.markdown("* **Build local workspace**: Determines the steps that a\
                    newcomer needs to follow in order to build the prerequirements\
                    of the local workspace. It may include setup instructions such\
                    as bash commands and modifications on computer settings.")

    page.markdown('<p class="custom-container">Example of <b>Build local workspace</b> from <a href="https://github.com/azkaban/azkaban">Azkaban</a>:<br>\
                <i>"We recommend IntelliJ IDEA. There is a free community edition available.<br>\
                Azkaban is a standard Gradle project. You can import it into your IDE using<br>\
                the build.gradle file in the root directory. For IntelliJ, choose Open Project<br>\
                from the Quick Start box or choose Open from the File menu and select the root<br>\
                build.gradle file."</i></p>', unsafe_allow_html=True)

    page.markdown("* **Deal with the code**: Includes information describing\
                    how newcomers should deal with the source code. This category\
                    may contain, in particular, code conventions, descriptions\
                    of the source code and guidelines on how to write code\
                    for the project.")

    page.markdown('<p class="custom-container">Example of <b>Deal with the code</b> from <a href="https://github.com/cuberite/cuberite">Cuberite</a>:<br>\
                <i>"When contributing, you must follow our code conventions. Otherwise,<br>\
                    CI builds will automatically fail and your PR will not be merged until<br>\
                    the non-conforming code is fixed. Due to this, we strongly advise you to<br>\
                    run src/CheckBasicStyle.lua before committing, it will perform various code<br>\
                    style checks and warn you if your code does not conform to our conventions."</i></p>', unsafe_allow_html=True)

    page.markdown("* **Submit the changes**: Represents information about\
                    how newcomers should submit a contribution back to the project.\
                    Besides the information about the submission process, it may\
                    also include information about platforms and tools used during\
                    the submission and software testing tutorials.")
    
    page.markdown('<p class="custom-container">Example of <b>Submit the changes</b> from <a href="https://github.com/balenalabs/balena-sound">Balena Sound</a>:<br>\
            <i>"Pull requests are the only way of pushing your code to the master branch.<br>\
                When creating a PR make sure you choose a short but sensical PR title and add<br>\
                a few lines describing your contribution."</i></p>', unsafe_allow_html=True)

    page.markdown('<p class="custom-page-title">Learn more</p>', unsafe_allow_html=True)

    page.markdown("For more information about the implementation of our classifier, please read our paper:")
    page.markdown('<p class="custom-container">(unavailable due double-blind review policy)<p>', unsafe_allow_html=True)
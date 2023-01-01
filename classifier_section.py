#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas
import collections
import streamlit as st
import plotly.express as plotly
from annotated_text import annotated_text
from scripts.classify_content import get_contributing_predictions

@st.cache(allow_output_mutation=True)
def get_projects():
    return pandas.read_csv('https://github.com/fronchetti/contributing.info/blob/main/resources/projects.csv?raw=true', encoding='cp1252')


def write_contributing_analysis(page, repository_url):
    paragraphs, predictions = get_contributing_predictions(page, repository_url)

    if len(paragraphs) > 0 and len(predictions) > 0:
        predictions_per_class = count_predictions_per_class(predictions, repository_url)
        write_overview_reasoning(page, predictions_per_class)
        write_dominant_categories(page, predictions_per_class)
        write_missing_categories(page, predictions_per_class)
        write_project_comparison(page, predictions_per_class)
        write_annotated_paragraphs(page, paragraphs, predictions)


def write_overview_reasoning(page, predictions):
    page.write("<hr>", unsafe_allow_html=True)
    page.markdown('<p class="custom-page-title">How covered is this CONTRIBUTING.md file?</p>', unsafe_allow_html=True)

    # Ignore the class "No categories identified" while defining the coverage of a CONTRIBUTING.md file
    categories_predictions = predictions[predictions['Category'] != 'No categories identified.']

    n_existent_categories = (categories_predictions['Number of paragraphs'] > 0).sum()
    total_categories = categories_predictions['Number of paragraphs'].count()
    percentage_existent_categories = n_existent_categories / total_categories * 100

    if percentage_existent_categories == 100:
        contributing_coverage = 'Excellent'
    elif percentage_existent_categories > 83:
        contributing_coverage = 'Very Good'
    elif percentage_existent_categories > 66:
        contributing_coverage = 'Good'
    elif percentage_existent_categories > 50:
        contributing_coverage = 'Regular'
    elif percentage_existent_categories > 33:
        contributing_coverage = 'Poor'
    elif percentage_existent_categories > 0:
        contributing_coverage = 'Very Poor'
    else:
        contributing_coverage = 'Undefined'

    page.markdown("According to our classification model,\
                the coverage of this CONTRIBUTING.md file is **{}**.".format(contributing_coverage))

    write_overview_barplot(page, predictions)

    coverage_reasonings = {
        'Excellent': 'It means the requested documentation file covered all the\
            six categories of information a newcomer needs to know\
            in order to contribute to an open source project. \
            For a more detailed explanation, please read the analysis below.',
        'Very Good': 'It means five out of six categories of\
            information known to be relevant to newcomers were identified in this documentation file.\
            To make the file more receptive to new contributors, maintainers need to make sure\
            that the CONTRIBUTING.md covers all the six categories of information.\
            A detailed analysis about this file is provided below.',
        'Good': 'It means that four out of six categories of information known to\
            be relevant for newcomers were identified in this CONTRIBUTING.md file.\
            We believe that a few changes could make it even better. Please, take a\
            look at the detailed analysis below.',
        'Regular': 'Only half of the categories of information known to be relevant\
            to newcomers were identified in this CONTRIBUTING.md file. To guarantee a\
            better retention of new contributors, the documentation file\
            must cover all the six categories of information. Please, take a look\
            at the detailed analysis below.',
        'Poor': 'Unfortunately, only two out of six categories of information known to be\
            relevant to newcomers in open source projects were identified in this CONTRIBUTING.md file.\
            To make sure this is not a misunderstanding from the classification model, please take a look\
            at the explanation below.',
        'Very Poor': "Less than two categories of information known to be relevant\
            to newcomers were identified in this CONTRIBUTING.md file. To make sure\
            that this is not a problem with the classification, please read the\
            review below.",
        'Undefined': "It means that none of the categories of information known\
            to be relevant to newcomers were identified in this documentation file.\
            Please, confirm that this is not a misundertanding by checking if URL provided is\
            correct and if the CONTRIBUTING.md file available in the repository is not empty."
    }

    page.markdown("{}".format(coverage_reasonings[contributing_coverage]))

def write_overview_barplot(page, predictions):
    barplot = plotly.bar(data_frame = predictions,
                     x = "Number of paragraphs", 
                     y = "Repository",
                     color = "Category",
                     color_discrete_map = classes_color,
                     orientation = "h",
                     height = 250,
                     template = 'ggplot2')

    barplot.update_layout(yaxis = {'visible': False,
                                   'showticklabels': False},
                          legend={'title_text': None,
                                  'orientation': 'h',
                                  'yanchor': 'top',
                                  'xanchor': 'center',
                                  'y': 2.25,
                                  'x': 0.5},
                          margin={'l': 50,
                                  'r': 50,
                                  't': 80,
                                  'b': 80},
                          paper_bgcolor='rgb(252, 252, 252)')

    # Hide legend for categories where number of paragraphs is zero
    for trace in barplot['data']:
        n_paragraphs_in_class = predictions.loc[predictions['Category'] == trace['name'], 'Number of paragraphs'].item()

        if  n_paragraphs_in_class == 0:
            trace['showlegend'] = False

    page.plotly_chart(barplot, use_container_width = True)

def check_plural(phrase, n_paragraphs):
    if int(n_paragraphs) == 0:
        return phrase.replace('0 paragraphs (0%) discuss', 'No paragraphs discusses')
    if int(n_paragraphs) == 1:
        return phrase.replace('1 paragraphs', '1 paragraph').replace('discuss', 'discusses')
    else:
        return phrase

def write_dominant_categories(page, predictions):

    dominant_reasonings = {
        'CF – Contribution flow': "**Contribution flow:** Describing the flow\
            for new contributions in an OSS project is a great way to highlight the\
            necessary steps newcomers need to take in order to place their first\
            contribution. Having the contribution flow in the dominant categories\
            means that the CONTRIBUTING.md file is probably covering the basics steps of the project.\
            However, maintainers need to keep in mind that more specific topics should also be\
            discussed in the documentation file (e.g. How to choose a task).",
        'CT – Choose a task': "**Choose a task:** It is almost impossible for a\
            newcomer to contribute to an OSS project without knowing what tasks are\
            available for external contributors. Having this as a dominant category\
            means that the CONTRIBUTING.md file is probably showing to novices what they can do in\
            the project. However, it is important ot highlight that describing other aspects\
            of the project is also important for them (e.g. How to talk with the community).",
        'TC – Talk to the community': "**Talk to the community:** Building a solid\
            community is a primary goal for most projects in the open source context.\
            Having this as a dominant category means that the CONTRIBUTING.md file is telling\
            newcomers how they can find, interact and behave in their community.",
        'BW – Build local workspace': "**Build local workspace:** Contributors\
            usually depend of their own local workspace to implement a contribution.\
            If this category is dominant, it means that the CONTRIBUTING.md file is describing\
            for newcomers how they should install the respective project on their own machines.\
            Although this is an important topic for newcomers to know, other aspects should also be\
            addressed by the project (e.g. How to dealt with the code).",
        'DC – Deal with the code': "**Deal with the code:** Each open source project has its\
            own standards and traditions. It is important for open source\
            projects to describe for newcomers how they should implement their code\
            before they place their first contribution. Having this category among the\
            dominant categories means that the CONTRIBUTING.md file highlights the guidelines to implement code\
            in the respective project.",
        'SC – Submit the changes': "**Submit the changes:** A contribution would\
            not be complete without the submission of changes back to the\
            repository. If this category is dominant in the CONTRIBUTING.md\
            file, it means that maintainers are probably describing how newcomers should\
            submit their contributions. However, maintainers should keep in mind that prior steps\
            in the contribution process should also be addressed by the\
            contributing file (e.g. How to deal with the code)."}

    # Ignore the class "No categories identified"
    predictions = predictions[predictions['Category'] != 'No categories identified.']

    dominant_categories = predictions.loc[predictions.Percentage >= 10]
    dominant_categories = dominant_categories.sort_values('Percentage', ascending = False)
    n_dominant_categories = len(dominant_categories.index)

    if n_dominant_categories > 0:
        page.write("<hr>", unsafe_allow_html=True)
        page.markdown('<p class="custom-page-title">Dominant categories</p>', unsafe_allow_html=True)
        page.markdown("The prevalent categories of information in this CONTRIBUTING.md file are:")
        
        if 2 > n_dominant_categories > 0:
            category = dominant_categories['Category'].iloc[0]
            category_paragraphs = str(int(dominant_categories['Number of paragraphs'].iloc[0]))
            category_percentage = str(dominant_categories['Percentage'].iloc[0]) + '%'

            page.markdown('- ' + dominant_reasonings[category])
            page.markdown(check_plural('<p class="container-dominant">' + category_paragraphs + ' paragraphs (' + category_percentage + ') discuss the category ' + category + ' </p>', category_paragraphs), unsafe_allow_html=True)

        elif 3 > n_dominant_categories > 1:
            category_a = dominant_categories['Category'].iloc[0]
            category_b = dominant_categories['Category'].iloc[1]
            category_a_paragraphs = str(int(dominant_categories['Number of paragraphs'].iloc[0]))
            category_b_paragraphs = str(int(dominant_categories['Number of paragraphs'].iloc[1]))
            category_a_percentage = str(dominant_categories['Percentage'].iloc[0]) + '%'
            category_b_percentage = str(dominant_categories['Percentage'].iloc[1]) + '%'

            page.markdown('- ' + dominant_reasonings[category_a])
            page.markdown(check_plural('<p class="container-dominant">' + category_a_paragraphs + ' paragraphs (' + category_a_percentage + ') discuss the category ' + category_a + ' </p>', category_a_paragraphs), unsafe_allow_html=True)

            page.markdown('- ' + dominant_reasonings[category_b])
            page.markdown(check_plural('<p class="container-dominant">' + category_b_paragraphs + ' paragraphs (' + category_b_percentage + ') discuss the category ' + category_b + ' </p>', category_b_paragraphs), unsafe_allow_html=True)

        elif n_dominant_categories > 2:
            category_a = dominant_categories['Category'].iloc[0]
            category_b = dominant_categories['Category'].iloc[1]
            category_c = dominant_categories['Category'].iloc[2]
            category_a_paragraphs = str(int(dominant_categories['Number of paragraphs'].iloc[0]))
            category_b_paragraphs = str(int(dominant_categories['Number of paragraphs'].iloc[1]))
            category_c_paragraphs = str(int(dominant_categories['Number of paragraphs'].iloc[2]))
            category_a_percentage = str(dominant_categories['Percentage'].iloc[0]) + '%'
            category_b_percentage = str(dominant_categories['Percentage'].iloc[1]) + '%'
            category_c_percentage = str(dominant_categories['Percentage'].iloc[2]) + '%'

            page.markdown('- ' + dominant_reasonings[category_a])
            page.markdown(check_plural('<p class="container-dominant">' + category_a_paragraphs + ' paragraphs (' + category_a_percentage + ') discuss the category ' + category_a + ' </p>', category_a_paragraphs), unsafe_allow_html=True)

            page.markdown('- ' + dominant_reasonings[category_b])
            page.markdown(check_plural('<p class="container-dominant">' + category_b_paragraphs + ' paragraphs (' + category_b_percentage + ') discuss the category ' + category_b + ' </p>', category_b_paragraphs), unsafe_allow_html=True)

            page.markdown('- ' + dominant_reasonings[category_c])
            page.markdown(check_plural('<p class="container-dominant">' + category_c_paragraphs + ' paragraphs (' + category_c_percentage + ') discuss the category ' + category_c + ' </p>', category_c_paragraphs), unsafe_allow_html=True)

def write_missing_categories(page, predictions):

    missing_reasonings = {
        'CF – Contribution flow': "**Contribution flow:** When joining an open-source project, new\
             contributors need to know the basic steps they need to follow to place their first contribution,\
             from downloading the source code to submitting their contribution back to the project.\
             A CONTRIBUTING.md file needs to highlight step-by-step what path newcomers must follow\
             to get their first contribution accepted. An easy way for maintainers to do it is by\
             creating an ordered list of steps.",
        'CT – Choose a task': "**Choose a task:** Newcomers need to know what\
            tasks they can work on and where they can find them. A CONTRIBUTING.md file\
            must provide instructions about where new contributors can find tasks to work on.\
            An easy way to prepare a project to receive outside contributions is by labeling tasks that\
            anyone could implement (See https://up-for-grabs.net/).",
        'TC – Talk to the community': "**Talk to the community:** Newcomers\
            usually need assistance from the community while placing their\
            first contribution. A CONTRIBUTING.md file must specify\
            how they can connect with the community and, more specifically, with project maintainers.\
            Community guidelines and etiquettes are also welcomed in this category (See https://docs.github.com/en/communities).",
        'BW – Build local workspace': "**Build local workspace:** It might be\
            impossible for new code contributors to work on a project without\
            building their own workspace first. A CONTRIBUTING.md file\
            must provide information on how newcomers can install the dependencies\
            of the project. Maintainers need to make sure it covers all the technical aspects\
            of the project while writing about this category, including hardware and software limitations (e.g. portability issues).",
        'DC – Deal with the code': "**Deal with the code:** If maintainers don't provide\
            information about how newcomers should deal with the source code\
            of the project, they might use their own style to implement their first\
            contribution. This independence might delay the contribution process,\
            requiring more effort from newcomers and project maintainers. A CONTRIBUTING.md file\
            must clearly specify how newcomers should deal with the source code before\
            placing a contribution back to the repository.",
        'SC – Submit the changes': "**Submit the changes:** A contribution would\
            not be complete without the submission of changes back to the\
            project. If this category is missing in the CONTRIBUTING.md\
            file, it means that maintainers may not be describing how newcomers\
            should submit their modifications back to the project. The CONTRIBUTING.md file\
            must provide information about the submission process, including information\
            about continuous integration tools, version control systems and tests."}

    # Ignore the class "No categories identified"
    predictions = predictions[predictions['Category'] != 'No categories identified.']

    missing_categories = predictions.loc[predictions.Percentage < 10]
    missing_categories = missing_categories.sort_values('Percentage')
    n_missing_categories = len(missing_categories.index)
    
    if n_missing_categories > 0:
        page.write("<hr>", unsafe_allow_html=True)
        page.markdown('<p class="custom-page-title">Missing categories</p>', unsafe_allow_html=True)
        page.markdown("The categories of information missing in this CONTRIBUTING.md file are:")
        
        if 2 > n_missing_categories > 0:
            category = missing_categories['Category'].iloc[0]
            category_paragraphs = str(int(missing_categories['Number of paragraphs'].iloc[0]))
            category_percentage = str(missing_categories['Percentage'].iloc[0]) + '%'

            page.markdown('- ' + missing_reasonings[category])
            page.markdown(check_plural('<p class="container-missing">' + category_paragraphs + ' paragraphs (' + category_percentage + ') discuss the category ' + category + ' </p>', category_paragraphs), unsafe_allow_html=True)

        elif 3 > n_missing_categories > 1:
            category_a = missing_categories['Category'].iloc[0]
            category_b = missing_categories['Category'].iloc[1]
            category_a_paragraphs = str(int(missing_categories['Number of paragraphs'].iloc[0]))
            category_b_paragraphs = str(int(missing_categories['Number of paragraphs'].iloc[1]))
            category_a_percentage = str(missing_categories['Percentage'].iloc[0]) + '%'
            category_b_percentage = str(missing_categories['Percentage'].iloc[1]) + '%'

            page.markdown('- ' + missing_reasonings[category_a])
            page.markdown(check_plural('<p class="container-missing">' + category_a_paragraphs + ' paragraphs (' + category_a_percentage + ') discuss the category ' + category_a + ' </p>', category_a_paragraphs), unsafe_allow_html=True)

            page.markdown('- ' + missing_reasonings[category_b])
            page.markdown(check_plural('<p class="container-missing">' + category_b_paragraphs + ' paragraphs (' + category_b_percentage + ') discuss the category ' + category_b + ' </p>', category_b_paragraphs), unsafe_allow_html=True)

        elif n_missing_categories > 2:
            category_a = missing_categories['Category'].iloc[0]
            category_b = missing_categories['Category'].iloc[1]
            category_c = missing_categories['Category'].iloc[2]
            category_a_paragraphs = str(int(missing_categories['Number of paragraphs'].iloc[0]))
            category_b_paragraphs = str(int(missing_categories['Number of paragraphs'].iloc[1]))
            category_c_paragraphs = str(int(missing_categories['Number of paragraphs'].iloc[2]))
            category_a_percentage = str(missing_categories['Percentage'].iloc[0]) + '%'
            category_b_percentage = str(missing_categories['Percentage'].iloc[1]) + '%'
            category_c_percentage = str(missing_categories['Percentage'].iloc[2]) + '%'

            page.markdown('- ' + missing_reasonings[category_a])
            page.markdown(check_plural('<p class="container-missing">' + category_a_paragraphs + ' paragraphs (' + category_a_percentage + ') discuss the category ' + category_a + ' </p>', category_a_paragraphs), unsafe_allow_html=True)

            page.markdown('- ' + missing_reasonings[category_b])
            page.markdown(check_plural('<p class="container-missing">' + category_b_paragraphs + ' paragraphs (' + category_b_percentage + ') discuss the category ' + category_b + ' </p>', category_b_paragraphs), unsafe_allow_html=True)

            page.markdown('- ' + missing_reasonings[category_c])
            page.markdown(check_plural('<p class="container-missing">' + category_c_paragraphs + ' paragraphs (' + category_c_percentage + ') discuss the category ' + category_c + ' </p>', category_c_paragraphs), unsafe_allow_html=True)
    
            if n_missing_categories > 3:
                page.markdown('<p class="container-warning"> Although just three categories of information are highlighted\
                    in this section, we identified that this CONTRIBUTING.md file has other\
                    {} categories that should be adjusted.</p>'.format(n_missing_categories - 3), unsafe_allow_html=True)


def write_project_comparison(page, predictions):
    page.write("<hr>", unsafe_allow_html=True)
    page.markdown('<p class="custom-page-title">This file compared to other projects:</p>', unsafe_allow_html=True)

    projects_dataframe = get_projects()

    selected_category = page.selectbox('Choose a category of information:', tuple(classes_color.keys()))

    sorted_dataframe = projects_dataframe.sample(frac=0.01)
    sorted_dataframe = sorted_dataframe.sort_values(by=[selected_category], ascending=True)
    # Include an empty value to isolate the project from the rest
    empty_row = {'Repository': '', selected_category: 0}
    sorted_dataframe = sorted_dataframe.append(empty_row, ignore_index=True)

    # Get values from project
    project_name = (predictions['Repository'].iloc[0]).replace('github.com/', '')
    project_value = predictions.loc[predictions['Category'] == selected_category, 'Number of paragraphs'].iloc[0]
    project_row = {'Repository': project_name, selected_category: project_value}
    sorted_dataframe = sorted_dataframe.append(project_row, ignore_index=True)

    barplot = plotly.bar(sorted_dataframe, x = 'Repository', y = selected_category, color=selected_category, template = 'ggplot2')
    barplot.update_layout(paper_bgcolor='rgb(245, 245, 245)', showlegend=False, yaxis_title='# Paragraphs', font_color='black')
    barplot.update_coloraxes(showscale=False)
    barplot.update_xaxes(tickangle=45)
    page.markdown('This file has ' + str(int(project_value)) + ' paragraphs in the category ' + selected_category + '. The average of the following sample for this category is ' + str(int(sorted_dataframe[selected_category].mean())) + '.')
    page.plotly_chart(barplot, use_container_width = True)


def write_annotated_paragraphs(page, paragraphs, predictions):
    with page.expander("Open document with predictions"):
        for paragraph, prediction in zip(paragraphs, predictions):
            if prediction == 'No categories identified.':
                page.write(paragraph)
            if prediction.startswith('CT'):
                annotated_text((paragraph, prediction, classes_color[prediction]))
            if prediction.startswith('CF'):
                annotated_text((paragraph, prediction, classes_color[prediction]))
            if prediction.startswith('TC'):
                annotated_text((paragraph, prediction, classes_color[prediction]))
            if prediction.startswith('BW'):
                annotated_text((paragraph, prediction, classes_color[prediction]))
            if prediction.startswith('DC'):
                annotated_text((paragraph, prediction, classes_color[prediction]))
            if prediction.startswith('SC'):
                annotated_text((paragraph, prediction, classes_color[prediction]))


def count_predictions_per_class(predictions, repository_url):
    counter = collections.Counter(predictions)

    dataframe = pandas.DataFrame.from_dict(counter,
                                           orient='index',
                                           columns=['Number of paragraphs'])

    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns = {"index": "Category"})
    dataframe['Repository'] = repository_url

    # Assign color to each category
    for category in classes_color.keys():
        if category not in dataframe['Category'].values:
            dataframe.loc[len(dataframe.index),
             ['Category', 'Number of paragraphs', 'Repository', 'Color']] = [category, 0, repository_url, classes_color[category]]
        else:
            dataframe.loc[dataframe['Category'] == category, ['Color']] = classes_color[category]

    # Calculate percentage per category
    if dataframe['Number of paragraphs'].sum() > 0:
        dataframe['Percentage'] = (dataframe['Number of paragraphs'] / dataframe['Number of paragraphs'].sum()) * 100
    else:
        dataframe['Percentage'] = 0

    dataframe['Percentage'] = dataframe['Percentage'].astype(int)

    return dataframe

classes_color = {'No categories identified.': "#264653",
    'CF – Contribution flow': "#287271",
    'CT – Choose a task': "#2a9d8f",
    'TC – Talk to the community': "#8ab17d",
    'BW – Build local workspace': "#e9c46a",
    'DC – Deal with the code': "#f4a261",
    'SC – Submit the changes': "#e76f51"}

percentage = lambda part, whole: int(part / whole * 100)
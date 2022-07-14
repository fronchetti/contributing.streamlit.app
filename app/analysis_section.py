#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas
import collections
import plotly.express as plotly
from annotated_text import annotated_text
from classifier.classify_content import get_contributing_predictions

classes_color = {'No categories identified.': "#577590",
    'CF – Contribution flow': "#f94144",
    'CT – Choose a task': "#f3722c",
    'TC – Talk to the community': "#f8961e",
    'BW – Build local workspace': "#f9c74f",
    'DC – Deal with the code': "#90be6d",
    'SC – Submit the changes': "#43aa8b"}

percentage = lambda part, whole: int(part / whole * 100)

def write_contributing_analysis(page, repository_url):
    paragraphs, predictions = get_contributing_predictions(page, repository_url)

    if len(paragraphs) > 0 and len(predictions) > 0:
        predictions_per_class = count_predictions_per_class(predictions, repository_url)
        write_overview_barplot(page, predictions_per_class)
        write_overview_reasoning(page, predictions_per_class)
        write_dominant_categories(page, predictions_per_class)
        write_weak_categories(page, predictions_per_class)
        write_project_comparison(page, predictions_per_class, repository_url)
        write_annotated_paragraphs(page, paragraphs, predictions)

def write_project_comparison(page, predictions, repository_url):
    page.write("#### Your file compared to other projects")
    if not os.path.isfile('projects.csv'):
        projects_dataframe = pandas.DataFrame()

        try:
            projects = ['https://github.com/vuejs/vue',
                        'https://github.com/facebook/react',
                        'https://github.com/tensorflow/tensorflow',
                        'https://github.com/twbs/bootstrap',
                        'https://github.com/microsoft/vscode',
                        'https://github.com/golang/go',
                        'https://github.com/nodejs/node',
                        'https://github.com/angular/angular',
                        'https://github.com/pytorch/pytorch',
                        'https://github.com/juliaLang/julia',
                        'https://github.com/scala/scala',
                        'https://github.com/vim/vim',
                        'https://github.com/gohugoio/hugo',
                        'https://github.com/hashicorp/terraform',
                        'https://github.com/activeadmin/activeadmin',
                        'https://github.com/apache/incubator-superset',
                        'https://github.com/atlanhq/camelot',
                        'https://github.com/babel/babel',
                        'https://github.com/aws/aws-cdk',
                        'https://github.com/azkaban/azkaban',
                        'https://github.com/cookiecutter/cookiecutter',
                        'https://github.com/microsoft/typeScript']
            
            for project in projects:
                _, predictions = get_contributing_predictions(page, project)
                predictions_per_class = count_predictions_per_class(predictions, project)
                projects_dataframe = projects_dataframe.append(predictions_per_class)

            projects_dataframe.to_csv('projects.csv')
        except Exception as e:
            page.error("The parser did not generate data from other projects to compare with.\
                        Skipping the project comparison section.")
            return

    projects_dataframe = pandas.read_csv('projects.csv')

    if projects_dataframe['Repository'].str.contains(repository_url).any():
        projects_dataframe = projects_dataframe[~projects_dataframe.Repository.str.contains(repository_url)]

    projects_dataframe = projects_dataframe.append(predictions)
    projects_dataframe['Repository'] = projects_dataframe.Repository.str.replace('https://' , '')
    projects_dataframe['Repository'] = projects_dataframe.Repository.str.replace('github.com/' , '')

    category_selection = page.selectbox('Choose a category of information:',
        tuple(classes_color.keys() - ['No categories identified.']))

    category_dataframe = projects_dataframe.loc[projects_dataframe['Category'] == category_selection]
    category_dataframe = category_dataframe.sort_values(by = 'Number of paragraphs')
    category_dataframe['Average'] = int(category_dataframe['Number of paragraphs'].mean())

    repository_url = repository_url.replace('https://' , '').replace('github.com/' , '')
    colors = {repository_url: '#ed3326'}
    color_discrete_map = {c: colors.get(c, '#90be6d') for c in category_dataframe.Repository.unique()}

    barplot = plotly.bar(category_dataframe, x = 'Repository', y = 'Number of paragraphs', color='Repository', color_discrete_map=color_discrete_map, template = 'ggplot2')
    barplot.update_layout(paper_bgcolor='rgb(245, 245, 245)', showlegend=False)
    # line = plotly.line(category_dataframe, x = 'Repository', y = 'Average', hover_data={'Repository': False}, dash='dash')
    # line.update_traces(line_color="red")
    # barplot.add_traces(line.data)
    page.plotly_chart(barplot, use_container_width = True)

def write_overview_barplot(page, predictions):
    page.write("#### Overall analysis")

    barplot = plotly.bar(data_frame = predictions,
                     x = "Number of paragraphs", 
                     y = "Repository",
                     color = "Category",
                     color_discrete_map = classes_color,
                     orientation = "h",
                     height = 170,
                     template = 'ggplot2')

    barplot.update_layout(yaxis = {'visible': False,
                                   'showticklabels': False},
                          legend={'title_text': None,
                                  'orientation': 'h',
                                  'yanchor': 'top',
                                  'xanchor': 'center',
                                  'y': 1.75,
                                  'x': 0.5},
                          margin={'l': 20,
                                  'r': 20,
                                  't': 20,
                                  'b': 20},
                          paper_bgcolor='rgb(245, 245, 245)')

    # Hide legend for categories where number of paragraphs is zero
    for trace in barplot['data']:
        n_paragraphs_in_class = predictions.loc[predictions['Category'] == trace['name'],
                                'Number of paragraphs'].item()

        if  n_paragraphs_in_class == 0:
            trace['showlegend'] = False

    page.plotly_chart(barplot, use_container_width = True)

def write_overview_reasoning(page, predictions):
    # Ignore the class "No categories identified"
    predictions = predictions[predictions['Category'] != 'No categories identified.']

    n_existent_categories = (predictions['Number of paragraphs'] > 0).sum()
    total_categories = predictions['Number of paragraphs'].count()
    percentage_existent_categories = n_existent_categories / total_categories * 100

    if percentage_existent_categories == 100:
        contributing_quality = 'Excellent'
    elif percentage_existent_categories > 83:
        contributing_quality = 'Very Good'
    elif percentage_existent_categories > 66:
        contributing_quality = 'Good'
    elif percentage_existent_categories > 50:
        contributing_quality = 'Regular'
    elif percentage_existent_categories > 33:
        contributing_quality = 'Poor'
    elif percentage_existent_categories > 0:
        contributing_quality = 'Very Poor'
    else:
        contributing_quality = 'Undefined'

    quality_reasonings = {
        'Excellent': 'It means that your documentation file covered all the\
            categories of information a newcomer usually needs to known before\
            attempting to join in an open source project. \
            Please read our analysis below to make it even better.',
        'Very Good': 'It means we identified five out of six categories of\
            information known to be relevant for newcomers in your documentation.\
            To make your project more receptive for new contributors, make sure\
            that your document covers all the six categories of information.\
            We provide a more detailed analysis about your documentation file below.',
        'Good': 'It means that four out of six categories of information known to\
            be relevant for newcomers were identified in your documentation file.\
            We believe that we can help you make it even better. Please, take a\
            look at our detailed analysis below and modify your file when you\
            judge as necessary.',
        'Regular': 'Only half of the categories of information known to be relevant\
            for newcomers were identified in your documentation file. To guarantee a\
            better retention of new contributors, make sure your documentation file\
            is covering the six categories of information we describe below.\
            We known you make it better!',
        'Poor': 'Unfortunately, only two categories of information known to be\
            relevant for newcomers in open-source projects was identified.\
            To make sure this is not a classification misunderstanding, please\
            review the evaluation we describe below. Let\'s make your project\
            even more receptive!',
        'Very Poor': "Less than two categories of information known to be relevant\
            for newcomers were identified in your documentation file. To make sure\
            that this is not a problem with our prediction, please read the\
            review below and make changes to your file that you judge as\
            necessary. We hope you can make your project even better!",
        'Undefined': "It means that none of the categories of information known\
            to be relevant for newcomers were identified in your documentation file.\
            Please, confirm if the repository URL is correct and the CONTRIBUTING\
            file available is not empty."
    }

    page.markdown("According to our classification model,\
                  the quality of your CONTRIBUTING file is **{}**. {}".format(contributing_quality,
                  quality_reasonings[contributing_quality]))

def write_dominant_categories(page, predictions):

    dominant_reasonings = {
        'CF – Contribution flow': "**Contribution flow:** Describing the flow\
            for new contributions in your project is a great way to highlight the\
            necessary steps newcomers need to take in order to place their first\
            contribution. Having the contribution flow in your dominant categories\
            means that you are probably covering the basics steps of your project.\
            However, always keep in mind that more specific topics should also be\
            discussed in your documentation.",
        'CT – Choose a task': "**Choose a task:** It is almost impossible for a\
            newcomer to contribute to your project without knowing what tasks are\
            available for external contributors. Having this as a dominant category\
            means that you are probably showing novices what they can do in your\
            project. However, please don't forget that describing other the aspects\
            of your project is also important for them.",
        'TC – Talk to the community': "**Talk to the community:** Building a solid\
            community is a primary goal for most projects in the open source context.\
            Having this as a dominant category means that you are telling your\
            newcomers how they can find and contact you.",
        'BW – Build local workspace': "**Build local workspace:** Code contributions\
            usually depend of a local workspace used during the development process.\
            If this category is dominant, it means that you are probably describing\
            for newcomers how they should install your software on their own machines.",
        'DC – Deal with the code': "**Deal with the code:** Each project has its\
            own code standards and traditions. It is important that open source\
            projects describe for newcomers how they should deal with the code\
            during their first contribution. Having this category among your\
            dominants means that you care about the quality of the source code\
            in your project.",
        'SC – Submit the changes': "**Submit the changes:** A contribution would\
            not be complete without the submission of changes back to the open\
            source project. If this category is dominant in your documentation\
            file, it means that you are probably describing how newcomers should\
            submit their modifications. However, keep in mind that prior steps\
            in the contribution process should also be handled by your\
            contributing file."}

    # Ignore the class "No categories identified"
    predictions = predictions[predictions['Category'] != 'No categories identified.']

    dominant_categories = predictions.loc[predictions.Percentage >= 15]
    dominant_categories = dominant_categories.sort_values('Percentage', ascending = False)
    n_weak_categories = len(dominant_categories.index)

    if n_weak_categories > 0:
        page.write("#### Dominant categories")
        page.markdown("The categories of information with the largest percentages of\
                paragraphs identified in your file are:")
        
        if 2 > n_weak_categories > 0:
            page.metric(dominant_categories['Category'].iloc[0], str(dominant_categories['Percentage'].iloc[0]) + '%')
            page.markdown('- ' + dominant_reasonings[dominant_categories['Category'].iloc[0]])
        elif 3 > n_weak_categories > 1:
            column_one, column_two = page.columns(2)
            column_one.metric(dominant_categories['Category'].iloc[0], str(dominant_categories['Percentage'].iloc[0]) + '%')
            column_two.metric(dominant_categories['Category'].iloc[1], str(dominant_categories['Percentage'].iloc[1]) + '%')
            page.markdown('- ' + dominant_reasonings[dominant_categories['Category'].iloc[0]])
            page.markdown('- ' + dominant_reasonings[dominant_categories['Category'].iloc[1]])
        elif n_weak_categories > 2:
            column_one, column_two, column_three = page.columns(3)
            column_one.metric(dominant_categories['Category'].iloc[0], str(dominant_categories['Percentage'].iloc[0]) + '%')
            column_two.metric(dominant_categories['Category'].iloc[1], str(dominant_categories['Percentage'].iloc[1]) + '%')
            column_three.metric(dominant_categories['Category'].iloc[2], str(dominant_categories['Percentage'].iloc[2]) + '%')
            page.markdown('- ' + dominant_reasonings[dominant_categories['Category'].iloc[0]])
            page.markdown('- ' + dominant_reasonings[dominant_categories['Category'].iloc[1]])
            page.markdown('- ' + dominant_reasonings[dominant_categories['Category'].iloc[2]])

def write_weak_categories(page, predictions):

    weak_reasonings = {
        'CF – Contribution flow': "**Contribution flow:** When\
            joining an open source project, new contributors need to be aware of\
            the basics steps they need to follow in order to place their first\
            contribution. As a project maintainer, it is your task to make sure\
            the contribution flow of your project is clearly stated in your\
            documentation file.",
        'CT – Choose a task': "**Choose a task:** Newcomers need to know what\
            tasks they can work on and where they can find them. As a project\
            maintainer, you must provide instructions about where new\
            contributors can find tasks to work on.",
        'TC – Talk to the community': "**Talk to the community:** Newcomers\
            usually need assistance from the community while placing their\
            first contribution. Make sure your documentation file specifies\
            where they can get in touch with the community and maintainers.",
        'BW – Build local workspace': "**Build local workspace:** It is\
            impossible for new contributors to work on a project without\
            building their own workspace first. As a project maintainer, you\
            must provide tutorials on how newcomers can install the dependencies\
            of your project. Make sure you cover all the technical aspects\
            and limitations of your project while writing about this category.",
        'DC – Deal with the code': "**Deal with the code:** If you don't provide\
            information about how newcomers should deal with the source code\
            of your project, they might use their own style to create their first\
            contribution. This independence might delay the contribution process,\
            requiring more effort from project maintainers. Please, make sure you\
            clearly specify how newcomers should deal with your source code when\
            placing a contribution.",
        'SC – Submit the changes': "**Submit the changes:** A contribution would\
            not be complete without the submission of changes back to the open\
            source project. If this category is dominant in your documentation\
            file, it means that you are probably describing how newcomers\
            should submit their modifications, and that is great! However,\
            keep in mind that prior steps in the contribution process should\
            also be handled by your contributing file."}

    # Ignore the class "No categories identified"
    predictions = predictions[predictions['Category'] != 'No categories identified.']

    weak_categories = predictions.loc[predictions.Percentage < 15]
    weak_categories = weak_categories.sort_values('Percentage')
    n_weak_categories = len(weak_categories.index)
    
    if n_weak_categories > 0:
        page.write("#### Weak categories")
        page.markdown("The categories of information with the smallest percentages of\
                paragraphs identified in your file are:")
        
        if 2 > n_weak_categories > 0:
            page.metric(weak_categories['Category'].iloc[0], str(weak_categories['Percentage'].iloc[0]) + '%')
            page.markdown('- ' + weak_reasonings[weak_categories['Category'].iloc[0]])
        elif 3 > n_weak_categories > 1:
            column_one, column_two = page.columns(2)
            column_one.metric(weak_categories['Category'].iloc[0], str(weak_categories['Percentage'].iloc[0]) + '%')
            column_two.metric(weak_categories['Category'].iloc[1], str(weak_categories['Percentage'].iloc[1]) + '%')
            page.markdown('- ' + weak_reasonings[weak_categories['Category'].iloc[0]])
            page.markdown('- ' + weak_reasonings[weak_categories['Category'].iloc[1]])
        elif n_weak_categories > 2:
            column_one, column_two, column_three = page.columns(3)
            column_one.metric(weak_categories['Category'].iloc[0], str(weak_categories['Percentage'].iloc[0]) + '%')
            column_two.metric(weak_categories['Category'].iloc[1], str(weak_categories['Percentage'].iloc[1]) + '%')
            column_three.metric(weak_categories['Category'].iloc[2], str(weak_categories['Percentage'].iloc[2]) + '%')
            page.markdown('- ' + weak_reasonings[weak_categories['Category'].iloc[0]])
            page.markdown('- ' + weak_reasonings[weak_categories['Category'].iloc[1]])
            page.markdown('- ' + weak_reasonings[weak_categories['Category'].iloc[2]])
    
            if n_weak_categories > 3:
                page.error("Although just three categories of information are highlighted\
                    in this section, we identified that your documentation file has\
                    {} categories that should be adjusted.".format(n_weak_categories))

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

    for category in classes_color.keys():
        if category not in dataframe['Category'].values:
            dataframe.loc[len(dataframe.index),
             ['Category', 'Number of paragraphs', 'Repository', 'Color']] = [category, 0, repository_url, classes_color[category]]
        else:
            dataframe.loc[dataframe['Category'] == category, ['Color']] = classes_color[category]

    # Calculate percentage ignoring paragraphs without categories.
    # percentage = dataframe[dataframe['Category'] != 'No categories identified.']
    # percentage['Percentage'] = (percentage['Number of paragraphs'] / percentage['Number of paragraphs'].sum()) * 100
    # dataframe['Percentage'] = 0
    # dataframe.update(percentage)

    if dataframe['Number of paragraphs'].sum() > 0:
        dataframe['Percentage'] = (dataframe['Number of paragraphs'] / dataframe['Number of paragraphs'].sum()) * 100
    else:
        dataframe['Percentage'] = 0

    dataframe['Percentage'] = dataframe['Percentage'].astype(int)
    return dataframe


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas
import streamlit as st
from urllib.error import URLError
from scripts.get_contributing import get_contributing_file
from scripts.get_features import convert_paragraphs_into_features

@st.cache
def get_classification_model():
    return pandas.read_pickle('https://github.com/fronchetti/contributing.info/blob/main/resources/classification_model.sav?raw=true')

def get_contributing_predictions(page, repository_url):

    try:
        if len(repository_url) > 0:
            if 'github.com' not in repository_url:
                raise URLError('The URL must refer to a public repository hosted on GitHub with a CONTRIBUTING.md file.')

            paragraphs = get_contributing_file(repository_url)

            if paragraphs:
                # Loads the classification model.
                model = get_classification_model()

                # Using the estimator, predicts the classes for the paragraphs in the file
                predictions = model.predict(convert_paragraphs_into_features(paragraphs))

                return paragraphs, predictions
            else:
                raise Exception("The CONTRIBUTING.md file of the requested project is empty.")

    except TypeError as type_exception:
        page.warning(type_exception)
    except ConnectionError as conn_exception:
        page.warning(conn_exception)
    except URLError as url_exception:
        page.error(url_exception.reason)
    except Exception as generic_exception:
        page.error("Something went wrong. Please report this issue in our repository.\n")
        page.warning("Traceback: " + str(generic_exception))

    return [], []


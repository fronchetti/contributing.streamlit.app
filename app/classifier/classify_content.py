#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import streamlit as page
from urllib.error import URLError
from classifier.get_contributing import get_contributing_file
from classifier.get_features import convert_paragraphs_into_features

@page.cache(allow_output_mutation=True)
def load_classification_model(filepath):
	model = pickle.load((open(filepath, 'rb')))
	return model

def get_contributing_predictions(page, repository_url):
	try:
		if len(repository_url) > 0:
			if 'github.com' not in repository_url:
				raise URLError('URL must belong to GitHub.')

			paragraphs = get_contributing_file(repository_url)

			if paragraphs:
				# Loads the classification model.
				model = load_classification_model('classifier/classification_model.sav')

				# Using the estimator, predicts the classes for the paragraphs in the file
				predictions = model.predict(convert_paragraphs_into_features(paragraphs))

				return paragraphs, predictions
	except Exception as e:
		page.error("The URL provided does not refer to a public repository\
				   on GitHub with a valid contribution file.")
		print(e)

	return [], []

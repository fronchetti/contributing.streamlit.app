#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
import string
import pandas
from functools import partial
from spacy.lang.en import English
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
from nltk.stem.porter import PorterStemmer

def select_features(features):
    """Selects the best features to use before prediction

    Args:
        features (Dataframe): Prediction features
    Returns:
        Dataframe: Best features using SelectPercentile (chi-square)
    """

    selector = pickle.load(open('classifier/feature_selector.sav', 'rb'))
    best_features = selector.transform(features)

    return best_features

def add_column_name_prefix(column_name, prefix):
    return prefix + column_name

def create_statistic_features(X):
    """Converts paragraphs into TF-IDF features.

    Note that in this study, the TF-IDF features are mentioned
    as statistic features, while rule-based features are grouped
    as heuristic features.

    Args:
        X: String columns containing paragraphs.
    Returns:
        A sparse matrix of TF-IDF features.
    """

    vect_args = {
        'ngram_range': (1, 2),  # Google recomends: 1-gram + 2-grams
        'strip_accents': 'unicode',
        'decode_error': 'replace',
        'stop_words': 'english',
        'analyzer': 'word',
    }

    vectorizer = pickle.load(open('classifier/tf-idf.sav', 'rb'))
    features = vectorizer.transform(X)
    statistic_features = pandas.DataFrame(features.toarray(), columns=vectorizer.get_feature_names())

    statistic_features = statistic_features.rename(mapper=partial(add_column_name_prefix, prefix="stat_"), axis="columns")

    return statistic_features

def create_heuristic_features(X):
    """Creates a set of features using a rule-based matching approach over paragraphs.

    To improve the performance of the classification models, a set of rule-based features were
    created in conjunction with the TF-IDF features.

    Each rule defines a new feature in X, and it is represented as a column in the dataframe. 
    Each rule was manually defined by the researchers based on what they have
    learned during the qualitative analysis. The row values of each rule (column)
    are defined based on the expression given by the respective rule. 
    There is, for example, a rule in this study that verifies if the
    word "GitHub" appears in each paragraph.
    If the word appears in a paragraph, it defines the row value of the
    rule's column as 1 or 0 otherwise.

    All rules of this study are presented in the `patterns.jsonl` file inside
    the `classifier` folder. Learn more about rule-based
    matching at: spacy.io/usage/rule-based-matching

    Args:
        X: A string column containing paragraphs.
    Returns:
        A sparse matrix of heuristic features.
    """

    nlp = English()
    jsonl_filepath = os.path.join('classifier/patterns.jsonl')
    ruler = nlp.add_pipe("entity_ruler").from_disk(jsonl_filepath)

    heuristic_features = pandas.DataFrame()
    heuristic_features['Paragraph'] = X

    for heuristic in ruler.patterns:
        heuristic_features[heuristic['id']] = 0

    for index, row in heuristic_features.iterrows():
        doc = nlp(row['Paragraph'])

        for heuristic in doc.ents:
            heuristic_features.at[index, heuristic.ent_id_] = 1

    heuristic_features.drop('Paragraph', axis=1, inplace=True)

    heuristic_features = heuristic_features.rename(mapper=partial(add_column_name_prefix, prefix="heur_"), axis="columns")

    return heuristic_features

def text_preprocessing(X, techniques):
    """Applies text processing techniques to a dataframe column of strings (text).

    Before converting paragraphs into features, a good starting point may be to apply
    pre-processing techniques that will remove unwanted information. This method contains
    a series of submethods that represent common preprocessing techniques used in
    machine learning.
    
    X (Dataframe): Strings with raw text for classification.
    techniques (Dictionary): Keys representing techniques to be applied in the 
        text processing process.
    
    Returns:
        Dataframe: Column of strings updated with the values formated by the preprocessing
        techniques defined as input.
    """

    X = X.dropna()

    def lowercase(paragraph):
        # Transforms uppercase characters into lowercase
        return paragraph.lower()

    def remove_punctuations(paragraph):
        # Removes all the punctuations of the text, including: !"#$%&'()*+, -./:;<=>?@[\]^_`{|}~
        return paragraph.translate(str.maketrans('', '', string.punctuation))

    def remove_stopwords(paragraph):
        # Removes all the stopwords of the paragraph, such as: "the, for, but, nor"
        stop_words = set(stopwords.words('english'))
        return " ".join([word for word in paragraph.split() if word not in stop_words])

    def stemming(paragraph):
        # Applies a stemmer technique for each word
        # Read about stemming at:
        # nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html
        stemmer = PorterStemmer()
        return " ".join([stemmer.stem(word) for word in paragraph.split()])

    def lemmatization(paragraph):
        # Applies a lemattizer for each word
        # Read about lemmatization at:
        # nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html
        lemmatizer = WordNetLemmatizer()
        return " ".join([lemmatizer.lemmatize(word) for word in paragraph.split()])

    if 'lowercase' in techniques:
        X = X.apply(lambda paragraph: lowercase(paragraph))

    if 'remove-punctuations' in techniques:        
        X = X.apply(lambda paragraph: remove_punctuations(paragraph))

    if 'remove-stopwords' in techniques:
        X = X.apply(lambda paragraph: remove_stopwords(paragraph))
    
    if 'stemming' in techniques:
        X = X.apply(lambda paragraph: stemming(paragraph))

    if 'lemmatization' in techniques:
        X = X.apply(lambda paragraph: lemmatization(paragraph))

    return X

def convert_paragraphs_into_features(paragraphs):
    dataframe = pandas.Series(paragraphs)

    # print("Applying preprocessing techniques on paragraphs column.")
    preprocessing_techniques = ['remove-stopwords', 'remove-punctuations', 'lemmatization']
    paragraphs = text_preprocessing(dataframe, preprocessing_techniques)

    # print("Converting paragraphs into statistic features.")
    statistic_features = create_statistic_features(dataframe)

    # print("Converting paragraphs into heuristic features.")
    heuristic_features = create_heuristic_features(dataframe)

    # print("Selecting features with SelectPercentile (chi2).")
    best_features = select_features(pandas.concat([statistic_features, heuristic_features], axis=1))

    return best_features
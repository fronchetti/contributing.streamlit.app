#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import string
import pandas
import streamlit as st
from functools import partial
from nltk.corpus import stopwords
from spacy.lang.en import English
import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.stem.porter import PorterStemmer

nltk.download('stopwords')
nltk.download('wordnet')

@st.cache(allow_output_mutation=True)
def get_feature_selector():
    selector = pandas.read_pickle('https://github.com/fronchetti/contributing.info/blob/main/resources/feature_selector.sav?raw=true')
    return selector

@st.cache(allow_output_mutation=True)
def get_tf_idf_vectorizer():
    vectorizer = pandas.read_pickle('https://github.com/fronchetti/contributing.info/blob/main/resources/tf-idf.sav?raw=true')
    return vectorizer

def select_features(features):
    """Selects the best features to use before prediction

    Args:
        features (Dataframe): Prediction features
    Returns:
        Dataframe: Best features using SelectPercentile (chi-square)
    """

    cloned_selector = copy.deepcopy(get_feature_selector())
    best_features = cloned_selector.transform(features)

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

    cloned_vectorizer = copy.deepcopy(get_tf_idf_vectorizer())
    features = cloned_vectorizer.transform(X)
    statistic_features = pandas.DataFrame(features.toarray(), columns=cloned_vectorizer.get_feature_names())

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
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(heuristic_patterns)

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


heuristic_patterns = [{"label": "GIT", "pattern": [{"LOWER": "git"}], "id": "git"},
    {"label": "GIT", "pattern": [{"LOWER": "commit"}], "id": "commit"},
    {"label": "GIT", "pattern": [{"LOWER": "committer"}], "id": "committer"},
    {"label": "GIT", "pattern": [{"LOWER": "branch"}], "id": "branch"},
    {"label": "GIT", "pattern": [{"LOWER": "rebase"}], "id": "rebase"},
    {"label": "GIT", "pattern": [{"LOWER": "diff"}], "id": "diff"},
    {"label": "GIT", "pattern": [{"LOWER": "checkout"}], "id": "checkout"},
    {"label": "GIT", "pattern": [{"LOWER": "sync"}], "id": "sync"},
    {"label": "GIT", "pattern": [{"LOWER": "master"}], "id": "master"},
    {"label": "GIT", "pattern": [{"LOWER": "origin"}], "id": "origin"},
    {"label": "GIT", "pattern": [{"LOWER": "upstream"}], "id": "upstream"},
    {"label": "GIT", "pattern": [{"LOWER": "status"}], "id": "status"},
    {"label": "GIT", "pattern": [{"LOWER": "revert"}], "id": "revert"},
    {"label": "GIT", "pattern": [{"LOWER": "log"}], "id": "log"},
    {"label": "GIT", "pattern": [{"LOWER": "fetch"}], "id": "fetch"},
    {"label": "GIT", "pattern": [{"LOWER": "author"}], "id": "author"},
    {"label": "GIT", "pattern": [{"LOWER": "message"}], "id": "message"},
    {"label": "TASK", "pattern": [{"LOWER": "fork"}], "id": "fork"},
    {"label": "TASK", "pattern": [{"LOWER": "issue"}], "id": "issue"},
    {"label": "TASK", "pattern": [{"LOWER": "tracker"}], "id": "issue-tracker"},
    {"label": "TASK", "pattern": [{"LOWER": "issue"}, {"LOWER": "tracker"}], "id": "issue-tracker"},
    {"label": "TASK", "pattern": [{"LOWER": "issue"}, {"IS_PUNCT": True}, {"LOWER": "tracker"}], "id": "issue-tracker"},
    {"label": "TASK", "pattern": [{"LOWER": "label"}], "id": "label"},
    {"label": "TASK", "pattern": [{"LOWER": "title"}], "id": "title"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "code"}, {"IS_STOP": True}, {"LOWER": "conduct"}], "id": "code-of-conduct"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "mailing"}, {"IS_PUNCT": True}, {"LOWER": "list"}], "id": "mailing-list"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "mailing"}, {"LOWER": "list"}], "id": "mailing-list"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "contact"}], "id": "contact"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "mail"}], "id": "email"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "email"}], "id": "email"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "e"}, {"IS_PUNCT": True}, {"LOWER": "mail"}], "id": "email"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "contact"}, {"LOWER": "us"}], "id": "contact"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "contact"}, {"IS_PUNCT": True}, {"LOWER": "us"}], "id": "contact"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "get"}, {"LOWER": "in"}, {"LOWER": "touch"}], "id": "contact"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "question"}], "id": "questions"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "questions"}], "id": "questions"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "slack"}], "id": "communication-channel"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "gitter"}], "id": "communication-channel"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "twitter"}], "id": "communication-channel"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "irc"}], "id": "communication-channel"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "irc"}], "id": "communication-channel"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "code"}, {"IS_STOP": True}, {"LOWER": "conduct"}], "id": "code-of-conduct"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "conduct"}], "id": "code-of-conduct"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "harassment"}], "id": "bad-behavior"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "troll"}], "id": "bad-behavior"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "insult"}], "id": "bad-behavior"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "sexualized"}, {"LOWER": "language"}], "id": "bad-behavior"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "sexual"}, {"LOWER": "attention"}], "id": "bad-behavior"},
    {"label": "COMMUNITY", "pattern": [{"LOWER": "political"}, {"LOWER": "attack"}], "id": "bad-behavior"},
    {"label": "CODE", "pattern": [{"LOWER": "snippet"}], "id": "snippet"},
    {"label": "CODE", "pattern": [{"LOWER": "code"}, {"LOWER": "snippet"}], "id": "snippet"},
    {"label": "CODE", "pattern": [{"LOWER": "linter"}], "id": "linter"},
    {"label": "CODE", "pattern": [{"LOWER": "lint"}], "id": "linter"},
    {"label": "CODE", "pattern": [{"LOWER": "text"}, {"LOWER": "editor"}], "id": "text-editor"},
    {"label": "CODE", "pattern": [{"LOWER": "text"}, {"IS_PUNCT": True}, {"LOWER": "editor"}], "id": "text-editor"},
    {"label": "CODE", "pattern": [{"LOWER": "coding"}, {"LOWER": "convention"}], "id": "coding-style"},
    {"label": "CODE", "pattern": [{"LOWER": "coding"}, {"LOWER": "style"}], "id": "coding-style"},
    {"label": "CODE", "pattern": [{"LOWER": "coding"}, {"LOWER": "rules"}], "id": "coding-style"},
    {"label": "CODE", "pattern": [{"LOWER": "coding"}, {"LOWER": "guidelines"}], "id": "coding-style"},
    {"label": "CODE", "pattern": [{"LOWER": "tabs"}], "id": "tabs"},
    {"label": "CODE", "pattern": [{"LOWER": "soft"}, {"LOWER": "tabs"}], "id": "tabs"},
    {"label": "CODE", "pattern": [{"LOWER": "readability"}], "id": "readability"},
    {"label": "CODE", "pattern": [{"LOWER": "maintainability"}], "id": "maintainability"},
    {"label": "CODE", "pattern": [{"LOWER": "testability"}], "id": "maintainability"},
    {"label": "CODE", "pattern": [{"LOWER": "elegance"}], "id": "elegance"},
    {"label": "CODE", "pattern": [{"LOWER": "docstring"}], "id": "docstring"},
    {"label": "CODE", "pattern": [{"LOWER": "comment"}], "id": "comment"},
    {"label": "CODE", "pattern": [{"LOWER": "library"}], "id": "library"},
    {"label": "CODE", "pattern": [{"LOWER": "module"}], "id": "module"},
    {"label": "CODE", "pattern": [{"LOWER": "function"}], "id": "function"},
    {"label": "CODE", "pattern": [{"LOWER": "method"}], "id": "method"},
    {"label": "CODE", "pattern": [{"LOWER": "variable"}], "id": "variable"},
    {"label": "CODE", "pattern": [{"LOWER": "component"}], "id": "component"},
    {"label": "CODE", "pattern": [{"LOWER": "database"}], "id": "database"},
    {"label": "CODE", "pattern": [{"LOWER": "postgres"}], "id": "database"},
    {"label": "CODE", "pattern": [{"LOWER": "mysql"}], "id": "database"},
    {"label": "CODE", "pattern": [{"LOWER": "mongodb"}], "id": "database"},
    {"label": "CODE", "pattern": [{"LOWER": "redis"}], "id": "database"},
    {"label": "CODE", "pattern": [{"LOWER": "sqlite"}], "id": "database"},
    {"label": "CODE", "pattern": [{"LOWER": "mariadb"}], "id": "database"},
    {"label": "CODE", "pattern": [{"LOWER": "python"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"LOWER": "java"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"LOWER": "ruby"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"LOWER": "javascript"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"LOWER": "php"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"TEXT": "C#"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"TEXT": "C++"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"LOWER": "typescript"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"LOWER": "shell"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"TEXT": "C"}], "id": "programming-language"},
    {"label": "CODE", "pattern": [{"LOWER": "debug"}], "id": "debug"},
    {"label": "CODE", "pattern": [{"LOWER": "sdk"}], "id": "sdk"},
    {"label": "CODE", "pattern": [{"LOWER": "jdk"}], "id": "sdk"},
    {"label": "CODE", "pattern": [{"LOWER": "software"}, {"LOWER": "development"}, {"LOWER": "kit"}], "id": "sdk"},
    {"label": "CODE", "pattern": [{"LOWER": "docker"}], "id": "docker"},
    {"label": "CODE", "pattern": [{"LOWER": "pep"}], "id": "coding-convention"},
    {"label": "CODE", "pattern": [{"LOWER": "pep"}, {"IS_PUNCT": True}, {"IS_DIGIT": True}], "id": "coding-convention"},
    {"label": "CODE", "pattern": [{"LOWER": "psr"}], "id": "coding-convention"},
    {"label": "CODE", "pattern": [{"LOWER": "psr"}, {"IS_PUNCT": True}, {"IS_DIGIT": True}], "id": "coding-convention"},
    {"label": "SETUP", "pattern": [{"LOWER": "tool"}], "id": "tool"},
    {"label": "SETUP", "pattern": [{"LOWER": "run"}], "id": "run"},
    {"label": "SETUP", "pattern": [{"LOWER": "package"}], "id": "package"},
    {"label": "SETUP", "pattern": [{"LOWER": "install"}], "id": "install"},
    {"label": "SETUP", "pattern": [{"LOWER": "update"}], "id": "update"},
    {"label": "SETUP", "pattern": [{"LOWER": "upgrade"}], "id": "upgrade"},
    {"label": "SETUP", "pattern": [{"LOWER": "remove"}], "id": "remove"},
    {"label": "SETUP", "pattern": [{"LOWER": "setup"}], "id": "setup"},
    {"label": "SETUP", "pattern": [{"LOWER": "configuration"}], "id": "setup"},
    {"label": "SETUP", "pattern": [{"LOWER": "dependency"}], "id": "dependency"},
    {"label": "SETUP", "pattern": [{"LOWER": "dependencies"}], "id": "dependency"},
    {"label": "SETUP", "pattern": [{"LOWER": "yarn"}], "id": "package-manager"},
    {"label": "SETUP", "pattern": [{"LOWER": "pip"}], "id": "package-manager"},
    {"label": "SETUP", "pattern": [{"LOWER": "npm"}], "id": "package-manager"},
    {"label": "SETUP", "pattern": [{"LOWER": "virtual"}, {"LOWER": "environment"}], "id": "environment"},
    {"label": "SETUP", "pattern": [{"LOWER": "source"}, {"LOWER": "code"}], "id": "source-code"},
    {"label": "SETUP", "pattern": [{"LOWER": "source"}], "id": "source-code"},
    {"label": "SETUP", "pattern": [{"LOWER": "requirement"}], "id": "requirement"},
    {"label": "SETUP", "pattern": [{"LOWER": "cd"}], "id": "shell-command"},
    {"label": "SETUP", "pattern": [{"LOWER": "mv"}], "id": "shell-command"},
    {"label": "SETUP", "pattern": [{"LOWER": "ls"}], "id": "shell-command"},
    {"label": "SETUP", "pattern": [{"LOWER": "dir"}], "id": "shell-command"},
    {"label": "FLOW", "pattern": [{"LOWER": "flow"}], "id": "flow"},
    {"label": "FLOW", "pattern": [{"LOWER": "contribution"}, {"LOWER": "flow"}], "id": "contribution-flow"},
    {"label": "FLOW", "pattern": [{"LOWER": "github"}], "id": "github"},
    {"label": "FLOW", "pattern": [{"LOWER": "release"}], "id": "release"},
    {"label": "FLOW", "pattern": [{"LOWER": "pull"}], "id": "pull-request"},
    {"label": "FLOW", "pattern": [{"LOWER": "pull"}, {"LOWER": "request"}], "id": "pull-request"},
    {"label": "FLOW", "pattern": [{"LOWER": "pull"}, {"IS_PUNCT": True}, {"LOWER": "request"}], "id": "pull-request"},
    {"label": "FLOW", "pattern": [{"LOWER": "clone"}], "id": "clone"},
    {"label": "FLOW", "pattern": [{"LOWER": "push"}], "id": "push"},
    {"label": "FLOW", "pattern": [{"LOWER": "merge"}], "id": "merge"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "changelog"}], "id": "changelog"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "ci"}], "id": "continuous-integration"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "continuous"}, {"LOWER": "integration"}], "id": "continuous-integration"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "jenkins"}], "id": "continuous-integration-tool"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "travis"}], "id": "continuous-integration-tool"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "travis"}, {"LOWER": "ci"}], "id": "continuous-integration-tool"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "circle"}, {"LOWER": "ci"}], "id": "continuous-integration-tool"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "license"}], "id": "license"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "cla"}], "id": "contributor-license-agreement"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "contributor"}, {"LOWER": "license"}, {"LOWER": "agreement"}], "id": "contributor-license-agreement"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "gnu"}], "id": "gnu"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "mit"}], "id": "mit"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "review"}], "id": "review"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "test"}], "id": "testing"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "unit"}, {"LOWER": "testing"}], "id": "testing"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "test"}, {"LOWER": "suite"}], "id": "test-suite"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "commit"}, {"LOWER": "guidelines"}], "id": "commit-guidelines"},
    {"label": "SUBMISSION", "pattern": [{"LOWER": "commit"}, {"LOWER": "message"}, {"LOWER": "guidelines"}], "id": "commit-guidelines"}]
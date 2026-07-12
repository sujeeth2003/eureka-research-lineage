from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
import pandas as pd

def extract_top_terms_per_cluster(df):
    # 1. Compute TF-IDF matrix
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df["abstract"])
    terms = vectorizer.get_feature_names_out()

    # 2. Extract top 5 terms per cluster and build a list of dictionaries
    top_n = 5
    export_data = []


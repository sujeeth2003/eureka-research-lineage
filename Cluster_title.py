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

    for cluster_num in sorted(df["cluster_id"].unique()):
        # Get row indices for the current cluster
        row_indices = df[df["cluster_id"] == cluster_num].index

        # Subset matrix and calculate mean scores
        cluster_matrix = tfidf_matrix[row_indices]
        mean_scores = np.asarray(cluster_matrix.mean(axis=0)).flatten()

        # Match terms with scores and sort descending
        sorted_terms = pd.Series(mean_scores, index=terms).sort_values(
            ascending=False
        )
        top_terms_list = sorted_terms[sorted_terms > 0].head(top_n).index.tolist()

        # Join terms into a single comma-separated string
        terms_string = ", ".join(top_terms_list)

        # Append results
        export_data.append(
            {"cluster_id": cluster_num, f"top_{top_n}_terms": terms_string}
        )

    return export_data



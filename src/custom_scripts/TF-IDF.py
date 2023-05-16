import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv('Book1.csv')

# Create a TF-IDF vectorizer and fit it on the 'answer' column
vectorizer = TfidfVectorizer()

# Loop over each row in the DataFrame
for index, row in df.iterrows():
    # Define the question
    question = row['question']
    
    # Transform the 'answer' column into a TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform([row['answer']])
    
    # Transform the question into a TF-IDF vector
    question_tfidf = vectorizer.transform([question])
    
    # Calculate the cosine similarity between the question vector and the answer vector
    cosine_similarities = cosine_similarity(question_tfidf, tfidf_matrix).flatten()
    
    # # Get the index of the most similar answer
    most_similar_index = cosine_similarities.argmax()
    
    # # Get the most important word from the answer
    most_important_words = sorted(vectorizer.vocabulary_.items(), key=lambda x: x[1])[most_similar_index][0]

    ## add the most important word to the DataFrame to the answer column
    df.loc[index, 'answer'] = most_important_words

    # Save the DataFrame to a CSV file
    df.to_csv('questions_preprocessed_1.csv', index=False)
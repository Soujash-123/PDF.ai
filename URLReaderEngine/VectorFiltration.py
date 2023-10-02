import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def FilterWRT(prompt, statements):
    # Tokenize and preprocess the prompt
    prompt_tokens = nltk.word_tokenize(prompt.lower())
    prompt_tokens = [token for token in prompt_tokens if token.isalpha()]

    # Tokenize and preprocess the statements
    statement_tokens_list = []
    for statement in statements:
        statement_tokens = nltk.word_tokenize(statement.lower())
        statement_tokens = [token for token in statement_tokens if token.isalpha()]
        statement_tokens_list.append(" ".join(statement_tokens))

    # Create TF-IDF vectors for the prompt and statements
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([prompt] + statement_tokens_list)
    prompt_vector = vectors[0]  # Vector representation of the prompt
    statement_vectors = vectors[1:]  # Vectors representation of the statements

    # Calculate cosine similarity between the prompt vector and statement vectors
    similarities = cosine_similarity(prompt_vector, statement_vectors)
    most_similar_index = similarities.argmax()  # Get the index of the most similar statement

    # Return the most relatable statement
    most_relatable_statement = statements[most_similar_index]

    return most_relatable_statement
if __name__ == '__main__':
    prompt = "What is the capital of France?"
    statements = [["France is an European Country",
                  "Eiffle Tower is in France"],
                  ["The capital of France is Paris",
                  "French is the official language of France."],
                  ["The capital of France is located in the same place as the Eiffel Tower."]]
    for i in statements:
            print(FilterWRT(prompt,i))
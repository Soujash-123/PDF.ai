import PyPDF2
import requests
from bs4 import BeautifulSoup
import re
import spacy
from transformers import pipeline

# Download the spacy model
# Note: You may need to download the model for your specific language
# and entity recognition requirements (e.g., 'en_core_web_sm')
# using: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

# Function to extract text from a PDF file
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()
    return text

# Function to extract text from a website
def extract_text_from_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text()
    return text

# Preprocess the text by removing special characters, extra whitespaces, etc.
def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    # Add more text preprocessing steps as needed
    return text

# Function to extract named entities from the text using spaCy
def extract_named_entities(text):
    doc = nlp(text)
    named_entities = [ent.text for ent in doc.ents]
    return named_entities

# Function to find answers to the questions using BERT-based question-answering
def find_answers(question, context):
    question_answering = pipeline("question-answering")
    result = question_answering(question=question, context=context)
    return result["answer"]

if __name__ == "__main__":
    # Extract text from a PDF or a website
    website_url = "https://www.cdc.gov/pcd/issues/2021/20_0573.htm"
    text_from_website = extract_text_from_website(website_url)
    preprocessed_text_from_website = preprocess_text(text_from_website)
    named_entities_from_website = extract_named_entities(preprocessed_text_from_website)

    # Sample questions
    question1 = input(">>>")
    answer1 = find_answers(question1, preprocessed_text_from_website)
    print(f"Answer to '{question1}': {answer1}")
    
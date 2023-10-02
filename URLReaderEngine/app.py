import requests
import chardet
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from VectorFiltration import FilterWRT
import openai

from flask import Flask, render_template, request

app = Flask(__name__)

def preprocess_text(text):
    # Tokenize the text into words
    tokens = word_tokenize(text.lower())

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    return filtered_tokens

def Layer1(text):
    tokens = preprocess_text(text)
    fdist = FreqDist(tokens)
    tokens = fdist.most_common(10)
    keywords = []
    if tokens:
        for keyword, count in tokens:
            keywords.append(keyword)
    return keywords

def Layer2(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.content
        encoding = chardet.detect(content)['encoding']
        content = content.decode(encoding)
        soup = BeautifulSoup(content, 'html.parser')
        contents = []
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            contents.append(paragraph.get_text())
        text = ' '.join(contents)
        tokens = preprocess_text(text)
        fdist = FreqDist(tokens)
        tokens = fdist.most_common(10)
        keywords = []
        if tokens:
            for keyword, count in tokens:
                keywords.append(keyword)
        return keywords
    except (requests.exceptions.RequestException, UnicodeDecodeError) as e:
        print('An error occurred:', e)
    except:
        print("Error Detected")

def Layer3(url, keywords, prompt_keywords):
    union_keywords = []
    for i in prompt_keywords:
        if i in keywords:
            union_keywords.append(i)
    paragraphs = []
    required_lines = []
    file_name = ""
    for i in url:
        if i.isdigit():
            file_name += i
    with open("./utils/" + file_name, "r", encoding='utf-8') as file:
        lines = file.read().split(".")
        for line in lines:
            line = line.strip()
            if all(word in line for word in union_keywords):
                required_lines.append(line)

    return required_lines

def Layer4(prompt, statements):
    probable_statements=[FilterWRT(prompt,statements)]
    return probable_statements

def Layer5(prompt, lst):
    reference = ".".join(lst[0])
    system_prompt = f"Answer the following question: \n {prompt} \n using the following lines as reference {reference}."
    openai.api_key = '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'
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=system_prompt,
        max_tokens=64,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    generated_statement = response.choices[0].text.strip()
    return generated_statement

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    url = request.form['url']
    prompt = request.form['prompt']

    keywords = Layer2(url)
    prompt_keywords = Layer1(prompt)
    paragraphs = Layer3(url, keywords, prompt_keywords)
    most_suitable_statements = Layer4(prompt, paragraphs)
    generated_statement = Layer5(prompt, paragraphs)

    return render_template('result.html', url=url, prompt=prompt, generated_statement=generated_statement, lines=paragraphs)

if __name__ == '__main__':
    app.run(debug=True)
import os
import PyPDF2
import string
import nltk
import replicate
import os

os.environ["REPLICATE_API_TOKEN"] = "r8_L61JGnVMdFrJQ3xCUSSkbCOXxyMoIyu1uh3Cx"

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class PhysicsDocumentReader:
    def __init__(self, api_key, directory):
        self.api_key = api_key
        self.directory = directory
        self.subject = None

    def readPDF(self, pdf_file):
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            full_text = ""
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                full_text += page.extractText()

        sentences = sent_tokenize(full_text)
        return sentences

    def sortChapterWise(self):
        self.subject = {}
        os.chdir(self.directory)
        for i in os.listdir():
            pdf_sentences = self.readPDF(i)
            self.subject[i] = pdf_sentences

    def preprocess_text(self, text):
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower()
        return text

    def getKeywords(self, text):
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
        return filtered_tokens

    def identifyChapter(self, prompt):
        prompt = self.preprocess_text(prompt)
        
        chapter_matches = {}
        for chapter, content in self.subject.items():
            chapter_text = " ".join(content)
            chapter_text = self.preprocess_text(chapter_text)
            
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([prompt, chapter_text])
            
            similarity = cosine_similarity(tfidf_matrix)
            chapter_matches[chapter] = similarity[0][1]

        matching_chapter = max(chapter_matches, key=chapter_matches.get)

        if chapter_matches[matching_chapter] > 0:
            return matching_chapter, self.findRelevantStatements(prompt, matching_chapter)
        else:
            return "Chapter not found.", []

    def findRelevantStatements(self, prompt, chapter_match):
        p_keywords = self.getKeywords(prompt)
        statements = [i for i in self.subject[chapter_match] if any(keyword in i for keyword in p_keywords)]
        return statements

    def answer_with_llm(self, prompt):
        pre_prompt = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'. Skip the greeting part and avoid asking questions. Pretend like you're answering a question in the exam paper."
        prompt_input ="Explain in atleast 250 words:" + prompt

        # Generate LLM response
        output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', # LLM model
                                input={"prompt": f"{pre_prompt} {prompt_input} Assistant: ", # Prompts
                                "temperature":0.7, "top_p":0.9, "max_length":128, "repetition_penalty":1})  # Model parameters
             
        full_response = ""

        for item in output:
          full_response += item

        return(full_response)


if __name__ == "__main__":
    api_key = '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'

    # Gather user input for subject and class
    subject_name = input("Enter the subject: ")
    class_name = input("Enter the class (e.g., Class11, Class12, etc.): ")

    # Construct the directory path based on user input
    directory = os.path.join(r'C:\Users\SOUJASH\Desktop\RanjanaEnterprises\REDB', subject_name, class_name)

    physics_reader = PhysicsDocumentReader(api_key, directory)
    physics_reader.sortChapterWise()

    prompt = "Explain the nature of Electromagnetic waves."

    chapter_match, statements = physics_reader.identifyChapter(prompt)
    print("The question is likely from:", chapter_match)

    answer = physics_reader.answer_with_llm(prompt)
    print("\nAnswer using LLM:")
    print(answer)

    #if len(statements) > 0:
     #   print("Relevant statements:")
      #  for statement in statements[0]:
       #     print("-", statement)

    # Get keywords from LLM answer
    llm_keywords = physics_reader.getKeywords(answer)
    print("LLM Answer Keywords:")
    print(llm_keywords)

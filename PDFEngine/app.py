from flask import Flask, render_template, request, redirect, url_for
from physics_document_reader import PhysicsDocumentReader
import os
import replicate

os.environ["REPLICATE_API_TOKEN"] = "r8_L61JGnVMdFrJQ3xCUSSkbCOXxyMoIyu1uh3Cx"


app = Flask(__name__)

base_directory = r'C:\Users\SOUJASH\Desktop\RanjanaEnterprises\REDB'
physics_reader = None


@app.route('/', methods=['GET', 'POST'])
def index():
    global physics_reader

    if request.method == 'POST':
        subject = request.form['subject']
        class_name = request.form['class']

        # Construct the directory path based on selected subject and class
        directory = os.path.join(base_directory, subject, class_name)

        # Initialize the physics_reader only if it's None or the directory changed
        if physics_reader is None or physics_reader.directory != directory:
            physics_reader = PhysicsDocumentReader("", directory)
            physics_reader.sortChapterWise()

        prompt = request.form['prompt']
        chapter_match, statements = physics_reader.identifyChapter(prompt)
        answer = physics_reader.answer_with_llm(prompt)
        statements = physics_reader.findRelevantStatements(prompt, chapter_match)[:10]

        # Generate the "How we concluded" part using OpenAI
        conclusion=""
        for i in statements:
            conclusion+=i+"."
        return render_template('result.html', asked_question=prompt, chapter_match=chapter_match, statements=statements, answer=answer, conclusion=conclusion)
    
    return render_template('index.html')

@app.route('/upload_pdf_page')
def upload_pdf_page():
    return render_template('upload_pdf_page.html')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    global physics_reader

    if request.method == 'POST':
        prompt = request.form['prompt']
        # Do further processing with the uploaded PDF file and the prompt here
        # For demonstration, let's just print the prompt
        print(f"Prompt: {prompt}")
        answer = physics_reader.answer_with_llm(prompt)

        # Generate the "How we concluded" part using OpenAI
        conclusion_prompt = f"Describe in 6-5 steps how you concluded this answer: {answer}. Keep the steps short and self-explanatory."
        conclusion_response = openai.Completion.create(
            engine="text-davinci-002",  # GPT-3.5 engine
            prompt=conclusion_prompt,
            max_tokens=200,
            temperature=0.7
        )
        conclusion = conclusion_response.choices[0].text.strip()

        return render_template('result.html', asked_question=prompt, answer=answer, conclusion=conclusion)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='localhost', port=1000, debug=True)

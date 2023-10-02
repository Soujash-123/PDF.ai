import requests
import chardet
from bs4 import BeautifulSoup

def RAFL(url):
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
        return contents
    except (requests.exceptions.RequestException, UnicodeDecodeError) as e:
        print('An error occurred:', e)

url = 'https://www.cdc.gov/pcd/issues/2021/20_0573.htm'
file_name=""
for i in url:
    if i.isdigit():
        file_name += i
result = RAFL(url)
text = []
if result:
    for content in result:
        text.append(content)
text = ' '.join(text)
file = open("./utils/"+file_name,"a+",encoding = 'utf-8')
file.write(text)
file.close()
contents=""
with open("./utils/"+file_name, "r" , encoding  = 'utf-8') as f:
    contents = f.read()
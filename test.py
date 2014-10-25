import requests
import urlparse

token = ""

with open('config/token', 'r') as f:
    token = f.read()

HEADERS = {
        "Authorization": "Token {token}".format(token=token),
        "Content-Type": "application/json",
        }

CORPUS_UPLOAD_PARAMS_ENDPOINT = "https://api.getlightbox.com/api/corpus-upload-parameters/"
CORPORA_ENDPOINT = "https://api.getlightbox.com/api/corpora/"
PROMPTS_ENDPOINT = "https://api.getlightbox.com/api/prompts/"
TRAINING_ANSWERS_ENDPOINT = "https://api.getlightbox.com/api/training-answers/"
ANSWERS_ENDPOINT = "https://api.getlightbox.com/api/answers/"

prompts = [
        "Why did the United States declare independence?",
        "How did the moon form?",
        "In Macbeth, whose ambition is the driving force of the play?",
        "How does Tom Sawyer change over the course of the story?",
        "What is Gestalt psychology?"
        ]

def show_url(endpoint, resource_id):
    return urlparse.urljoin(endpoint, resource_id)

def id_from_url(url):
    return url.split("/")[-1]

def s3_params():
    r = requests.get(CORPUS_UPLOAD_PARAMS_ENDPOINT, headers=HEADERS)
    return r.json()

def send_corpus_file():
    data = {
            'AWSAccessKeyId': params['access_key_id'],
            'key': params['key'],
            'acl': 'public-read',
            'Policy': params['policy'],
            'Signature': params['signature'],
            'success_action_status': '201',
            }

    files = {'file': open('answers.csv', 'rb')}
    r = requests.post(params['s3_endpoint'], data=data, files=files)

def create_prompt(title="", text="", description=""):
    data = { "title": title, "text": text, "description": description }
    r = requests.post(PROMPTS_ENDPOINT, data=json.dumps(data), headers=HEADERS)
    return id_from_url(r.json()['url'])

def create_corpus(prompt_id=0, description=""):
    data = {
            "prompt": show_url(PROMPTS_ENDPOINT, prompt_id),
            "description": description
            }
    r = requests.post(CORPORA_ENDPOINT, data=json.dumps(data), headers=HEADERS)
    return id_from_url(r.json()['url'])


def initialize_lightbox(title="", prompt_text="", prompt_description=""):
    prompt_id = create_prompt
    print "Created prompt: {prompt_id}".format(prompt_id=prompt_id)


if __name__ == "__main__":
    print s3_params()

import requests
import urlparse
import json

token = ""

with open('config/token', 'r') as f:
    token = f.read().strip()

CORPUS_UPLOAD_PARAMS_ENDPOINT = "https://api.getlightbox.com/api/corpus-upload-parameters/"
TRAINING_ANSWERS_ENDPOINT = "https://api.getlightbox.com/api/training-answers/"
ANSWERS_ENDPOINT = "https://api.getlightbox.com/api/answers/"
ANSWER_SETS_ENDPOINT = "https://api.getlightbox.com/api/answer-sets/"

prompts = [
        "Why did the United States declare independence?",
        "How did the moon form?",
        "In Macbeth, whose ambition is the driving force of the play?",
        "How does Tom Sawyer change over the course of the story?",
        "What is Gestalt psychology?"
        ]

class LightboxResource:
    base_url = "https://api.getlightbox.com/api/"
    endpoint = None

    HEADERS = {
            "Authorization": "Token {token}".format(token=token),
            "Content-Type": "application/json",
            }

    @staticmethod
    def endpoint_of(resource):
        return urlparse.urljoin(LightboxResource.base_url, resource+"/")

    def set_id(self, _id):
        self._id = _id
        self.show_url = urlparse.urljoin(self.endpoint, _id)

    def get(self):
        r = requests.get(self.show_url, headers=LightboxResource.HEADERS)
        self.response = r.json()

    def __init__(self, data):
        if 'id' in data:
            self.set_id(data['id'])
            self.get()
        else:
            print self.HEADERS
            r = requests.post(self.endpoint, data=json.dumps(data), headers=self.HEADERS)
            self.response = r.json()

            if 'url' in self.response:
                self.set_id(self.response['url'].split('/')[-1])

class Prompt(LightboxResource):
    endpoint = LightboxResource.endpoint_of("prompts")

    def __init__(self, title, text, description):
        LightboxResource.__init__(self, { 'title': title, 'text': text, 'description': description })

class Corpus(LightboxResource):
    endpoint = LightboxResource.endpoint_of("corpora")
    params_endpoint = LightboxResource.endpoint_of("corpus-upload-parameters")
    s3_params = None

    @staticmethod
    def get_s3_params():
        r = requests.get(Corpus.params_endpoint, headers=LightboxResource.HEADERS)
        Corpus.s3_params = r.json()

    @staticmethod
    def send_file(filename):
        get_s3_params()
        data = {
                'AWSAccessKeyId': Corpus.s3_params['access_key_id'],
                'key': Corpus.s3_params['key'],
                'acl': 'public-read',
                'Policy': Corpus.s3_params['policy'],
                'Signature': Corpus.s3_params['signature'],
                'success_action_status': '201',
                }
        files = { 'file': open(filename, 'rb') }
        r = requests.post(Corpus.s3_params['s3_endpoint'], data=data, files=files)

class Answer(LightboxResource):
    endpoint = LightboxResource.endpoint_of("answers")

if __name__ == "__main__":
    # get s3 params
    #Corpus.get_s3_params()
    #print Corpus.s3_params

    # create a new prompt
    p = Prompt("test", "This is a test. Don't answer me!", "only a test")
    print p._id

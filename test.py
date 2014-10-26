import requests
import urlparse
import json
import random

token = ""
with open('config/token', 'r') as f:
    token = f.read().strip()

prompts = [
        "Why did the United States declare independence?",
        "How did the moon form?",
        "In Macbeth, whose ambition is the driving force of the play?",
        "How does Tom Sawyer change over the course of the story?",
        "What is Gestalt psychology?"
        ]

class LightboxResource(object):
    base_url = "https://api.getlightbox.com/api/"
    endpoint = None

    HEADERS = {
            "Authorization": "Token {token}".format(token=token),
            "Content-Type": "application/json",
            }

    @staticmethod
    def endpoint_for(resource):
        return urlparse.urljoin(LightboxResource.base_url, resource+"/")

    @staticmethod
    def id_from_url(url):
        return url.split('/')[-1]

    @classmethod
    def url_for(cls, _id):
        url = urlparse.urljoin(cls.endpoint, str(_id))

    @classmethod
    def find(cls, _id):
        r = requests.get(cls.url_for(_id), headers=cls.HEADERS)
        obj = cls(_id, response.json())
        return obj

    @classmethod
    def create(cls, data):
        r = requests.post(cls.endpoint, data=json.dumps(data), headers=cls.HEADERS)
        response = r.json()
        obj = cls(cls.id_from_url(response['url']), response)
        return obj

    def __init__(self, _id, response={}):
        self._id = _id
        self.response = response

class Prompt(LightboxResource):
    endpoint = LightboxResource.endpoint_for("prompts")

    @classmethod
    def create(cls, title="", text="", description=""):
        super(Prompt, cls).create({
            'title': title,
            'text': text,
            'description': description
            })

class Grader(LightboxResource):
    endpoint = LightboxResource.endpoint_for("graders")

    @classmethod
    def create(cls, prompt_id, name="Grader"):
        super(Grader, cls).create({
            'prompt': Prompt.url_for(prompt_id),
            'name': name
            })

class Lightbox(LightboxResource):
    endpoint = LightboxResource.endpoint_for("lightboxes")

    @classmethod
    def create(cls, grader_id, name="Lightbox"):
        super(Lightbox, cls).create({
            'grader': Grader.url_for(grader_id),
            'name': name
            })

class Corpus(LightboxResource):
    endpoint = LightboxResource.endpoint_for("corpora")
    params_endpoint = LightboxResource.endpoint_for("corpus-upload-parameters")
    s3_params = {}

    @classmethod
    def create(cls, prompt_id=None, description=""):
        if not prompt_id:
            return None

        super(Corpus, cls).create({
            'prompt': Prompt.url_for(prompt_id),
            'description': description
            })

    @classmethod
    def get_s3_params(cls):
        r = requests.get(cls.params_endpoint, headers=cls.HEADERS)
        cls.s3_params = r.json()

    @classmethod
    def send_file(cls, filename):
        cls.get_s3_params()
        data = {
                'AWSAccessKeyId': cls.s3_params['access_key_id'],
                'key': cls.s3_params['key'],
                'acl': 'public-read',
                'Policy': cls.s3_params['policy'],
                'Signature': cls.s3_params['signature'],
                'success_action_status': '201',
                }
        files = { 'file': open(filename, 'rb') }
        r = requests.post(cls.s3_params['s3_endpoint'], data=data, files=files)

class Author(LightboxResource):
    endpoint = LightboxResource.endpoint_for("authors")

    @classmethod
    def create(cls, designator=("%016x" % random.getrandbits(64)), email=""):
        super(Author, cls).create({
            'designator': designator,
            'email': email
            })

class AnswerSet(LightboxResource):
    endpoint = LightboxResource.endpoint_for("answer-sets")

    @classmethod
    def create(cls, lightbox_id):
        super(AnswerSet, cls).create({
            'lightbox': Lightbox.url_for(lightbox_id)
            })

class Answer(LightboxResource):
    endpoint = LightboxResource.endpoint_for("answers")

    @classmethod
    def create(cls, author_id, answer_set_id, text):
        if not author_id or not answer_set_id or not text:
            return None

        super(Answer, cls).create({
            'author': Author.url_for(prompt_id),
            'answer_set': AnswerSet.url_for(answer_set_id),
            'text': text
            })

if __name__ == "__main__":
    # get s3 params
    #Corpus.get_s3_params()
    #print Corpus.s3_params

    # create a new prompt
    #p = Prompt("test", "This is a test. Don't answer me!", "only a test")
    #print p._id

    # 35, 36 -> test prompts
    #Prompt.find(35)
    #p = Prompt.create("test2", "Your answer means nothing, NOTHING!", "yet another test")
    pass

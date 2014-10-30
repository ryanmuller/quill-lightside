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
        return urlparse.urljoin(cls.endpoint, str(_id))

    # TODO fail elegantly
    @classmethod
    def all(cls):
        r = requests.get(cls.endpoint, headers=cls.HEADERS)
        response = r.json()
        objs = [ cls(cls.id_from_url(obj['url']), obj) for obj in response['results'] ]
        return objs

    @classmethod
    def find(cls, _id):
        r = requests.get(cls.url_for(_id), headers=cls.HEADERS)
        obj = cls(_id, r.json())
        return obj

    @classmethod
    def create(cls, data):
        r = requests.post(cls.endpoint, data=json.dumps(data), headers=cls.HEADERS)
        response = r.json()
        obj = cls(cls.id_from_url(response['url']), response)
        return obj

    # TODO test me
    def reload(self):
        self = type(self).find(self._id)
        return self

    # TODO inherit only from Tasks
    # TODO better info from status
    def process(self):
        if 'process' in self.response:
            r = requests.post(self.response['process'], headers=type(self).HEADERS)
            return r.status_code == 200 or r.status_code == 202
        else:
            return False

    def url(self):
        return type(self).url_for(self._id)

    def destroy(self):
        r = requests.delete(self.url(), headers=type(self).HEADERS)
        return self

    def __init__(self, _id, response={}):
        self._id = _id
        self.response = response

class Prompt(LightboxResource):
    endpoint = LightboxResource.endpoint_for("prompts")

    @classmethod
    def create(cls, title="", text="", description=""):
        return super(Prompt, cls).create({
            'title': title,
            'text': text,
            'description': description
            })

    def text(self):
        return self.response['text']

class Grader(LightboxResource):
    endpoint = LightboxResource.endpoint_for("graders")

    @classmethod
    def create(cls, prompt_id, name="Grader"):
        return super(Grader, cls).create({
            'prompt': Prompt.url_for(prompt_id),
            'name': name
            })

    def prompt(self):
        p = self.response['prompt']
        return Prompt(LightboxResource.id_from_url(p['url']), p)

class Lightbox(LightboxResource):
    endpoint = LightboxResource.endpoint_for("lightboxes")

    @classmethod
    def create(cls, grader_id, name="Lightbox"):
        return super(Lightbox, cls).create({
            'grader': Grader.url_for(grader_id),
            'name': name
            })

    # TODO set in __init__?
    def name(self):
        return self.response['name']

    def grader(self):
        return Grader.find(LightboxResource.id_from_url(self.response['grader']))

    def answer_set(self):
        aset = self.response['answer_set']
        return AnswerSet(LightboxResource.id_from_url(aset['url']), aset)

class Corpus(LightboxResource):
    endpoint = LightboxResource.endpoint_for("corpora")
    params_endpoint = LightboxResource.endpoint_for("corpus-upload-parameters")
    s3_params = {}

    # note: description is required
    @classmethod
    def create(cls, prompt_id=None, description="primary corpus"):
        if not prompt_id:
            return None

        return super(Corpus, cls).create({
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
        return r.status_code == 201

class CorpusUploadTask(LightboxResource):
    endpoint = LightboxResource.endpoint_for("corpus-upload-tasks")

    @classmethod
    def create(cls, corpus_id, s3_key, content_type="text/csv"):
        if not s3_key and 'key' in Corpus.s3_params:
            s3_key = Corpus.s3_params['key']

        if not corpus_id or not s3_key:
            return None

        return super(CorpusUploadTask, cls).create({
            'corpus': Corpus.url_for(corpus_id),
            's3_key': s3_key,
            'content_type': content_type
            })

class Author(LightboxResource):
    endpoint = LightboxResource.endpoint_for("authors")

    @classmethod
    def create(cls, designator=("%016x" % random.getrandbits(64)), email=""):
        return super(Author, cls).create({
            'designator': designator,
            'email': email
            })

class TrainingAnswer(LightboxResource):
    endpoint = LightboxResource.endpoint_for("training-answers")

    @classmethod
    def create(cls, corpus_id, text):
        if not corpus_id or not text:
            return None

        return super(TrainingAnswer, cls).create({
            'corpus': Corpus.url_for(corpus_id),
            'text': text
            })

class ResolvedScore(LightboxResource):
    endpoint = LightboxResource.endpoint_for("resolved-scores")

    @classmethod
    def create(cls, training_answer_id, label):
        if not training_answer_id or not label:
            return None

        return super(ResolvedScore, cls).create({
            'training_answer': TrainingAnswer.url_for(training_answer_id),
            'label': label
            })

class HumanScore(LightboxResource):
    endpoint = LightboxResource.endpoint_for("human-scores")

    @classmethod
    def create(cls, training_answer_id, label):
        if not training_answer_id or not label:
            return None

        return super(HumanScore, cls).create({
            'training_answer': TrainingAnswer.url_for(training_answer_id),
            'label': label
            })

class TrainingTask(LightboxResource):
    endpoint = LightboxResource.endpoint_for("training-tasks")

    @classmethod
    def create(cls, corpus_id, grader_id):
        return super(TrainingTask, cls).create({
            'corpus': Corpus.url_for(corpus_id),
            'grader': Grader.url_for(grader_id)
            })

class TrainedModel(LightboxResource):
    endpoint = LightboxResource.endpoint_for("trained-models")

class AnswerSet(LightboxResource):
    endpoint = LightboxResource.endpoint_for("answer-sets")

    # FIXME
    @classmethod
    def create(cls, lightbox_id):
        return super(AnswerSet, cls).create({
            'lightbox': Lightbox.url_for(lightbox_id)
            })

class Answer(LightboxResource):
    endpoint = LightboxResource.endpoint_for("answers")

    @classmethod
    def create(cls, author_id, answer_set_id, text):
        if not author_id or not answer_set_id or not text:
            return None

        return super(Answer, cls).create({
            'author': Author.url_for(author_id),
            'answer_set': AnswerSet.url_for(answer_set_id),
            'text': text
            })

    def prediction_result(self):
        if 'prediction_results' in self.response and len(self.response['prediction_results']) > 0:
            return PredictionResult.find(LightboxResource.id_from_url(self.response['prediction_results'][0]))
        else:
            return None

class PredictionTask(LightboxResource):
    endpoint = LightboxResource.endpoint_for("prediction-tasks")

    @classmethod
    def create(cls, answer_set_id):
        return super(PredictionTask, cls).create({
            'answer_set': AnswerSet.url_for(answer_set_id)
            })

# GET /prediction-results/
# GET /prediction-results/(int: prediction_result_id)
class PredictionResult(LightboxResource):
    endpoint = LightboxResource.endpoint_for("prediction-results")

    def label(self):
        return self.response['label']

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
    Prompt.all()

    # A Proclamation About Rosa Parks
    # Prompt: 20 (?)
    # Grader: 34
    # Lightbox: 30
    # AnswerSet: 30
    # Author: 1
    # Answer: 1580


    # test
    # prompt: 35
    # grader: 44
    # lightbox: 31
    # answerset: 31
    # answer: 1581
    # 

    # Water Cycle
    # prompt: 37
    # grader: 45
    # lightbox: 33 
    # answer-set: 33
    # corpus: 164
    # training answer: 41503
    # resolved score: 41503
    # human score: 1
    # s3 key: corpus-uploads/2014/10/28/56d59c80102d4e7db5bc5707fce24759.csv
    # training task: 96
    # trained model: 164
    # prediction task: 1584


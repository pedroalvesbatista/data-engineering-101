import luigi
import ipdb
import pickle
from os import listdir
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from luigi import six
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import CountVectorizer

def read_input(input):
  X, y = [], []
  for line in input.open('r'):
    items = line.strip().split(',')
    X.append(items[1])
    y.append(items[0])
  return X, y

# Scrape NYT API and put in Mongo

# Acquire Data (web scraping) for date, load from mongo

# Parse Article (Beautiful Soup) and store in mongo or as flat files

# Load data from files
class InputText(luigi.ExternalTask):
    """
    This class represents something that was created elsewhere by an external process,
    so all we want to do is to implement the output method.
    """
    filename = luigi.Parameter()

    def output(self):
        """
        Returns the target output for this task.
        In this case, it expects a file to be present in the local file system.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        root = '/Users/jonathandinu/Repositories/workshopper/data-engineering-101/'
        return luigi.LocalTarget(root + self.filename)

## Tokenize Data
class Tokenization(luigi.Task):
    input_dir = luigi.Parameter()

    def requires(self):
        """
        Which other Tasks need to be complete before
        this Task can start? Luigi will use this to 
        compute the task dependency graph.
        """
        #ipdb.set_trace()
        return [ InputText(self.input_dir + '/' + filename) for filename in listdir(self.input_dir) ]

    def output(self):
        """
        When this Task is complete, where will it produce output?
        Luigi will check whether this output (specified as a Target) 
        exists to determine whether the Task needs to run at all.
        """
        
        return luigi.LocalTarget(self.input_dir + '/tokenized.tsv')

    def run(self):
        """
        How do I run this Task?
        Luigi will call this method if the Task needs to be run.
        """
        # remove stop words and punctuation
        stop = set(stopwords.words('english'))
        tokenizer = RegexpTokenizer(r'\w+')
        wordnet = WordNetLemmatizer()

        docs = []

        for f in self.input(): # The input() method is a wrapper around requires() that returns Target objects
            lines = 0
            words = []

            for line in f.open('r'):
                if lines == 0:
                    label = line
                    lines +=1
                else:
                    words.extend(tokenizer.tokenize(line))
                    lines +=1

            words_filtered = filtered_words = [wordnet.lemmatize(w) for w in words if not w in stopwords.words('english')]
            docs.append((label, '\t'.join(words)))

        out = self.output().open('w')
        for label, tokens in docs:
            out.write("%s,%s\n" % (label.strip(), tokens.strip()))
        out.close()

## Vectorize Data (stemming)
class Vectorize(luigi.Task):
    input_dir = luigi.Parameter()

    def requires(self):
        return Tokenization(self.input_dir)

    def run(self):
        corpus, labels = read_input(self.input())

        vectorizer = CountVectorizer(min_df=1)
        X = vectorizer.fit_transform(corpus)

        fc = self.output()[0].open('w')
        fv = self.output()[1].open('w')
        fl = self.output()[2].open('w')
        pickle.dump(X, fc)
        pickle.dump(vectorizer, fv)
        fl.write(','.join(labels))
        fc.close()
        fv.close()
        fl.close()

    def output(self):
        return [luigi.LocalTarget('models/corpus.pickle'),
                luigi.LocalTarget('models/vectorizer.pickle'),
                luigi.LocalTarget('models/labels.csv')]

## Train (and serialize) Model
class TrainClassifier(luigi.Task):
  input_dir = luigi.Parameter()
  lam = luigi.FloatParameter(default=1)

  def requires(self):
    return Vectorize(self.input_dir)

  def run(self):
    from sklearn.naive_bayes import MultinomialNB

    corpus, vect, lab = self.input()
    
    # deserialize inputs
    vectorizer = pickle.load(vect.open('r'))
    X = pickle.load(corpus.open('r'))
    labels = lab.open('r').read().split(',')

    c = MultinomialNB(alpha=self.lam)
    c.fit(X, labels)

    f = self.output().open('w')
    pickle.dump(c, f)
    f.close()

  def output(self):
    return luigi.LocalTarget('models/model-alpha-%d.pickle' % self.lam)

# Offshoots

## Build Topic Models
class TopicModel(luigi.Task):
  input_dir = luigi.Parameter()
  num_topics = luigi.IntParameter(default=1)

  def requires(self):
    return Vectorize(self.input_dir)

  def run(self):
    corpus, vect, lab = self.input()

    # deserialize inputs
    vectorizer = pickle.load(vect.open('r'))
    X = pickle.load(corpus.open('r'))
    labels = lab.open('r').read().split(',')

    nmf = NMF(n_components=self.num_topics).fit(X)

    f = self.output().open('w')
    pickle.dump(nmf, f)
    f.close()

  def output(self):
    return luigi.LocalTarget('models/model-topic-%d.pickle' % self.num_topics)

class BuildModels(luigi.Task):
    input_dir = luigi.Parameter()
    lam = luigi.FloatParameter(default=1)
    num_topics = luigi.IntParameter(default=1)

    def requires(self):
        return [TrainClassifier(self.input_dir, self.lam), TopicModel(self.input_dir, self.num_topics)]

if __name__ == '__main__':
    luigi.run()
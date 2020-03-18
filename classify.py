import yaml
import sys
import random
import nltk
import operator
import jellyfish as jf
import json
import requests
import os
import time
import signal
import subprocess
from nltk.tag import StanfordPOSTagger
from textblob.classifiers import NaiveBayesClassifier
from execute import construct_command
from feedback import get_user_feedback
#from feedback import get_response
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn import preprocessing

my_path = os.path.abspath(os.path.dirname(__file__))
print(my_path)

CONFIG_PATH = os.path.join(my_path, "REIA_repo/config/config.yml")
print(CONFIG_PATH)
MAPPING_PATH = os.path.join(my_path, "REIA_repo/data/mapping.json")
print(MAPPING_PATH)
TRAINDATA_PATH = os.path.join(my_path, "REIA_repo/data/traindata.txt")
print(TRAINDATA_PATH)
LABEL_PATH = os.path.join(my_path, "REIA_repo/data")
print(LABEL_PATH)

sys.path.insert(0, LABEL_PATH)
import trainlabel

with open(CONFIG_PATH,"r") as config_file:
	config = yaml.load(config_file)

os.environ['STANFORD_MODELS'] = config['tagger']['path_to_models']

exec_command = config['preferences']['execute']

def classify(text):
	X_train = np.array([line.rstrip('\n') for line in open(TRAINDATA_PATH)])
	y_train_text = trainlabel.y_train_text
	X_test = np.array([text])
	target_names = ['file', 'folder', 'network', 'system', 'general']

	lb = preprocessing.MultiLabelBinarizer()
	Y = lb.fit_transform(y_train_text)

	classifier = Pipeline([
		('vectorizer', CountVectorizer()),
		('tfidf', TfidfTransformer()),
		('clf', OneVsRestClassifier(LinearSVC()))])

	classifier.fit(X_train, Y)
	predicted = classifier.predict(X_test)
	all_labels = lb.inverse_transform(predicted)

	for item, labels in zip(X_test, all_labels):
		return (', '.join(labels))

print("Starting...")	
x = classify("shift $s1 by $s2 and store the result in $s3")
print(x)


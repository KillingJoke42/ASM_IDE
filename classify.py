import yaml
import sys
import json
import os
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn import preprocessing

my_path = os.path.abspath(os.path.dirname(__file__))

TRAINDATA_PATH = os.path.join(my_path, "REIA_repo/data/traindata.txt")
LABEL_PATH = os.path.join(my_path, "REIA_repo/data")

sys.path.insert(0, LABEL_PATH)
import trainlabel

def classify(text):
	X_train = np.array([line.rstrip('\n') for line in open(TRAINDATA_PATH)])
	y_train_text = trainlabel.y_train_text
	X_test = np.array([text])

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


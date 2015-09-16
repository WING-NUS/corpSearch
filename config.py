from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from vocab.tokenizers import LowerTokenizer
from system.systems import *

twitter_classifier = RandomForestClassifier()
facebook_classifier = RandomForestClassifier()

converter = Final

tokenizer = LowerTokenizer

evaluate_converter = Final

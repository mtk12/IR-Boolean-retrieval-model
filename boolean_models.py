import numpy as np
import pandas as pd
from flask import Flask, render_template,request
import re
from collections import defaultdict
from nltk.stem import PorterStemmer

#stemming initialization
ps = PorterStemmer() 

#creates inverted index
def inverted_index(stop_words):
    
    dictionary = {}
    documents = {}
    
    for i in range(0,56):
        doc_no = i
        with open ("Trump Speechs\Trump Speechs\speech_" + str(doc_no) + ".txt",'r') as file:
            next(file)
            s=file.read().replace('\n',' ')
        
        #cleaning documents
        s = re.sub('  ', ' ', s)
        s = re.sub(r"won't", "will not", s)
        s = re.sub(r"can\'t", "can not", s)
        s = re.sub(r"n\'t", " not", s)
        s = re.sub(r"\'re", " are", s)
        s = re.sub(r"\'s", " is", s)
        s = re.sub(r"\'d", " would", s)
        s = re.sub(r"\'ll", " will", s)
        s = re.sub(r"\'t", " not", s)
        s = re.sub(r"\'ve", " have", s)
        s = re.sub(r"\'m", " am", s)
        s = re.sub(r'[0-9]+', '', s)
        s=re.sub(r'[^\w\s]',' ', s)
        key = 'speech_' + str(doc_no)
        
        documents.setdefault(key,[])
        documents[key].append(s)
        
        #removing stopwords and lowercase
        s = s.lower()
        s = [words if words not in stop_words else '' for words in s.split(' ')]
        doc = []
        doc = list(filter(None, s)) 
        stemmed = []
        
        #stemming
        for i in doc:
            stemmed.append(ps.stem(i))
            
        #creating posting list
        for x in stemmed:
            key = x
            dictionary.setdefault(key, [])
            dictionary[key].append(doc_no)
            
        #removing duplicates
        dictionary = {a:list(set(b)) for a, b in dictionary.items()}
        
    return dictionary,documents

#creates positional index
def positional_index(stop_words):
    
    dictionary = {}
    documents = {}
    for i in range(0,56):
        doc_no = i
        with open ("Trump Speechs\Trump Speechs\speech_" + str(doc_no) + ".txt",'r') as file:
            s=file.read().replace('\n',' ')[1:]
        
        #cleaning documents
        s = re.sub('  ', ' ', s)
        s = re.sub(r"won't", "will not", s)
        s = re.sub(r"can\'t", "can not", s)
        s = re.sub(r"n\'t", " not", s)
        s = re.sub(r"\'re", " are", s)
        s = re.sub(r"\'s", " is", s)
        s = re.sub(r"\'d", " would", s)
        s = re.sub(r"\'ll", " will", s)
        s = re.sub(r"\'t", " not", s)
        s = re.sub(r"\'ve", " have", s)
        s = re.sub(r"\'m", " am", s)
        s=re.sub(r'[^\w\s]',' ', s)
        
        key = 'speech_' + str(doc_no)
        documents.setdefault(key,[])
        documents[key].append(s)
        
        s = s.lower()
        s = s.split(' ')
        doc = []
        doc = list(filter(None, s)) 
        temp_dict = {}
        stemmed = []
        
        #stemming
        for i in doc:
            stemmed.append(ps.stem(i))
        
        #creating positional index posting lists
        a = 0
        for x in stemmed:
            key = x
            temp_dict.setdefault(key, [])
            temp_dict[key].append(a)
            a += 1
        for x in temp_dict:
            if dictionary.get(x):
                dictionary[x][doc_no] = temp_dict.get(x)
            else:
                key = x
                dictionary.setdefault(key, [])
                dictionary[key] = {}
                dictionary[x][doc_no] = temp_dict.get(x)
            
    return dictionary,documents
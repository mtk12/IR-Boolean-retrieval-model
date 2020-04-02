import numpy as np
import pandas as pd
from flask import Flask, render_template,request
import query_processing
import boolean_models
import time

app = Flask(__name__)

#Getting stopwords from the file
stop_words = []
with open ("Stopword-List.txt",'r') as file:
    s=file.read().replace('\n',' ')
stop_words = s.split()

#Getting inverted_index and positional_index
dictionary_inverted,docu = boolean_models.inverted_index(stop_words)
dictionary_positional,docu = boolean_models.positional_index(stop_words)

#Returning Relevant document retrieved
def documents_ret(a):
    
    documents = {}
    if(a):
        for i in a:
            speech = "speech_" + str(i)
            documents.setdefault(speech,[])
            documents[speech].append(docu.get(speech))
    else:
        documents = {}
    
    return documents
        

#Default page display/home_page
@app.route('/')
def dictionary():
    return render_template('home.html')

#Funtion will invoke whenever a query is posted
@app.route("/query", methods=['POST'])
def upload():
    #query processing start time
    start = time.time()
    #getting query from the HTML form
    query = request.form['query']
    #Checking for boolean,proximity and phrase queries
    if('/' in query):
        result = query_processing.positional_query(query,dictionary_positional)
    elif('"' not in query):
        result = query_processing.process_query(query,dictionary_inverted)
    else:
        result = query_processing.phrase_query(query,dictionary_positional,dictionary_inverted)

    documents = documents_ret(result)
    print(result)
    end = time.time()
    #total time to process query
    times = end - start
    return render_template('dictionary.html',dictionary = documents, num_docs= len(documents), time = str(times) + " " + "seconds")

if __name__ == '__main__':
    app.run()

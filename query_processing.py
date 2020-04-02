import re
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import wordnet as wn
from collections import defaultdict
from nltk.stem import PorterStemmer 


ps = PorterStemmer() 

#All documents
doc_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
           28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]

#infix to postifix query
def postfix(infix_tokens):
    
    #precendence initialization
    precedence = {}
    precedence['NOT'] = 3
    precedence['AND'] = 2
    precedence['OR'] = 1
    precedence['('] = 0
    precedence[')'] = 0    

    output = []
    operator_stack = []
    
    #creating postfix expression
    for token in infix_tokens:
        if (token == '('):
            operator_stack.append(token)

        elif (token == ')'):
            operator = operator_stack.pop()
            while operator != '(':
                output.append(operator)
                operator = operator_stack.pop()
        
        elif (token in precedence):
            if (operator_stack):
                current_operator = operator_stack[-1]
                while (operator_stack and precedence[current_operator] > precedence[token]):
                    output.append(operator_stack.pop())
                    if (operator_stack):
                        current_operator = operator_stack[-1]

            operator_stack.append(token)

        else:
            output.append(token.lower())
    
    #while staack is not empty appending
    while (operator_stack):
        output.append(operator_stack.pop())
    return output

#AND two posting lists
def AND_op(word1,word2):
    if ((word1) and (word2)):
        return set(word1).intersection(word2)
    else:
        return set()
     
#OR two posting lists
def OR_op(word1,word2):
    return set(word1).union(word2)
   
#NOT two posting lists
def NOT_op(a,doc_ids):
    return set(doc_ids).symmetric_difference(a)

#Boolean query processing
def process_query(q,dictionary_inverted):

    q = q.replace('(', '( ')
    q = q.replace(')', ' )')
    q = q.split(' ')
    query = []

    for i in q:
        query.append(ps.stem(i))
    for i in range(0,len(query)):
        if ( query[i]== 'and' or query[i]== 'or' or query[i]== 'not'):
            query[i] = query[i].upper()
    results_stack = []
    postfix_queue = postfix(query)

    #evaluating postfix query expression
    for i in postfix_queue:
        if ( i!= 'AND' and i!= 'OR' and i!= 'NOT'):
            i = i.replace('(', ' ')
            i = i.replace(')', ' ')
            i = i.lower()
            i = dictionary_inverted.get(i)
            results_stack.append(i)
        elif (i=='AND'):
            a = results_stack.pop()
            b = results_stack.pop()
            results_stack.append(AND_op(a,b))
        elif (i=='OR'):
            a = results_stack.pop()
            b = results_stack.pop()
            results_stack.append(OR_op(a,b))
        elif (i == 'NOT'):
            a = results_stack.pop()
            print(a)
            results_stack.append(NOT_op(a,doc_ids))
            
    return results_stack.pop()

#Evaluating proximity query
def positional_query(q,dictionary_positional):
    
    q = re.sub(r"AND", "", q)
    q = re.sub(r"  ", " ", q)
    q = q.split(' ')
    query = []
    
    for i in q:
        query.append(ps.stem(i))
        
    word1 = dictionary_positional.get(query[0])
    word2 = dictionary_positional.get(query[1])
    anding = set(word1).intersection(word2)
    
    query[2] = re.sub(r"/", "", query[2])
    answer = []
    skip = int(query[2]) + 1
    for i in anding:
        pp1 = dictionary_positional.get(query[0])[i]
        pp2 = dictionary_positional.get(query[1])[i]
        plen1 = len(pp1)
        plen2 = len(pp2)
        ii = jj = 0 
        while ii != plen1:
            while jj != plen2:
                if (abs(pp1[ii] - pp2[jj]) == skip):
                    answer.append(i)
                elif pp2[jj] > pp1[ii]:
                    break    
                jj+=1
            ii+=1
    answer = list(dict.fromkeys(answer))
    return answer

#checking whether word is present within position
def doc_check(ii,jj,plen1,plen2,skip,pp1,pp2):
    while ii != plen1:
        while jj != plen2:
            if (abs(pp1[ii] - pp2[jj]) == skip):
                return 1
            elif pp2[jj] > pp1[ii]:
                break
            jj+=1
        ii+=1
    return 0

#Evaluating phrase query     
def phrase_query(q,dictionary_positional,dictionary_inverted):
    
    q = q.replace('"', '')
    q = q.split()

    query = []
    for i in q:
        query.append(ps.stem(i))
        query.append('AND')
    query.pop()
    query = " ".join(query)
    anding = process_query(query,dictionary_positional)
    print(anding)
    answer = []
    query = query.replace('AND','')
    query = query.split()
    print(query)

    for i in anding:
        pp1 = dictionary_positional.get(query[0].lower())[i]
        flag = []
        skip = 1
        for x in range(1,len(query)):
            pp2 = dictionary_positional.get(query[x].lower())[i]
            plen1 = len(pp1)
            plen2 = len(pp2)
            ii = jj = 0 
            flag.append(doc_check(ii,jj,plen1,plen2,skip,pp1,pp2))
            skip = skip + 1
        if(0 not in flag):
            answer.append(i)
    answer = list(dict.fromkeys(answer))
    
    return answer
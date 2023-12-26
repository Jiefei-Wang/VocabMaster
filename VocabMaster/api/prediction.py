

import pandas as pd
import numpy as np
import datetime
import random
#from statsmodels.miscmodels.ordinal_model import OrderedModel

##############################################
# vanilla prediction
##############################################
# word counts
def countWordFreqs(learningWordsDF):
    count = {}
    for i in range(len(learningWordsDF)):
        record = learningWordsDF.loc[i]
        word = record.word
        if word not in count:
            count[word] = {'total': 0,
                           'known':0,
                           'fuzzy':0,
                           'unknown':0
                           }
        count[word]['total'] += 1
        status = record.answer
        if status == 0:
            count[word]['unknown'] += 1
        if status == 1:
            count[word]['fuzzy'] += 1
        if status == 2:
            count[word]['known'] += 1
    return count
        



def predictNextWordsPlain(allWords, learningWordsDF, n):
    N =max(10,n)
    # number of simultanouse learning words
    nLearning = 10
    # number of repeats before using logistic model
    learnCutoff = 10
    
    ## The learning words
    count = learningWordsDF.groupby('word').size()
    count_learning = count[count<learnCutoff]
    sorted_data = count_learning.sort_values()
    nextWords = list(sorted_data.index)
    
    if len(nextWords)>N:
        nextWords = nextWords[:N]
    
    ## If number of words is less than required
    if len(nextWords)<N:
        newWords = list(set(allWords) - set(learningWordsDF.word))
        nNewWords = N-len(nextWords)
        nNewWords = min(len(newWords), nNewWords)
        nextWords = newWords[:nNewWords]+ nextWords
    
    if len(nextWords)<N:
        oldWords = list(count[count>=learnCutoff].index)
        nOldWords = N-len(nextWords)
        nOldWords = min(len(oldWords), nOldWords)
        nextWords = nextWords + oldWords[:nOldWords]
        random.shuffle(nextWords)
    
    
    n_pick = min(n,len(nextWords))
    nextWords = nextWords[:n_pick]
    
    df = pd.DataFrame({
        'word': nextWords,
        'prob': [np.NaN] * len(nextWords)
    })
    return df



##############################################
# logistic prediction
##############################################
## Prepare the matrix for doing the logistic regression
def logisticData(learningWordsDF):
    count = {}
    index = []
    
    df = pd.DataFrame({
        'word': [],
        'answer': [],
        'n': [],
        'dt': [],
        'study':[],
        'unknown':[],
        'fuzzy':[],
        'known':[]
    })
    
    for i in range(len(learningWordsDF)):
        record = learningWordsDF.loc[i]
        word = record.word
        if word not in count:
            count[word] = {
                'date': record.date,
                'n': 0,
                'study': record.studyTime,
                'known':0,
                'fuzzy':0,
                'unknown':0
            }
            index.append(i)
        
        df.loc[len(df.index)] = [
                                record.word,
                                record.answer,
                                count[word]['n'],
                                record.date - count[word]['date'], 
                                count[word]['study'],
                                count[word]['unknown'],
                                count[word]['fuzzy'],
                                count[word]['known']
                                ] 
        count[word]['n'] += 1
        count[word]['date'] = record.date
        count[word]['study'] = record.studyTime
        status = record.answer
        if status == 0:
            count[word]['unknown'] += 1
        if status == 1:
            count[word]['fuzzy'] += 1
        if status == 2:
            count[word]['known'] += 1
        
    df = df.loc[~df.index.isin(index)]
    TransAndAddColDF(df)
    
    
    currentTime = datetime.datetime.now().timestamp()
    df_new = pd.DataFrame({
        'word': [],
        'n': [],
        'dt': [],
        'study':[],
        'unknown':[],
        'fuzzy':[],
        'known':[]
    })
    for word,value in count.items():
        df_new.loc[len(df_new.index)] = [
            word,
            value['n'],
            currentTime - count[word]['date'],
            value['study'],
            value['unknown'],
            value['fuzzy'],
            value['known']
        ]
    
    TransAndAddColDF(df_new)
    
    return [df, df_new, count]
    
## Add columns and do the log transformation
def TransAndAddColDF(df):
    df.n = np.log(df.n)
    df.dt = np.log(df.dt)
    df.study = np.log(df.study)
    df["n*dt"] = df.n * df.dt
    df["study*dt"] = df.study * df.dt


def predictNextWordsLogistic(allWords, learningWordsDF, n):
    ## For performing logistic regression
    ## Minimum the number of record requirement
    minRecords = 100
    ## Minimum number of words requirement
    minWords = 10
    
    if len(learningWordsDF) < minRecords or len(pd.unique(learningWordsDF.word))<minWords:
        return predictNextWordsPlain(allWords, learningWordsDF, n)
    
    
    [df, df_new, _] = logisticData(learningWordsDF)
    colName = ['n', 'dt', 'study', 'unknown', 'fuzzy', 'known', 'n*dt', 'study*dt']
    
    mod_prob = OrderedModel(df.answer,
                    df[colName],
                    distr='probit')
    res_log = mod_prob.fit(method='bfgs')

    predicted = res_log.model.predict(res_log.params, exog=df_new[colName])
    predictedDF = pd.DataFrame({
        'word' : df_new.word,
        'prob' : [x[2] for x in predicted]
    })
    
    n_pick = min(n , len(predictedDF))
    predictedNext = predictedDF.sort_values(by='prob')[:n_pick]
    
    
    if len(predictedNext)<n:
        newWords = list(set(allWords) - set(learningWordsDF.word))
        nNewWords = n-len(newWords)
        nNewWords = min(len(newWords), nNewWords)
        newWordsDF = pd.DataFrame({
            'word' : newWords[:nNewWords],
            'prob' : [None] * nNewWords
        })
        predictedNext = pd.concat([predictedNext, newWordsDF])
    
    return predictedNext


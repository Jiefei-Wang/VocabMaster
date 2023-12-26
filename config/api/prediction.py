

import pandas as pd
import numpy as np
import datetime
import random
#from statsmodels.miscmodels.ordinal_model import OrderedModel
from sklearn.linear_model import LogisticRegression

##############################################
# vanilla prediction
##############################################
# word counts
def countWordFreqs(learningWordsDF):
    count = {}
    for i in range(len(learningWordsDF)):
        record = learningWordsDF.iloc[i]
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
    N = max(10,n)
    # number of repeats before using logistic model
    learnCutoff = 4
    
    ## The learning words
    count = learningWordsDF.groupby('word').size()
    count_learning = count[count<learnCutoff]
    sorted_data = count_learning.sort_values()
    nextWords = list(sorted_data.index)
    
    first_answers = learningWordsDF.groupby('word')[["word","answer"]].head(1)
    known_words = first_answers[first_answers.answer==2]
    nextWords = list(set(nextWords) - set(known_words.word))
    
    
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
    
    currentTime = datetime.datetime.now().timestamp()
    df = pd.DataFrame({
        'word': [],
        'answer': [],
        'n_round': [],
        'review_interval': [],
        'time_since_first': [],
        'study_time':[],
        'unknown':[],
        'fuzzy':[],
        'known':[]
    })
    
    for i in range(len(learningWordsDF)):
        record = learningWordsDF.iloc[i]
        word = record.word
        if word not in count:
            count[word] = {
                'date': record.date,
                'n_round': 0,
                'last_time': record.date,
                'study_time': record.studyTime,
                'known':0,
                'fuzzy':0,
                'unknown':0,
                'first_time': record.date
            }
            index.append(i)
        
        df.loc[len(df.index)] = [
                                record.word,
                                record.answer,
                                count[word]['n_round'],
                                record.date - count[word]['last_time'], 
                                record.date - count[word]['first_time'], 
                                record.studyTime,
                                count[word]['unknown'],
                                count[word]['fuzzy'],
                                count[word]['known']
                                ] 
        count[word]['n_round'] += 1
        count[word]['last_time'] = record.date
        status = record.answer
        if status == 0:
            count[word]['unknown'] += 1
        if status == 1:
            count[word]['fuzzy'] += 1
        if status == 2:
            count[word]['known'] += 1
        
    df = df.loc[~df.index.isin(index)]
    df = TransAndAddColDF(df)
    
    
    df_new = pd.DataFrame({
        'word': [],
        'n_round': [],
        'review_interval': [],
        'time_since_first': [],
        'study_time':[],
        'unknown':[],
        'fuzzy':[],
        'known':[]
    })
    for word,value in count.items():
        timediff1 = currentTime - count[word]['last_time']
        if timediff1 < 0:
            timediff1 = 0
            
        timediff2 = currentTime - count[word]['first_time']
        if timediff2 < 0:
            timediff2 = 0
        
        df_new.loc[len(df_new.index)] = [
            word,
            value['n_round'],
            timediff1,
            timediff2,
            value['study_time'],
            value['unknown'],
            value['fuzzy'],
            value['known']
        ]
    
    df_new = TransAndAddColDF(df_new)
    
    return [df, df_new, count]
    
def calc_weight(group):
    n = len(group)
    weights = pd.Series(range(1, n+1), index=group.index)
    return weights / weights.sum()


## Add columns and do the log transformation
def TransAndAddColDF(df):
    df = df.reset_index()
    if 'answer' in df:
        df.loc[df.answer==1,'answer'] = 0
        df.loc[df.answer==2,'answer'] = 1
    
    weights = df.groupby('word').apply(calc_weight).reset_index(level=0, drop=True)
    df['weight'] = weights
    
    df.unknown = df.unknown + df.fuzzy
    df.n_round = np.log(df.n_round)
    df.review_interval = np.log(df.review_interval + 1)
    df.study_time= np.log(df.study_time + 1)
    df.time_since_first= np.log(df.time_since_first + 1)
    df["n_round*review_interval"] = df.n_round * df.review_interval
    df["study_time*review_interval"] = df.study_time * df.review_interval
    return df


def predictNextWordsLogistic(allWords, learningWordsDF, n):
    ## For performing logistic regression
    ## Minimum the number of record requirement
    minRecords = 50
    ## Minimum number of words requirement
    minWords = 20
    
    if  len(learningWordsDF)<minRecords or len(pd.unique(learningWordsDF.word))<minWords:
        return predictNextWordsPlain(allWords, learningWordsDF, n)
    
    
    [df, df_new, _] = logisticData(learningWordsDF)
    colName = ['n_round', 'review_interval', 'time_since_first', 'study_time', 'unknown', 'known']
    #colName2 = ["word", 'n_round', 'review_interval', 'time_since_first', 'study_time', 'unknown', 'known']
    #print(df_new[colName2])
    # test = df_new[df_new['review_interval'].isna()]
    #if len(test)!=0:
    #    word = test.word[0]
    #    print(learningWordsDF[learningWordsDF.word==word])
    #    print(df[df.word==word])
    #    print(df_new[df_new.word==word])
    
    
    logmodel = LogisticRegression()
    logmodel.fit(df[colName], df.answer, sample_weight=df.weight)
    predictions = logmodel.predict_proba(df_new[colName])
    
    predictedDF = pd.DataFrame({
        'word' : df_new.word,
        'prob' : [x[1] for x in predictions]
    })
    print(predictedDF)
    predictedDF = predictedDF[predictedDF.prob<0.95]
    
    recent_word = learningWordsDF.tail(5).word
    predictedDF = predictedDF.loc[~predictedDF.word.isin(recent_word)]
    
    n_pick = min(n , len(predictedDF))
    predictedNext = predictedDF.sort_values(by='prob')[:n_pick]
    
    if len(predictedNext)<n:
        newWords = list(set(allWords) - set(learningWordsDF.word))
        nNewWords = n-len(predictedNext)
        nNewWords = min(len(newWords), nNewWords)
        newWordsDF = pd.DataFrame({
            'word' : newWords[:nNewWords],
            'prob' : [np.NaN] * nNewWords
        })
        predictedNext = pd.concat([predictedNext, newWordsDF])
    
    return predictedNext




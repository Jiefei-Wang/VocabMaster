import pandas as pd


Dict_list = pd.DataFrame({
  'ecdict': {
    'language': 'zh-CN',
    'needs_update': False
  },
  'google':{
    'language': None,
    'needs_update': True
  },
  'dictionaryapi':{
    'language': 'EN',
    'needs_update': True
  }
})

allSources = list(Dict_list.keys())
Source = pd.Series(allSources, index=allSources)

class Annotation:
    definition = "definition"
    note = "note"

class defaultUserValue:
    glossaryBookName = 'mybook'
    exerciseBook = 'mybook'
    language = 'zh-CN'
    searchSource = Source.ecdict
    definitionSources = Source.ecdict + ',' + Source.dictionaryapi  + ',' + Source.google



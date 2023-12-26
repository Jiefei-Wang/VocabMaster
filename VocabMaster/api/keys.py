class Source:
    dictionaryapi = "dictionaryapi"
    google = "google"
    ecdict = "ecdict"
    PyDictionary = "PyDictionary"

class Annotation:
    definition = "definition"
    note = "note"

class defaultUserValue:
    glossaryBookName = 'mybook'
    exerciseBook = 'mybook'
    language = 'zh-CN'
    searchSource = Source.ecdict
    definitionSources = Source.ecdict + ',' + Source.PyDictionary + ',' + Source.dictionaryapi  + ',' + Source.google


allSources = [attr for attr in dir(Source) if not callable(getattr(Source, attr)) and not attr.startswith("__")]

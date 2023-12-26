class wordInfoHub{
    static wordInfo = {};
    static defined = {};
    
    static set(word, key, value){
        if (wordInfoHub.wordInfo[word]==undefined){
            wordInfoHub.wordInfo[word]={};
            wordInfoHub.defined[word] = {}
        }
        wordInfoHub.wordInfo[word][key]=value;
        wordInfoHub.defined[word][key]=true;
    }

    static get(word, key=null){
        if (key==null){
            return wordInfoHub.wordInfo[word];
        }
        if (!wordInfoHub.exists(word, key)){
            return undefined;
        }
        if (wordInfoHub.wordInfo[word] == undefined){
            return undefined;
        }
        return wordInfoHub.wordInfo[word][key];
    }

    static exists(word, key=null){
        if (wordInfoHub.defined[word]==undefined){
            return false;
        }
        if(key!=null){
            if (wordInfoHub.defined[word][key] !=true){
                return false;
            }
        }
        return true;
    }
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}


class requestUtils{
    static apiRequestTemplate(async=true){
        let req = new XMLHttpRequest();
        req.open('POST', baseUrl + 'api/jsonApi',async);
        req.setRequestHeader('Accept', 'application/json');
        req.setRequestHeader('Content-Type', 'application/json');
        const csrftoken = getCookie('csrftoken');
        req.setRequestHeader('X-CSRFToken', csrftoken);
        return req;
    }
    
    static jsonRequest(obj, callback = null, async = true){
        var obj_json = JSON.stringify(obj)
        var req = requestUtils.apiRequestTemplate();
        req.onload = ()=>{
            callback(req);
        };
        req.send(obj_json);
    }

    static handleRequestError(request){
        if (request.status != 200) { // analyze HTTP status of the response
            alert(`Error ${request.status}: ${request.statusText}`); // e.g. 404: Not Found
            return true;
        } 
        return false;
    }
}

class component{
    static wordItem(word, definition, backId){
        const template = document.getElementById('individual-word-template');
        var a = template.content.firstElementChild.cloneNode(true);
        a.setAttribute('onclick', "component.wordItemOnclick(this)");
        a.dataset.id = backId;
        a.dataset.word = word;


        var word_spell = a.querySelector("#individual-word-spell");
        word_spell.innerText = word;

        var explain = a.querySelector("#individual-word-explaination");
        explain.innerText = definition;

        return(a);
    }
    static wordItemOnclick(obj){
        WordPanel.backWindowId=obj.dataset.id;
        WordPanel.showWord(obj.dataset.word);
    }

    static getNavigationBar(){
        return document.getElementById('navigation-bar');
    }

    static getSpinner(){
        return document.getElementById('loading-spinner');
    }
}

class UserInfo{
    static user = undefined;
    static glossaryBook=undefined;
    static exerciseBook=undefined;
    static language=undefined;
    static searchSource=undefined;
    static definitionSouces=undefined;

    static isLoading = false;
    static is_authenticated(){
        return document.getElementById("is_authenticated").value == "True";
    }

    static updateUserInfo(){
        if(!UserInfo.is_authenticated()){
            UserInfo.isLoading = false;
            return;
        }
        if(UserInfo.isLoading){
            return;
        }
        UserInfo.isLoading = true;

        var jsonRequest = {
            'action' : 'getUserInfo'
        };
        requestUtils.jsonRequest(jsonRequest, (req) => {
            UserInfo.isLoading = false;
            if(requestUtils.handleRequestError(req)){
                return;
            }
            var jsonResponse = JSON.parse(req.responseText);
            this.user = jsonResponse['user'];
            this.glossaryBook = jsonResponse['glossaryBook'];
            this.exerciseBook = jsonResponse['exerciseBook'];
            this.language = jsonResponse['language'];
            this.searchSource = jsonResponse['searchSource'];
            this.definitionSouces = jsonResponse['detailSouces'];
        });
    }
}


class WordPronounce{
    static loading = {};
    static audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    static isLoading(word,region){
        var status = WordPronounce.loading[word+region];
        if(status == undefined){
            return false;
        }
        return status
    }
    static setLoadingStatus(word, region, isLoading){
        WordPronounce.loading[word+region] = isLoading;
    }

    static playWord(buttonDOM){
        var word = buttonDOM.dataset.word;
        var region = buttonDOM.dataset.region;
        WordPronounce.pronounce(word,region);
    }
    static pronounce(word, region){
        if (!wordInfoHub.exists(word, region + '-pronounce')){
            WordPronounce.loadPronounce(word, region);
        }
        if (WordPronounce.isLoading(word, region)){
            return setTimeout(()=>{return WordPronounce.pronounce(word, region)}, 100);
        }

        var decodedString = wordInfoHub.get(word,region + '-pronounce');
        const decodedBytes = new Uint8Array(decodedString.split('').map(char => char.charCodeAt(0)));
        var audioSource = WordPronounce.audioCtx.createBufferSource();
        WordPronounce.audioCtx.decodeAudioData(decodedBytes.buffer, (buffer) => {
            audioSource.buffer = buffer;
            audioSource.connect(WordPronounce.audioCtx.destination);
            },
      
            (err) => console.error(`Error with decoding audio data: ${err.err}`));
    
            // connect the AudioBufferSourceNode to the
            // destination so we can hear the sound
            audioSource.connect(WordPronounce.audioCtx.destination);
    
            // start the source playing
            audioSource.start();
    }

    static loadPronounce(word, region){
        if (WordPronounce.isLoading(word, region)){
            return;
        }
        WordPronounce.setLoadingStatus(word, region, true);
        var jsonRequest = {
            'action' : 'get',
            'target' :  'pronounce',
            'word' : word,
            'region': region
        };
        requestUtils.jsonRequest(jsonRequest, (req)=>{WordPronounce.loadPronounceCallback(req, word, region)});
    }

    static loadPronounceCallback(req, word, region){
        WordPronounce.setLoadingStatus(word, region, false);
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        const data = jsonResponse['data'];

        const decodedString = atob(data);
        wordInfoHub.set(word, region + '-pronounce', decodedString);
    }
}


class API{
    static searchWord(callback, word){
        var jsonRequest = {
            'action' : 'search',
            'word' :  word
        };
        
        requestUtils.jsonRequest(jsonRequest, callback)
    }

    static queryWordDefinitions(callback, word){
        var jsonRequest = {
            'action' : 'queryWordDefinitions',
            'word' :  word
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static getWordAnnotation(callback,word, type){
        var jsonRequest = {
            'target': 'wordAnnotation',
            'action' : 'get',
            'word' :  word,
            'type': type
        };
        requestUtils.jsonRequest(jsonRequest, callback);

    }
    static updateWordAnnotation(callback, word, type, data){
        var jsonRequest = {
            'target': 'wordAnnotation',
            'action' : 'update',
            'word' :  word,
            'type': type,
            'data': data
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static queryWordSoundmarks(callback, word){
        var jsonRequest = {
            'action' : 'queryWordSoundmarks',
            'word' :  word
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static findBookByWord(callback, word){
        var jsonRequest = {
            'action' : 'findBookByWord',
            'word': word
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static addGlossaryWord(callback, bookName, words){
        if (typeof(words)=='string'){
            words = [words];
        }
        var jsonRequest = {
            'target' : 'glossaryWord',
            'action' : 'add',
            'bookName': bookName,
            'words' :  words
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static deleteGlossaryWord(callback, bookName, word){
        var jsonRequest = {
            'target' : 'glossaryWord',
            'action' : 'delete',
            'bookName': bookName,
            'word' :  word
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    
    static queryGlossaryWord(callback, bookName){
        var jsonRequest = {
            'action' : 'query',
            'target' :  'glossaryWord',
            'bookName': bookName
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static getGlossaryBooks(callback){
        var jsonRequest = {
            'action' : 'get',
            'target' :  'glossaryBook'
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static addGlossaryBook(callback, bookName){
        var jsonRequest = {
            'action' : 'add',
            'target' :  'glossaryBook',
            'bookName' : bookName
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static deleteGlossaryBook(callback, bookName){
        var jsonRequest = {
            'action' : 'delete',
            'target' :  'glossaryBook',
            'bookName': bookName
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }


    static setDefaultGlossaryBook(callback, bookName){
        var jsonRequest = {
            'action' : 'setDefault',
            'target' :  'glossaryBook',
            'bookName': Glossary.currentBookName
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static showExerciseBookInfo(callback, bookName){
        var jsonRequest = {
            'action' : 'showInformation',
            'target' : 'exerciseBook',
            'bookName' : bookName
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }
    
    static setDefaultExerciseBook(callback, bookName){
        var jsonRequest = {
            'action' : 'set',
            'target' :  'exerciseBook',
            'bookName': bookName
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static queryExerciseWords(callback, bookName){
        var jsonRequest = {
            'action' : 'query',
            'target' :  'exerciseWords',
            'bookName': bookName
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }

    static addOrUpdateExerciseWord(callback, bookName, id, word, answerId, studyTime){
        const date = new Date();
        var jsonRequest = {
            'action' : 'addOrUpdate',
            'target' :  'exerciseWords',
            'bookName': bookName,
            'id': id,
            'word': word,
            'answer': answerId,
            'date': date,
            'studyTime': studyTime
        };
        requestUtils.jsonRequest(jsonRequest, callback);
    }
    
}


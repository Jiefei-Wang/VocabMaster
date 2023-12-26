class Exercise{
    /***********************
    Internal data
    ***********************/
    static answerMap = {
        'known':2,
        'fuzzy':1,
        'unknown': 0
    }

    static bookName = undefined;
    static words = [];
    // The answer for a word
    static answers = [];
    // The id that is used to identify an answer in the database
    // Used to change an existing answer
    static wordHistoryIds = [];
    //the index of the word that is showing to the user now
    static currentWordIdx = 0;

    //Calculate how long a word is shown to the user
    static wordShownTime = Date.now();

    /***********************
     data accessor function
    ***********************/
    static wordsLoading = false;
    static isLoading(){
        return Exercise.wordsLoading;
    }
    static setLoadingStatus(status){
        Exercise.wordsLoading = status;
    }

    static getCurrentIdx(){
        return Exercise.currentWordIdx;
    }
    static getWordCount(){
        return Exercise.words.length;
    }
    static getWordInfo(id){
        return Exercise.words[id];
    }
    static addWordsInfo(words, ids, probs){
        for(var i=0;i<words.length;i++){
            var word = {
                word : words[i],
                id : ids[i],
                prob : probs[i]
            }
            Exercise.words.push(word);
        }
    }
    static existsWord(id){
        return Exercise.words[id] != undefined;
    }

    static getAnswer(id){
        return Exercise.answers[id];
    }
    static setAnswer(id, value){
        Exercise.answers[id] = value;
    }
    static existsAnswer(id){
        return Exercise.answers[id] != undefined;
    }

    static getWordHistoryId(id){
        return Exercise.wordHistoryIds[id];
    }
    static setWordHistoryId(id, value){
        Exercise.wordHistoryIds[id] = value;
    }
    static existsWordHistoryId(id){
        return Exercise.wordHistoryIds[id] != undefined;
    }

    static getAnswerId(answer){
        return Exercise.answerMap[answer.toLowerCase()]
    }


    /***********************
     element accessor function
    ***********************/
    static getWordElement(){
        return document.getElementById("exercise-word");
    }

    static getSoundmarkPanelElement(){
        return document.getElementById("exercise-soundmark-panel");
    }

    static getAnswerElement(type){
        return document.getElementById(`exercise-answer-${type}`);
    }

    static getDefinitionPanelHideElement(){
        return document.getElementById("exercise-definition-panel-hide");
    }

    static getDefinitionPanelElement(){
        return document.getElementById("exercise-definition-panel");
    }

    static getDefinitionElement(){
        return document.getElementById("exercise-definition");
    }

    static getNoteElement(){
        return document.getElementById("exercise-note");
    }

    static getNoteTitleElement(){
        return document.getElementById("exercise-note-title");
    }
    /***********************
     button control
    ***********************/
    static unhighlightButton(type){
        var elt = Exercise.highlightButton(type);
        var className = elt.className;
        className = className.replace("btn-","btn-outline-");
        elt.setAttribute("class", className);
        return elt;
    }
    
    static highlightButton(type){
        var elt = Exercise.getAnswerElement(type);
        var className = elt.className;
        className = className.replace("-outline","");
        elt.setAttribute("class", className);
        return elt;
    }

    static selectButton(answer){
        var buttonTypes = ['known','unknown','fuzzy'];
        for (var type of buttonTypes){
            Exercise.unhighlightButton(type);
        }
        if (buttonTypes.includes(answer)){
            Exercise.highlightButton(answer);
        }
    }

    
    /***********************
     utilities
    ***********************/
    static clearAllData(){
        Exercise.words=[];
        Exercise.answers=[];
        Exercise.wordHistoryIds=[];
        Exercise.currentWordIdx = 0;
    }

    
    static nextWord(offset){
        const maxLoad = 1;
        var idx = Exercise.getCurrentIdx();
        // Aloow 1 unanswered word at most
        const undefinedCount = idx + offset - Exercise.answers.filter(x => x !== undefined).length;
        if (undefinedCount>=maxLoad){
            return;
        }

        if(idx + offset<0){
            return;
        }
        //update existing answer
        //Exercise.uploadAnswer(idx);

        Exercise.currentWordIdx = idx + offset;
        Exercise.showCard();
    }


    
    /***********************
     Main functions
    ***********************/
     static loadPanel(bookName = null){
        if (bookName != null) {
            if (Exercise.bookName != bookName) {
                Exercise.clearAllData();
            }
            Exercise.bookName = bookName;
        }
        Exercise.showCard();
    }

    static showCard(){
        var idx = Exercise.getCurrentIdx();
        if(idx>= Exercise.words.length){
            Exercise.loadWords();
            return setTimeout(()=>{
                return Exercise.showCard()
            }, 100);
        }

        // Reset the timer;
        Exercise.wordShownTime = Date.now();
        var info = Exercise.getWordInfo(idx);
        var word = info.word;
        var title = Exercise.getWordElement();
        title.innerText = word;
        title.dataset.idx = idx;

        Exercise.showSoundmark(idx);
        if (Exercise.existsAnswer(idx)){
            Exercise.showDefinition(idx);
        }else{
            Exercise.showWaitingInfoInDefinition(idx);
        }

        Exercise.showAnswerButton(idx);
    }

    static showSoundmark(idx){
        var info = Exercise.getWordInfo(idx);
        var word = info.word;

        if(idx!= Exercise.getCurrentIdx()){
            return;
        }
        if(!wordInfoHub.exists(word, 'US')){
            return setTimeout(()=>{return Exercise.showSoundmark(idx)}, 100);
        }
        
        var panel = Exercise.getSoundmarkPanelElement();
        panel.innerHTML = '';
        for(var i=0;i<Keys.soundMarkRegions.length;i++){
            var region = Keys.soundMarkRegions[i];
            var soundmark = wordInfoHub.get(word, region)
            var sm = WordPanel.createSoundmarkElement(word, region, soundmark);
            sm.setAttribute('class', 'btn btn-sm btn-light')
            panel.append(sm);
            //Pronunce the word
            if(region=="US"){
                WordPronounce.playWord(sm);
            }
        }
    }

    static showDefinition(idx){
        var info = Exercise.getWordInfo(idx);
        var word = info.word;
        if(idx!= Exercise.getCurrentIdx()){
            return;
        }
        
        if(!wordInfoHub.exists(word, 'exercise-def')){
            return setTimeout(()=>{return Exercise.showDefinition(idx)}, 100);
        }

        Exercise.getDefinitionPanelHideElement().hidden=true;
        Exercise.getDefinitionPanelElement().hidden=false;

        //Add definition
        //If the custom definition exists, then use the custom one
        //Otherwise, use default definition
        var definition = wordInfoHub.get(word, 'exercise-custom-def');
        if(definition==""){
            definition = wordInfoHub.get(word, 'exercise-def');
        }
        var definitionElt = Exercise.getDefinitionElement();
        definitionElt.innerText = definition;

        // Add note
        var note = wordInfoHub.get(word, 'exercise-note');
        if(note!=""){
            Exercise.getNoteTitleElement().hidden=false;
            var noteElt = Exercise.getNoteElement();
            noteElt.innerText = note;
        }else{
            Exercise.getNoteTitleElement().hidden=true;
        }

        //defintionElt.dataset.idx = idx;
        //defintionElt.dataset.isShown = true;
    }
    
    static showWaitingInfoInDefinition(idx){
        Exercise.getDefinitionPanelHideElement().hidden=false;
        Exercise.getDefinitionPanelElement().hidden=true;
        //var definitionElt = Exercise.getDefinitionElement();
       //definitionElt.dataset.idx = idx;
        //definitionElt.dataset.isShown = false;
    }

    static showAnswerButton(idx){
        //Remove the answer selection first
        var answer = Exercise.getAnswer(idx);
        var buttonTypes = ['known','unknown','fuzzy'];
        for (var type of buttonTypes){
            var elt = Exercise.getAnswerElement(type);
            elt.dataset.idx = idx;
        }
        // If no answer is selected, this will unhighlight all
        Exercise.selectButton(answer);
    }


    static loadWords(){
        if(Exercise.isLoading()){
            return;
        }
        if (Exercise.bookName==undefined){
            throw new Error('bookName is undefined');
        }
        API.queryExerciseWords(Exercise.loadWordsCallback, Exercise.bookName);
        Exercise.setLoadingStatus(true);
    }
    
    static loadWordsCallback(req){
        Exercise.setLoadingStatus(false);
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        var source = jsonResponse['source'];
        var wordslist = jsonResponse['words'];

        var words =  wordslist['words'];
        var ids = wordslist['ids']
        var probs = wordslist['probs']
        Exercise.addWordsInfo(words, ids, probs);

        var definitions = wordslist[source];
        var customDefinitions = wordslist["customDefinition"];
        var notes = wordslist["note"];
        var US = wordslist['US'];
        var UK = wordslist['UK'];
        
        for(var i =0;i<words.length;i++){
            var word = words[i];
            var def = definitions[i];
            var customDef = customDefinitions[i];
            var note = notes[i];
            wordInfoHub.set(word, 'exercise-def', def);
            wordInfoHub.set(word, 'exercise-custom-def', customDef);
            wordInfoHub.set(word, 'exercise-note', note);
            wordInfoHub.set(word, 'UK', UK[i]);
            wordInfoHub.set(word, 'US', US[i]);
        }
    }
   
    static knownWordTimer;
    static selectAnswer(buttonDOM){
        var idx = Exercise.getCurrentIdx();
        var existsAnswer = Exercise.existsAnswer(idx);
        var answer = buttonDOM.innerText.toLowerCase();

        // update data
        Exercise.showDefinition(idx);
        Exercise.selectButton(answer)
        Exercise.setAnswer(idx, answer)

        // upload answer and show next question
        clearTimeout(Exercise.knownWordTimer);
        if (answer == 'known' && !existsAnswer){
            Exercise.knownWordTimer = setTimeout(() => {
                Exercise.nextWord(1);
            }, 1500);
        }else{
            Exercise.uploadAnswer(idx);
        }
    }

    // upload the answer, if answer exists, then update answer
    static uploadAnswer(idx){
        // We must at least have the answer
        if (!Exercise.existsAnswer(idx)){
            return
        }
        var info = Exercise.getWordInfo(idx);
        var word = info.word
        var id = info.id

        var answer = Exercise.getAnswer(idx);
        var answerId = Exercise.getAnswerId(answer);
        var timeInSeconds = (Date.now() - Exercise.wordShownTime)/1000;
        API.addOrUpdateExerciseWord((req)=>{
            if(requestUtils.handleRequestError(req)){
                return;
            }
            var jsonResponse = JSON.parse(req.responseText);
            Exercise.setWordHistoryId(idx, jsonResponse['id']);
        }, Exercise.bookName, id, word, answerId, timeInSeconds);
    }


    // If the word is clicked
    static wordOnclick(obj){
        WordPanel.backWindowId=Panels.exercise;
        var info = Exercise.getWordInfo(Exercise.getCurrentIdx());
        var word = info.word;
        WordPanel.showWord(word);
    }

    // If the definition is clicked
    static definitionOnclick(obj){
        var idx = Exercise.getCurrentIdx();
        var isShown = obj.dataset.isShown;
        if(isShown == 'true'){
            Exercise.showWaitingInfoInDefinition(idx);
        }else{
            Exercise.showDefinition(idx);
        }
    }
}
class WordPanel {
    static workingOn = '';
    // Which window needs to be shown when the back button has been clicked? 
    static backWindowId = null;

    // Obtain a HTML component
    static getStarElement(){
        return document.getElementById("glossary-star");
    }
    static getTitleElement(){
        return document.getElementById("word-head");
    }
    static getGlossaryElement(){
        return document.getElementById("glossary-name");
    }
    static getWordDefinitionsPanelElement(){
        return document.getElementById("word-definitions-panel");
    }

    static getWordSoundmarksPanelElement(){
        return document.getElementById("word-soundmarks-panel");
    }
    
    static getCustomDefinitionBoxElement(){
        return document.getElementById("custom-definition-box");
    }
    static getCustomConfirmButtonElement(){
        return document.getElementById("custom-confirm-button");
    }
    
    static getAnnotationElement(type){
        var element_id;
        if (type == "definition"){
            element_id = 'word-custom-definition-panel';
        }else{
            element_id = "word-custom-note-panel";
        }
        return document.getElementById(element_id);
    }
    static getAnnotationTextElement(type){
        var element_id;
        if (type == "definition"){
            element_id = "word-custom-definition";
        }else{
            element_id = "word-custom-note";
        }
        return document.getElementById(element_id);
    }

    static cleanAnnotation(){
        if (UserInfo.is_authenticated()) {
            WordPanel.getAnnotationElement(Keys.customDefinition).hidden = false;
            var elt = WordPanel.getAnnotationTextElement(Keys.customDefinition);
            elt.innerHTML = "";
            WordPanel.getAnnotationElement(Keys.customNote).hidden = false;
            var elt = WordPanel.getAnnotationTextElement(Keys.customNote);
            elt.innerHTML = "";
        }else{
            WordPanel.getAnnotationElement(Keys.customDefinition).hidden = true;
            WordPanel.getAnnotationElement(Keys.customNote).hidden = true;
        }
    }

    static cleanDefinition(){
        var wordPanel = WordPanel.getWordDefinitionsPanelElement();
        wordPanel.innerHTML="";

    }


    static createSoundmarkElement(word, region, soundmark){
        const template = document.getElementById('word-soundmark-template');
        var obj = template.content.firstElementChild.cloneNode(true);
        if (soundmark==undefined){
            obj.innerText = region;
        }else{
            obj.innerText = region + ": [" + soundmark + "]";
        }
        obj.dataset.word = word;
        obj.dataset.region = region;
        return obj;
    }

    static createWordDetailElement(source, definition){
        const template = document.getElementById('word-definition-template');
        var obj = template.content.firstElementChild.cloneNode(true);
        var headElt = obj.querySelector("#source-head-template");
        headElt.innerText = source;

        if(source == Keys.customDefinition||source == Keys.customNote){
            headElt.innerHTML = headElt.innerHTML+
            `<button style="float: right;" data-bs-toggle="modal" data-bs-target="#custom-modal" data-source="${source}" onclick="WordPanel.editOnclick(this)">Edit</button>`;
        }

        var definitionElt=obj.querySelector("#source-definition-template");
        definitionElt.innerText = definition;
        definitionElt.dataset.type = `definition-${source}`;
        return obj;
    }

    static displayGlossaryStar(display){
        WordPanel.getGlossaryElement().hidden=!display;
        WordPanel.getStarElement().hidden=!display;
    }


    static showWord(word){
        showPanel(Panels.wordPanel);

        var spinner = component.getSpinner();
        spinner.hidden=false;
        
        //Clear the screen
        WordPanel.cleanAnnotation();
        WordPanel.cleanDefinition();

        // Word title and glossary
        WordPanel.updateHead(word);
        WordPanel.displayGlossaryStar(true);
        /* 
        If user has multiple calls, this will make sure only
        the last call  will take effect
        */
        WordPanel.workingOn = word;
        
        // Get the word definition
        API.queryWordDefinitions(WordPanel.wordDefinitionsCallback, word);

        // Get custom definition
        WordPanel.cleanAnnotation();
        if (UserInfo.is_authenticated()) {
            API.getWordAnnotation(WordPanel.wordAnnotationCallback, word, Keys.customDefinition);
            API.getWordAnnotation(WordPanel.wordAnnotationCallback, word, Keys.customNote);
        }

        // Get the word soundmark
        API.queryWordSoundmarks(WordPanel.wordSoundMarkCallback, word);

        if (UserInfo.is_authenticated()){
            // Check if the word has been added into a glossary book
            API.findBookByWord(WordPanel.glossaryCallback, word);
        }else{
            WordPanel.displayGlossaryStar(false);
        }
    }

    static wordDefinitionsCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        var word = jsonResponse['word'];
        var sources = jsonResponse['sources'];
        if (WordPanel.workingOn!=word)
            return;

        var wordPanel = WordPanel.getWordDefinitionsPanelElement();
        wordPanel.innerHTML='';
        for(var i=0;i<sources.length;i++){
            var source = sources[i];
            var content = jsonResponse[source];
            if(content!=null){
                var obj = WordPanel.createWordDetailElement(source, jsonResponse[source]);
                wordPanel.append(obj);
            }
        }
        
        var spinner = component.getSpinner();
        spinner.hidden=true;
    }

    
    static wordAnnotationCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        var word = jsonResponse['word'];
        var data = jsonResponse['data'];
        var type = jsonResponse['type'];
        if (WordPanel.workingOn!=word)
            return;

        var wordPanel = WordPanel.getAnnotationTextElement(type);
        wordPanel.innerText=data;
    }


    static wordSoundMarkCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        var word = jsonResponse['word'];
        var regions = jsonResponse['regions'];
        if (WordPanel.workingOn!=word)
            return;

        var soundmarksPanel = WordPanel.getWordSoundmarksPanelElement();
        soundmarksPanel.innerHTML='';
        for(var i=0;i<Keys.soundMarkRegions.length;i++){
            var region = Keys.soundMarkRegions[i];
            var obj = WordPanel.createSoundmarkElement(word, region, jsonResponse[region]);
            soundmarksPanel.append(obj);
        }
    }

    static glossaryCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        var book = jsonResponse['book'];
        WordPanel.updateGlossary(book);
    }

    // Show the word in the header
    static updateHead(word){
        var elt = WordPanel.getTitleElement();
        elt.innerText = word;
    }

    static updateGlossary(bookName){
        WordPanel.updateGlossaryName(bookName);
        WordPanel.updateGlossaryStatus(bookName);

        
    }
    static updateGlossaryName(bookName){
        var elt = WordPanel.getGlossaryElement();
        elt.innerText = bookName;
    }
    // Show the little start to show if the word is in glossary
    static updateGlossaryStatus(bookName){
        var star = WordPanel.getStarElement();
        if (bookName==null){
            star.setAttribute("class", "bi-star");
            star.style.color = "black";
            star.dataset.bookName = "";
        }else{
            star.setAttribute("class", "bi-star-fill");
            star.style.color = "rgb(255, 191, 0)";
            star.dataset.bookName = bookName;
        }
    }
    
    static addOrRemoveWordFromGlossary(){
        var title = WordPanel.getTitleElement();
        var word = title.innerHTML;

        var star = WordPanel.getStarElement();
        var bookName = star.dataset.bookName;
        if (bookName == ''){
            API.addGlossaryWord(WordPanel.addOrRemoveCallback, undefined, word);
        }else{
            API.deleteGlossaryWord(WordPanel.addOrRemoveCallback, bookName, word);
        }
    }




    static addOrRemoveCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        var action = jsonResponse['action']
        var bookName = jsonResponse['bookName']

        if(action == "add"){
            WordPanel.updateGlossary(bookName)
        }else{
            WordPanel.updateGlossary(null);
        }
    }


    static backOnclick(){
        var spinner = component.getSpinner();
        spinner.hidden=true;
        if (WordPanel.backWindowId==null){
            showPanel(Panels.home, false);
        }else{
            showPanel(WordPanel.backWindowId, false);
            WordPanel.backWindowId = null;
        }
    }

    static editOnclick(type){
        if(!UserInfo.is_authenticated()){
            return;
        }
        var textDOM = WordPanel.getAnnotationTextElement(type);

        var box = WordPanel.getCustomDefinitionBoxElement();
        box.value = textDOM.innerText;
        
        var confirmButton = WordPanel.getCustomConfirmButtonElement();
        confirmButton.dataset.type = type;
    }

    static customConfirmOnclick(buttonDOM){
        if(!UserInfo.is_authenticated()){
            return;
        }
        var type = buttonDOM.dataset.type;
        var meaning = WordPanel.getCustomDefinitionBoxElement().value;
        var word = WordPanel.getTitleElement().innerText;

        var textDOM = WordPanel.getAnnotationTextElement(type);
        textDOM.innerText = meaning;
        API.updateWordAnnotation((req)=>{
            if(requestUtils.handleRequestError(req)){
                return;
            }
        }, word,type,meaning);
    }
}




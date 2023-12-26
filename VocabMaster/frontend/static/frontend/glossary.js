class Glossary{
    static currentBookName=null;
    // word cache
    static wordslist;
    static addDates;
    static definitions;

    static getNewBookNameElement(){
        return document.getElementById("new-book-name");
    }
    static getWordsPanelElement(){
        return document.getElementById("glossary-book-words");
    }
    static getGlossaryBookListElement(){
        return document.getElementById("glossary-book-list");
    }
    static getCurrentBookElement(){
        return document.getElementById("glossary-current-book-name");
    }
    static getDeleteMessageElement(){
        return document.getElementById("glossary-delete-book-name");
    }
    static getBatchAddBox(){
        return document.getElementById("batch-add-box");
    }


    static createGlossaryBookItems(bookName){
        const template = document.getElementById('glossary-book-template');
        var obj = template.content.firstElementChild.cloneNode(true);

        var circle = obj.querySelector("#glossary-book-name-circle");
        circle.id = `glossary-book-name-${bookName}`;
        if(bookName == Glossary.currentBookName){
            circle.checked = true;
        }

        var item = obj.querySelector("#glossary-book-name-template");
        if (bookName == UserInfo.glossaryBook){
            item.innerText = bookName + ' (default)';
        }else{
            item.innerText = bookName;
        }

        item.dataset.bookName = bookName;
        item.setAttribute('for', circle.id);

        return obj;
    }

    static loadPanel(reload=false){
        if(!UserInfo.is_authenticated()){
            return;
        }
        if(reload){
            UserInfo.updateUserInfo();
        }

        if (UserInfo.isLoading){
            return setTimeout(()=>{
                return Glossary.loadPanel();
            }, 100);
        }

        Glossary.loadBooksList();
        if(Glossary.currentBookName==null){
            Glossary.currentBookName = UserInfo.glossaryBook;
        }
        Glossary.setCurrentBook(Glossary.currentBookName);
    }

    static changeBook(bookDOM){
        var bookName = bookDOM.dataset.bookName;
        var elt = Glossary.getDeleteMessageElement();
        const modalBody = 'Are you sure you want to delete the book ' + bookName + '?';
        elt.innerHTML = modalBody;

        Glossary.setCurrentBook(bookName);
    }
    

    static setCurrentBook(bookName){
        Glossary.currentBookName = bookName;
        API.queryGlossaryWord(Glossary.setCurrentBookCallback, bookName);
    }

    static setCurrentBookCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        Glossary.getWordsPanelElement().innerHTML = '';
        var jsonResponse = JSON.parse(req.responseText);
        var wordslist = jsonResponse['words'];
        var bookName = jsonResponse['bookName'];
        var source = jsonResponse['source']

        var words =  wordslist['words']
        var definitions = wordslist[source]
        for(var i=0; i<words.length; i++){
            var obj = component.wordItem(words[i], definitions[i], Panels.glossary);
            Glossary.getWordsPanelElement().appendChild(obj);
        }
        Glossary.bookLoaded=true;
        //Set current book name
        Glossary.getCurrentBookElement().innerText = bookName;
    }

    static loadBooksList(){
        API.getGlossaryBooks(Glossary.loadBooksListCallback);
    }

    static loadBooksListCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var elt = Glossary.getGlossaryBookListElement();
        elt.innerHTML = '';
        var jsonResponse = JSON.parse(req.responseText);
        var booksList = jsonResponse['books'];
        for(var i=0;i<booksList.length;i++){
            var obj = Glossary.createGlossaryBookItems(booksList[i]);
            elt.append(obj);
        }
    }

    static addNewbook(){
        var obj = Glossary.getNewBookNameElement();
        var bookName = obj.value;
        if(bookName.length==0)
            return;
        obj.value="";

        API.addGlossaryBook((req) => {
            if(requestUtils.handleRequestError(req)){
                return;
            }
            Glossary.loadBooksList();
        }, bookName);
    }

    static deleteBook(){
        API.deleteGlossaryBook((req) => {
            if(requestUtils.handleRequestError(req)){
                return;
            }
            Glossary.currentBookName = null;
            Glossary.loadPanel(reload=true);
        }, Glossary.currentBookName);
    }

    static setDefaultBook(){
        API.setDefaultBook((req) => {
            if(requestUtils.handleRequestError(req)){
                return;
            }
            UserInfo.glossaryBook = Glossary.currentBookName;
            Glossary.loadBooksList();
        }, Glossary.currentBookName);
    }

    static batchAdd(){
        var elt = Glossary.getBatchAddBox();
        var text = elt.value;
        var words = text.split("\n");
        const updatedWrds = words.map(element => element.trim()).filter(element => element !== '');
        if(Glossary.currentBookName==null || updatedWrds.length==0){
            return;
        }
        API.addGlossaryWord((req)=>{
            if(requestUtils.handleRequestError(req)){
                return;
            }
            elt.value='';
            Glossary.setCurrentBook(Glossary.currentBookName);
        }, Glossary.currentBookName, 
        updatedWrds);
    }
}


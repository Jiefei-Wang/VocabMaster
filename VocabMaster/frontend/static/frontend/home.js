class SearchBar {
    static displayedWord = '';
    // The word that is currently being searched
    // If received a response with a word that is different from this, the response will be ignored
    static searchingWord = '';
    static resultsList;

    static getSearchBoxElement(){
        return document.getElementById('word_search_box');
    }
    static getSearchResultElement(){
        return document.getElementById('word_search_results');
    }

    static update(){
        var resultsList = this.getSearchResultElement();
        const word = this.getSearchBoxElement().value;
        // If the word is empty, clear the results
        if (word.length ==0) {
            resultsList.innerHTML = '';
            this.displayedWord='';
            this.searchingWord='';
            return;
        }
        if (this.searchingWord == word || this.displayedWord == word) {
            return;
        }
        this.searchingWord = word;
        this.searchWord(word);
    }
   //static variable defined
    static searchTimer;
    static searchWord(word){
        clearTimeout(SearchBar.searchTimer);
        SearchBar.searchTimer = 
        setTimeout(()=>{API.searchWord(SearchBar.searchWordCallback, word);}, 300);
    }

    static searchWordCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        var searchedWord = jsonResponse['searchedWord'];
        var wordslist = jsonResponse['words'];
        var definitions = jsonResponse['definitions'];

        var resultsList = SearchBar.getSearchResultElement();
        if (searchedWord == SearchBar.searchingWord ) {
            resultsList.innerHTML = '';
            for(var i=0;i<wordslist.length;i++){
                var obj = component.wordItem(wordslist[i], definitions[i], Panels.home);
                resultsList.appendChild(obj);
            }
            SearchBar.displayedWord = searchedWord;
            SearchBar.searchingWord = '';
        }
    }
}


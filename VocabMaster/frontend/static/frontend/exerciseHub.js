class ExerciseHub{
    static bookName = undefined;
    static exercising = false;

    static getBookNameElement(){
        return document.getElementById("exerciseHub-book-name");
    }
    static getBookInfoPanelElement(){
        return document.getElementById("exerciseHub-book-information-panel");
    }
    
    static getProgressElement(){
        return document.getElementById("exerciseHub-progress");
    }
    
    static getBookListPanelElement(){
        return document.getElementById("exerciseHub-book-list-panel");
    }

    static createBookInformation(key, value){
        const template = document.getElementById('exerciseHub-information-template');
        var obj = template.content.firstElementChild.cloneNode(true);
        obj.innerText = `${key}: ${value}`;
        return obj;
    }

    static createBookNameElementInList(bookName){
        const template = document.getElementById('exerciseHub-book-template');
        var obj = template.content.firstElementChild.cloneNode(true);
        obj.innerText = bookName;
        return obj;
    }
    
    static loadPanel(){
        if(!UserInfo.is_authenticated()){
            return;
        }
        var jsonRequest = {
            'action' : 'get',
            'target' :  'exerciseBook'
        };
        requestUtils.jsonRequest(jsonRequest, ExerciseHub.loadPanelCallback);
    }
    
    static loadPanelCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        ExerciseHub.bookName = jsonResponse['bookName'];
        var obj = ExerciseHub.getBookNameElement();
        obj.innerText = ExerciseHub.bookName;
        ExerciseHub.loadBookInformation();
    }

    static loadBookInformation(){
        if(!UserInfo.is_authenticated()){
            return;
        }
        API.showExerciseBookInfo(ExerciseHub.loadBookInformationCallback, ExerciseHub.bookName);
    }

    static loadBookInformationCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);
        var panel = ExerciseHub.getBookInfoPanelElement();
        panel.innerHTML = '';
        var keys = ['learning', 'not learned', 'total'];
        for (const key of keys) {
            var obj = ExerciseHub.createBookInformation(key, jsonResponse[key]);
            panel.append(obj);
        }

        ExerciseHub.setProgress(jsonResponse['learning']/jsonResponse['total']*100);
    }

    static setProgress(percent){
        var obj = ExerciseHub.getProgressElement();
        obj.style.width = `${percent}%`;
    }

    static loadBookList(){
        API.getGlossaryBooks(ExerciseHub.loadBookListCallback);
    }
    
    static loadBookListCallback(req){
        if(requestUtils.handleRequestError(req)){
            return;
        }
        var jsonResponse = JSON.parse(req.responseText);

        var bookNames = jsonResponse['books'];
        var panel = ExerciseHub.getBookListPanelElement();
        panel.innerHTML='';
        for (const bookName of bookNames){
            var obj = ExerciseHub.createBookNameElementInList(bookName);
            panel.append(obj);
        }
    }

    static setBook(bookDOM){
        var bookName = bookDOM.innerText;
        API.setDefaultExerciseBook((req) => {
            if(requestUtils.handleRequestError(req)){
                return;
            }
            ExerciseHub.loadPanel();
        }, bookName);
    }

    static startExercise(isStart){
        ExerciseHub.exercising = isStart;
        if(isStart){
            Exercise.loadPanel(ExerciseHub.bookName);
            showPanel('exercise');
        }else{
            showPanel('exerciseHub');
        }
    }
}
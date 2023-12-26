const baseUrl = window.location.origin+'/';

var id = JSON.parse(document.getElementById('user_id').textContent);

class Keys {
    static soundMarkRegions = ['US', 'UK'];
    static dictionaryapi = "dictionaryapi";
    static ecdict = "ecdict";
    static google = "google";
    static customDefinition = "definition";
    static customNote = "note";
    static US = "US";
    static UK = "UK";
    static AU = "AU";
}


class Panels{
    static home = 'home';
    static wordPanel = 'wordPanel';
    static glossary = 'glossary';
    static exercise = 'exercise';
    static exerciseHub = 'exerciseHub';
}

window.onload = function () {
    UserInfo.updateUserInfo();
    showPanel('home');
}

function showPanel(id, load = true) {
    document.querySelectorAll(".mainPanel").forEach(element => {
        element.style.display = "none";
    });
    document.getElementById(id).style.display = "block";


    if(load){
        if (id == "glossary"){
            Glossary.loadPanel(reload=true);
        }
        if(id == "exerciseHub"){
            ExerciseHub.loadPanel();
        }
        if (id == "exercise"){
            Exercise.loadPanel();
        }
    }
}


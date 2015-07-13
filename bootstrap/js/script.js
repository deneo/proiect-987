$(document).on("click", "a", function () {

    // get the href attribute
    var newUrl = $(this).attr("href");

    // veryfy if the new url exists or is a hash
    if (!newUrl || newUrl[0] === "#") {
        // set that hash
        location.hash = newUrl;
        return;
    }

    // now, fadeout the html (whole page)
    $("html").fadeOut(function () {
        // when the animation is complete, set the new location
        location = newUrl;
    });

    // prevent the default browser behavior.
    return false;
});

var chosen = -1;

var choose = function(id) {
	if (id == chosen) return;
	var classes1 = document.getElementById("choice" + id).getAttribute("class");
	if (chosen != -1) document.getElementById("choice" + chosen).setAttribute("class", classes1);
	document.getElementById("choice" + id).setAttribute("class", classes1 + " user-choice");
	chosen = id;
}

var themes = {
    "default": "//netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css",
    "amelia" : "//bootswatch.com/amelia/bootstrap.min.css",
    "cerulean" : "//bootswatch.com/cerulean/bootstrap.min.css",
    "cosmo" : "//bootswatch.com/cosmo/bootstrap.min.css",
    "cyborg" : "//bootswatch.com/cyborg/bootstrap.min.css",
    "flatly" : "//bootswatch.com/flatly/bootstrap.min.css",
    "journal" : "//bootswatch.com/journal/bootstrap.min.css",
    "readable" : "//bootswatch.com/readable/bootstrap.min.css",
    "simplex" : "//bootswatch.com/simplex/bootstrap.min.css",
    "slate" : "//bootswatch.com/slate/bootstrap.min.css",
    "spacelab" : "//bootswatch.com/spacelab/bootstrap.min.css",
    "united" : "//bootswatch.com/united/bootstrap.min.css"
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

$(function(){
   var x = readCookie("tema");
   console.log(x);
   var themesheet = $('<link href="'+themes[x]+'" rel="stylesheet" />');
    themesheet.appendTo('head');
    $('.theme-link').click(function(){
       var themeurl = themes[$(this).attr('data-theme')]; 
        themesheet.attr('href',themeurl);
        document.cookie = "tema = " + $(this).attr('data-theme') + "; path=/;";
    });
});


//main.js
var buttons = document.getElementsByClassName("copybutton");
for (var button in buttons) {
    var clip = new ZeroClipboard(button, {
        moviePath: "static/js/ZeroClipboard.swf"
    });
    clip.on("load", function (client) {
        // alert( "movie is loaded" );

        client.on("complete", function (client, args) {
            // `this` is the element that was clicked
            this.style.color = "#9999FF";
            alert("Copied text to clipboard: " + args.text);
        });
    });
}

$(function() {
  $('#submit_query').bind('click', function() {
    $.post('history', {
      search_term: $('input[name="search_term"]').val()
    }, function(data) {
      $("#shortened_history").html(data.result);
    });
    return false;
  });
});

function form_validation() {

    var letters = /^[a-zA-Z0-9]+$/;
    var result = letters.test(document.getElementById('alias').value);

    if (document.getElementById('url').value == "") {
        alert("Please provide a non-empty string");
        document.getElementById('url').focus();
        return false;
    }
    //if (document.getElementById('alias').value == "") {
    //    alert("Please provide a non-empty string as alias");
    //    document.getElementById('alias').focus();
    //    return false;
    //}
    //if (result == false) {
    //    alert("Please provide 'letters only' string for alias");
    //    document.getElementById('alias').focus();
    //    return false;
    //}

    return true;
}
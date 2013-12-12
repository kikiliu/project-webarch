
 //main.js
 var clip = new ZeroClipboard( document.getElementById("copyText"), {
 } );

 clip.on( "load", function(client) {
   // alert( "movie is loaded" );

     client.on( "complete", function(client, args) {
         // `this` is the element that was clicked
             this.style.color = "9999FF";
                 alert("Copied text to clipboard: " + args.text );
                   } );
                   } );


                   


function form_validation()
{
	
	var letters = /^[a-zA-Z]+$/;
	var result = letters.test(document.getElementById('alias').value);

   	if( document.getElementById('url').value == "" )
   	{
     		alert( "Please provide a non-empty string" );
     		document.getElementById('url').focus() ;
     		return false;
   	}
   	if( document.getElementById('alias').value == "")
   	{
     		alert( "Please provide a non-empty string as alias" );
     		document.getElementById('alias').focus() ;
     		return false;	
   	}
   	if( result == false ) 
   	{
     		alert( "Please provide 'letters only' string for alias" );
     		document.getElementById('alias').focus() ;
     		return false;
   	}		

	return(true);

}










function setCookie(title, value, exdays){
	var exdata = new Date();
	exdate.setDate(exdate.getDate()+exdays);
	var c_value = escape(value) + ((exdays==null)) ? "" : "; expires="+exdate.toUTCString());
	document.cookie = title + "=" + value + "; path=/server";	
}

function getCookie(title){
	var
}

function deleteCookie(name){
	setCookie(name, "", -1);
}
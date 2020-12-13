function dC(name) {
	get_card_image(name, "card-image");
	document.getElementById("card-modal").style.display = "block";
}

function hC(name) {
	if (window.matchMedia("(hover: none)").matches) {
		return
	}
	get_card_image(name, "card-hover-image");
	document.getElementById("card-hover").style.display = "block";
}

function oC() {
	document.getElementById("card-hover").style.display = "none";
}

function sC(name, target) {
	if (document.getElementById(target).src == "") {
		console.log("Chargement de l'image : "+name+" sur "+target);
		get_card_image(name, target, "small");
	}
	console.log(name+" chargée");
}

/**/

var latitude = 40.633258
var longitude = -8.659097

/*
function showPosition(position){
	latitude = position.coords.latitude;
	longitude = position.coords.longitude;	
	$("#location").html(latitude+" "+longitude);
}

$(document).ready(function() {
	navigator.geolocation.getCurrentPosition(showPosition);
});
*/

var map = new L.Map("mapa", {center: [latitude, longitude], zoom: 15});

var osmUrl="http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
var osmAttrib="Map data  OpenStreetMap contributors";
var osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});		

map.addLayer(osm);

map.on("click", mostraCoordenadas);

function mostraCoordenadas(e){
  var s = document.getElementById("coordenadas");
  s.innerHTML = "Latitude, Longitude = "+e.latlng.lat+", "+e.latlng.lng;
}


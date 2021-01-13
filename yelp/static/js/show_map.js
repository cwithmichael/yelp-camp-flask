(function () {
    'use strict'
    mapboxgl.accessToken = 'pk.eyJ1IjoiY3dpdGhtaWNoYWVsIiwiYSI6ImNranUwemQwbjIxMWoyemszbDBvanJwN3kifQ.VTh7EYZxcDESBYUWoh35yw';
    var map = new mapboxgl.Map({
	container: 'map',
	style: 'mapbox://styles/mapbox/streets-v11',
	center: camp_location,
	zoom: 9
    });
    new mapboxgl.Marker()
	.setLngLat(camp_location)
	.setPopup(
	    new mapboxgl.Popup({offset: 25})
		.setHTML(
		    `<h3>${camp_title}</h3>`
		)
	)
	.addTo(map)

})();

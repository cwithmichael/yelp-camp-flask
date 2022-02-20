(function () {
	'use strict'
	mapboxgl.accessToken = document.currentScript.getAttribute("tok");
	var map = new mapboxgl.Map({
		container: 'show-map',
		style: 'mapbox://styles/mapbox/streets-v11',
		center: camp_location,
		zoom: 9
	});
	map.addControl(new mapboxgl.NavigationControl());
	new mapboxgl.Marker()
		.setLngLat(camp_location)
		.setPopup(
			new mapboxgl.Popup({ offset: 25 })
				.setHTML(
					`<h3>${camp_title}</h3>`
				)
		)
		.addTo(map)

})();

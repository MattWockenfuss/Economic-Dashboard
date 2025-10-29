//    https://plotly.com/javascript/reference/choroplethmap/


var data = [{
  type: "choroplethmap", 
  locations: ["NY", "MA", "VT", "TX", "PA"], 
  z: [-50, -10, -20, -90, -40],
  geojson: "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
}];

/*
const bounds = [
    [-180, 10], //Southwest coordinates
    [-40, 90] //Northeast coordinates
];
*/




const layout = {
  map: {
    style: "carto-darkmatter-nolabels", // any MapLibre style
    center: { lat: 38.8283, lon: -98.5795 },
    zoom: 4.5,
    bounds: { east: -40, north: 90, south: 10, west: -180},
    margin: {t:0,r:0,b:0,l:0}
  }
};

var config = {
    scrollZoom: true,      //users cant scroll
    editable: false,        //users cant edit the data
    displayModeBar: false,   //the command bar, options, etc...
    displaylogo: false        //displays the logo on modebar
};





// let map2 = {
//     container: 'mapplot',
//     center: [-98.5795, 38.8283],
//     zoom: 5,
//     maxBounds: bounds, //Set to max
//     canvasContextAttributes: {antialias: true}
// };






Plotly.newPlot('mapplot', data, layout, config);



map.on('mousemove', (e) => {
      console.log(`lon: ${e.lngLat.lng.toFixed(4)}, lat: ${e.lngLat.lat.toFixed(4)}`);
});



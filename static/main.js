var data = [{
  type: "choroplethmap", 
  locations: ["NY", "MA", "VT", "TX", "PA"], 
  z: [-50, -10, -20, -90, -40],
  geojson: "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
}];

var layout = {map: {center: {lon: -74, lat: 43}, zoom: 3.5}};

Plotly.newPlot('map', data, layout);
//    https://plotly.com/javascript/reference/choroplethmap/

/*
var data = [{
  type: "choroplethmap", 
  locations: ["NY", "MA", "VT", "TX", "PA", "VT", "MA", "MN", "HI", "AK"], 
  z: [-50, -10, -20, -90, -40, -15, -100, -200, -30, -20],
  geojson: "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
}];

const layout = {
  map: {
    style: "carto-darkmatter-nolabels", // any MapLibre style
    center: { lat: 38.8283, lon: -98.5795 },
    zoom: 4.5,
    bounds: { east: -60, north: 72, south: 17, west: -172},
    margin: {t:0,r:0,b:0,l:0}
  }
};

var config = {
    scrollZoom: true,      //users cant scroll
    editable: false,        //users cant edit the data
    displayModeBar: false,   //the command bar, options, etc...
    displaylogo: false        //displays the logo on modebar
};

Plotly.newPlot('mapplot', data, layout, config);



map.on('mousemove', (e) => {
      console.log(`lon: ${e.lngLat.lng.toFixed(4)}, lat: ${e.lngLat.lat.toFixed(4)}`);
});
*/

function GenChoropleth() {
  //If data is for choropleth

  var data = [{
    type: "choroplethmap", 
    locations: ["NY", "MA", "VT", "TX", "PA", "VT", "MA", "MN", "HI", "AK"], 
    z: [-50, -10, -20, -90, -40, -15, -100, -200, -30, -20],
    geojson: "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
  }];

  const layout = {
    map: {
      style: "carto-darkmatter-nolabels", // any MapLibre style
      center: { lat: 38.8283, lon: -98.5795 },
      zoom: 4.5,
      bounds: { east: -60, north: 72, south: 17, west: -172},
      margin: {t:0,r:0,b:0,l:0}
    }
  };

  var config = {
    scrollZoom: true,      //users cant scroll
    editable: false,        //users cant edit the data
    displayModeBar: false,   //the command bar, options, etc...
    displaylogo: false        //displays the logo on modebar
  };

  Plotly.newPlot('mapplot', data, layout, config);

  return true;
}

function GenDensity() {
  //If data is for density

  var data = [{
    type: "densitymap", 
    lon: [-98, -105, -110], lat: [35, 30, 32], z: [1, 3, 5],
    radius: 100, colorbar: {y: 1, yanchor: 'top', len: 0.45},
    geojson: "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
  }];

  const layout = {
    map: {
      style: "carto-darkmatter-nolabels", // any MapLibre style
      center: { lat: 38.8283, lon: -98.5795 },
      zoom: 4.5,
      bounds: { east: -60, north: 72, south: 17, west: -172},
      margin: {t:0,r:0,b:0,l:0}
    }
  };

  var config = {
    scrollZoom: true,      //users cant scroll
    editable: false,        //users cant edit the data
    displayModeBar: false,   //the command bar, options, etc...
    displaylogo: false        //displays the logo on modebar
  };

  Plotly.newPlot('mapplot', data, layout, config);

  return true;
}

GenChoropleth();
const slider = document.getElementById("dataSlider");
const label = document.getElementById("sliderLabel");
const bigyearlabel = document.getElementById("year");

// initialize
label.innerText = slider.value;

// update live
slider.addEventListener("input", () => {
  label.innerText = slider.value;
  bigyearlabel.innerText = slider.value;
});




const colorThemes = {
  gdp: [
    [0, "#0f172a"],
    [0.5, "#2563eb"],
    [1, "#60a5fa"]
  ],
  population: [
    [0, "#052e16"],
    [0.5, "#22c55e"],
    [1, "#bbf7d0"]
  ],
  unemployment: [
    [0, "#2b0000"],
    [0.4, "#8b0000"],
    [0.75, "#ff6b6b"],
    [1, "#ffe66d"]
  ],
  income: [
    [0, "#1f1147"],
    [0.4, "#3b3b98"],
    [0.75, "#fbc531"],
    [1, "#fff1b6"]
  ],
  costOfLiving: [
    [0, "#022c22"],
    [0.4, "#134e4a"],
    [0.75, "#2dd4bf"],
    [1, "#ccfbf1"]
  ],
  growth: [
    [0, "#0b132b"],
    [0.35, "#1c2541"],
    [0.7, "#3a86ff"],
    [1, "#9ec5fe"]
  ],
};

const datasets = {
  gdp: [
    4200, 2600, 2400, 1600, 1100, 1000, 900, 880, 850, 840,
    820, 810, 790, 750, 700, 680, 650, 630, 620, 600,
    580, 560, 540, 520, 500, 480, 460, 450, 430, 420,
    400, 380, 360, 350, 340, 330, 320, 300, 280, 270,
    260, 240, 230, 220, 210, 200, 190, 180, 170, 165, 58
  ],
  population: [
    39.0, 30.5, 23.5, 21.0, 13.0, 12.5, 11.8, 11.1, 10.9, 10.1,
    9.4, 8.9, 7.9, 7.6, 7.2, 7.0, 6.9, 6.2, 6.1, 5.9,
    5.8, 5.7, 5.3, 4.9, 4.7, 4.5, 4.3, 4.0, 3.6, 3.4,
    3.2, 3.1, 2.9, 2.8, 2.7, 2.2, 1.9, 1.8, 1.8, 1.5,
    1.4, 1.4, 1.1, 1.1, 1.0, 0.9, 0.8, 0.6, 0.6, 0.5, 0.75
  ],
  unemployment: [
    4.7,4.2,5.1,4.8,5.4,5.2,5.6,5.0,4.9,4.3,
    4.4,4.1,4.5,5.7,4.9,5.3,5.4,4.3,4.4,4.9,
    4.2,5.1,5.3,5.8,6.0,5.5,4.8,4.2,4.6,5.0,
    4.1,5.2,5.7,6.1,4.9,5.6,4.4,6.2,4.7,4.3,
    4.2,4.8,4.9,4.1,4.3,4.5,4.6,4.1,5.0,5.4
  ],
  income: [
    84,82,76,71,70,69,67,66,65,81,
    78,85,74,68,72,63,64,77,73,66,
    86,65,61,59,58,57,71,79,63,62,
    76,70,56,54,60,58,65,55,61,73,
    72,60,58,78,80,63,61,69,62,68
  ],
  costOfLiving: [
    150,145,115,125,112,110,104,102,100,140,
    130,150,120,108,105,98,97,122,107,100,
    147,99,95,92,94,90,120,145,98,97,
    115,118,93,90,96,95,98,89,99,125,
    121,100,99,140,138,105,103,110,101,120
  ],
  growth: [
    70,65,78,75,60,62,58,74,73,66,
    77,64,71,57,76,72,63,80,69,61,
    67,59,71,54,52,56,66,64,60,61,
    85,79,55,50,62,57,65,49,70,73,
    68,60,63,67,69,58,61,66,72,74
  ]
}



function GenChoropleth() {
  const container = document.getElementById('mapplot');
  const rect = container.getBoundingClientRect();

  var data = [{
    type: "choroplethmap",
    locations: [
      "CA","NY","TX","FL","IL","PA","OH","GA","NC","NJ",
      "WA","MA","VA","MI","AZ","TN","IN","CO","MN","WI",
      "MD","MO","SC","AL","LA","KY","OR","CT","IA","OK",
      "UT","NV","AR","MS","KS","NM","NE","WV","ID","HI",
      "NH","ME","MT","RI","DE","SD","ND","VT","WY","AK","DC"
    ],
    z: datasets.gdp,
    opacity: 1,                  // 👈 important for animation
    colorscale: colorThemes.gdp,
    geojson: "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json",
    showscale: false
  }];

  const layout = {
    margin: {t:0, r:0, b:0, l:0, pad: 0},
    map: {
      style: "carto-darkmatter-nolabels", // any MapLibre style
      center: { lat: 38.8283, lon: -98.5795 },
      zoom: 4.5,
      bounds: { east: -60, north: 72, south: 17, west: -172}
      
    }
  };

  var config = {
    scrollZoom: true,      //users cant scroll
    editable: false,        //users cant edit the data
    displayModeBar: false,   //the command bar, options, etc...
    displaylogo: false        //displays the logo on modebar
  };

  Plotly.newPlot('mapplot', data, layout, config);
  window.addEventListener('resize', () => {
    const r = container.getBoundingClientRect();
    Plotly.relayout(container, { width: r.width, height: r.height });
  });
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

function setDataset(name) {
  const values = datasets[name];
  const colorscale = colorThemes[name];

  const min = Math.min(...values);
  const max = Math.max(...values);

  // 1) Apply new data instantly, but invisible (opacity 0)
  Plotly.restyle("mapplot", {
    z: [values],
    zmin: [min],
    zmax: [max],
    colorscale: [colorscale],
    opacity: [0]
  }, [0]).then(() => {
    // 2) Fade it in
    Plotly.animate("mapplot", {
      data: [{ opacity: 1 }]
    }, {
      transition: { duration: 5700, easing: "sin-in-out" },
      frame: { duration: 5700, redraw: false }
    });
  });
}

window.setDataset = setDataset;

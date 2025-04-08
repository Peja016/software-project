import fetchData from "./fetchData.js";

let directionsService, directionsRenderer;

let map;

directionsService = new google.maps.DirectionsService();
directionsRenderer = new google.maps.DirectionsRenderer({
  suppressMarkers: true,
  preserveViewport: true,
  polylineOptions: {
    strokeColor: "#e63946",
    strokeWeight: 6,
    strokeOpacity: 0.9,
  },
});

const isMobile = window.innerWidth <= 768;

const mapDiv = document.getElementById("map");

const weather = document.getElementById("weather");

const legend = document.getElementById("legend");

const originInput = document.getElementById("origin");
const destinationInput = document.getElementById("destination");

const options = {
  componentRestrictions: { country: "ie" }, // Restrict to Ireland
};

// Setup Autocomplete
const originAutocomplete = new google.maps.places.Autocomplete(
  originInput,
  options
);
const destinationAutocomplete = new google.maps.places.Autocomplete(
  destinationInput,
  options
);

// Save markers and last route globally
let originMarker = null;
let destinationMarker = null;
let lastRouteResponse = null;

// Function to show markers and path but NOT time yet
const updateRoutePreview = () => {
  const origin = originInput.value;
  const destination = destinationInput.value;

  if (!origin || !destination) return;

  directionsService.route(
    {
      origin: origin,
      destination: destination,
      travelMode: google.maps.TravelMode.BICYCLING,
    },
    (response, status) => {
      if (status === "OK") {
        lastRouteResponse = response;
        directionsRenderer.setDirections(response);

        // Get start and end positions
        const startLoc = response.routes[0].legs[0].start_location;
        const endLoc = response.routes[0].legs[0].end_location;

        // Remove previous markers
        if (originMarker) originMarker.setMap(null);
        if (destinationMarker) destinationMarker.setMap(null);

        // Add origin marker
        originMarker = new google.maps.Marker({
          position: startLoc,
          map: map,
          label: {
            text: "S",
            color: "white",
          },
          zIndex: 5,
        });

        // Add destination marker
        destinationMarker = new google.maps.Marker({
          position: endLoc,
          map: map,
          label: {
            text: "D",
            color: "white",
          },
          zIndex: 5,
        });
      } else {
        directionsRenderer.set("directions", null);
        if (originMarker) originMarker.setMap(null);
        if (destinationMarker) destinationMarker.setMap(null);
        lastRouteResponse = null;
        alert("Preview route failed: " + status);
      }
    }
  );
};

// Trigger live preview when place is selected
originAutocomplete.addListener("place_changed", updateRoutePreview);
destinationAutocomplete.addListener("place_changed", updateRoutePreview);

// add close button
const setCloseBtn = (dom) => {
  const closeBtn = document.createElement("button");
  closeBtn.textContent = "×";
  closeBtn.className = "close-btn";
  closeBtn.addEventListener("click", () => {
    dom.remove();
  });
  dom.appendChild(closeBtn);
};

// Show time & distance only after clicking "Route" button
document.getElementById("routeBtn").addEventListener("click", () => {
  if (!lastRouteResponse) {
    alert("Please enter valid origin and destination first.");
    return;
  }

  const leg = lastRouteResponse.routes[0].legs[0];
  const duration = leg.duration.text;
  const distance = leg.distance.text;
  const estimation = document.createElement("div");
  estimation.className = "estimation";

  setCloseBtn(estimation);

  const line1 = document.createElement("p");
  line1.textContent = `Estimated time: ${duration}`;

  const line2 = document.createElement("p");
  line2.textContent = `Distance: ${distance}`;

  estimation.appendChild(line1);
  estimation.appendChild(line2);

  mapDiv.appendChild(estimation);
  // Auto-remove after 5 seconds if not manually closed
  setTimeout(() => {
    if (document.body.contains(estimation)) {
      estimation.remove();
    }
  }, 5000);
});

const lineChart = document.createElement("div");
lineChart.id = "line-chart";

const showDailyWeather = async (stationInfo) => {
  const weatherData = await fetchData(`/api/oneDayWeather`);
  if (!weatherData || weatherData.length === 0) return;
  const weatherSection = document.createElement("div");
  weatherSection.className = "weather-section";
  const title = document.createElement("h3");
  title.textContent = "Historical Weather Overview";
  weatherSection.appendChild(title);

  // Create wrapper for weather cards
  const weatherContainer = document.createElement("div");
  weatherContainer.className = "weather-cards";

  weatherData.forEach((data) => {
    const card = document.createElement("div");
    card.className = "weather-card";

    const time = document.createElement("p");
    time.textContent = data.time;
    time.className = "weather-hour";

    const icon = document.createElement("img");
    icon.src = `https://openweathermap.org/img/wn/${data.icon}.png`;
    icon.alt = data.description || "weather icon";
    icon.className = "weather-icon";

    const temp = document.createElement("p");
    temp.textContent = `${data.temperature}`;
    temp.className = "weather-temp";

    card.appendChild(time);
    card.appendChild(icon);
    card.appendChild(temp);

    weatherContainer.appendChild(card);
  });

  weatherSection.appendChild(weatherContainer);
  stationInfo.appendChild(weatherSection);
};

const drawChart = async (number) => {
  const stationData = await fetchData(`/api/stations/${number}`);
  const data = google.visualization.arrayToDataTable(stationData);
  const options = {
    title: "Bike Availability & Stand Availability Over Time (historical data)",
    titleTextStyle: {
      fontSize: 16,
    },
    curveType: "function",
    legend: { position: "bottom" },
    hAxis: { title: "Time" },
    vAxis: {
      title: "Quantity",
      viewWindow: {
        min: 0,
      },
    },
    colors: ["#457b9d", "#e63946"],
  };

  const chart = new google.visualization.LineChart(lineChart);
  chart.draw(data, options);
};

const addMarkers = async () => {
  const infoWindow = new google.maps.InfoWindow();
  const bikeData = await fetchData("/api/bikesInfo");
  bikeData.forEach(
    ({
      position,
      name,
      available_bikes,
      available_bike_stands,
      status,
      number,
    }) => {
      const marker = new google.maps.Marker({
        position,
        map,
        icon: {
          url:
            "/static/images/location" +
            (available_bikes
              ? available_bike_stands
                ? ""
                : "_darkBlue"
              : "_gray") +
            ".svg",
          scaledSize: new google.maps.Size(40, 40),
        },
      });

      marker.addListener("mouseover", () => {
        infoWindow.setContent(`
            <div class="info">
                <p>${name}</p>
                <p>Available bikes: ${available_bikes}</p>
                <p>Available bike stands:  ${available_bike_stands}</p>
                <p>Status:  ${status}</p>
            </div>
        `);
        infoWindow.open(map, marker);
      });

      marker.addListener("mouseout", () => {
        infoWindow.close();
      });

      // Now start drawing the chart
      google.charts.load("current", { packages: ["corechart"] });

      marker.addListener("click", (e) => {
        const markerPosition = marker.getPosition();

        // remove the previous stationInfo
        const existingInfo = document.getElementById("station-info");
        if (existingInfo) {
          existingInfo.remove();
        }
        // set the station clicked to be the center of page.
        map.panTo(markerPosition);
        google.charts.setOnLoadCallback(drawChart(number));

        const stationInfo = document.createElement("div");
        stationInfo.id = "station-info";

        stationInfo.style.display = "block";

        const stop = document.createElement("div");
        const id = document.createElement("p");

        id.textContent = `Station ID: ${number}`;

        const stationName = document.createElement("p");
        stationName.style.fontSize = "20px";
        stationName.style.fontWeight = "bold";
        stationName.style.color = "var(--custom-primary)";
        stationName.textContent = name;

        stop.appendChild(id);
        stop.appendChild(stationName);

        const info = document.createElement("div");
        const line1 = document.createElement("p");
        line1.textContent = `Current status: ${status}`;
        const line2 = document.createElement("p");
        line2.innerHTML = `
          <span>
            Available Bikes: 
            <span style="color: var(--custom-darkBlue); font-size: 18px;">${available_bikes}</span>
          </span>
          &nbsp;|& ;
          <span>
            Available Stands:
            <span style="color: var(--custom-red); font-size: 18px;">${available_bike_stands}</span>
          </span>
        `;

        info.appendChild(line1);
        info.appendChild(line2);

        stationInfo.appendChild(stop);
        stationInfo.appendChild(info);
        stationInfo.appendChild(lineChart);
        showDailyWeather(stationInfo);

        setCloseBtn(stationInfo);

        document.body.appendChild(stationInfo);
      });
    }
  );
};

export const initMap = async () => {
  const center = { lat: 53.3492323, lng: -6.2677148 };
  map = new google.maps.Map(mapDiv, {
    zoom: 15,
    center,
  });

  map.controls[google.maps.ControlPosition.LEFT_TOP].push(weather);

  if (!isMobile) {
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(legend);
  }

  setTimeout(() => {
    legend.style.opacity = 1;
    weather.style.opacity = 1;
  }, 500);

  directionsRenderer.setMap(map);

  addMarkers();
};

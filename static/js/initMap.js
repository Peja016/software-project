import fetchData from "./fetchData.js";

let directionsService, directionsRenderer;

export async function initMap() {
  const bikeData = await fetchData("/api/bikesInfo");
  const center = { lat: 53.3492323, lng: -6.2677148 };
  const mapDiv = document.getElementById("map");
  const map = new google.maps.Map(mapDiv, {
    zoom: 15,
    center,
  });

  const weather = document.getElementById("weather");
  map.controls[
    google.maps.ControlPosition.LEFT_TOP
  ].push(weather);

  const legend = document.getElementById("legend");
  map.controls[
    google.maps.ControlPosition.TOP_RIGHT
  ].push(legend);

  if (bikeData) {
    legend.style.opacity = 1
    weather.style.opacity = 1
  }

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

  directionsRenderer.setMap(map);

  bikeData.forEach(({ position }) => {
    const infoWindow = new google.maps.InfoWindow();
    bikeData.forEach(
      ({ position, name, available_bikes, available_bike_stands, status }) => {
        const marker = new google.maps.Marker({
          position,
          map,
          icon: {
            url:
              "/static/images/location" +
              (available_bikes
                ? available_bike_stands
                  ? ""
                  : "_lightBlue"
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

        marker.addListener("click", (e) => {
          const markerPosition = marker.getPosition();
          // set the station clicked to be the center of page.
          map.panTo(markerPosition);
        });
      }
    );
  });
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
  function updateRoutePreview() {
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
  }

  // Trigger live preview when place is selected
  originAutocomplete.addListener("place_changed", updateRoutePreview);
  destinationAutocomplete.addListener("place_changed", updateRoutePreview);

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

    const closeBtn = document.createElement("button");
    closeBtn.textContent = "×";
    closeBtn.className = "close-btn";
    closeBtn.addEventListener("click", () => estimation.remove());

    const line1 = document.createElement("p");
    line1.textContent = `Estimated time: ${duration}`;

    const line2 = document.createElement("p");
    line2.textContent = `Distance: ${distance}`;

    estimation.appendChild(closeBtn);
    estimation.appendChild(line1);
    estimation.appendChild(line2);
    mapDiv.appendChild(estimation);
    // Auto-remove after 3 seconds if not manually closed
    setTimeout(() => {
      if (document.body.contains(estimation)) {
        estimation.remove();
      }
    }, 5000);
  });
}

window.initMap = initMap
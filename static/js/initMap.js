async function initMap() {
    const bikeData = await fetchData("{{ bikes_api_url }}");
    const lat = "{{ lat }}"
    const lon = "{{ lon }}"
    const location = { lat: +lat, lng: +lon };
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 15,
        center: location
    });

    bikeData.forEach(({ position }) => {
        const marker = new google.maps.Marker({
            position,
            map,
        });

        // console.log(bikeData)
        const infoWindow = new google.maps.InfoWindow();
        
        bikeData.forEach(({
            position,
            name,
            available_bikes,
            available_bike_stands,
            status
        }) => {
            const marker = new google.maps.Marker({
                position,
                map,
            });
            
            marker.addListener("click", () => {
                infoWindow.setContent(`
                    <div>
                        <b>${name}</b>
                        <p>Available bikes: ${available_bikes}</p>
                        <p>Available bike stands: ${available_bike_stands}</p>
                        <p>Status: ${status}</p>
                    </div>
                `);
                infoWindow.open(map, marker);
            });
        });
    });
}
import fetchData from './fetchData.js'

const getWeather = async () => {
    const weatherData = await fetchData('/api/weather');
    const temp = weatherData.main.temp
    const iconCode = weatherData.weather[0].icon; // get icon code
    const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
    document.getElementById("weather-icon").src = iconUrl;
    const weather = document.getElementById("weather");
    const text = weather.querySelector("p");
    text.textContent = `${Math.round(temp * 10) / 10}℃`;
}

getWeather()
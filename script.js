let pinDictionary = {};
let cardDictionary = {};
let scrollCounter = 0;
let pharmaciesWithDetails = {};

function setFromToText(currentHour){
    let desdeHastaElement = document.getElementById("desdehasta");

    if (currentHour >= 8) {
        desdeHastaElement.textContent = "ABIERTAS HASTA LAS 8HS DE MAÑANA";
    } else {
        desdeHastaElement.textContent = "ABIERTAS HASTA LAS 8HS DE HOY: ";
    }
}

function addCard(pharmacy){
    let nameNewNode = document.createElement("h4");
    let addressNewNode = document.createElement("h5");
    let extraInformationNewNode = document.createElement("h5");
    let cardNewNode = document.createElement("div");
    let cardText = document.createElement("div");
    let pharmacyListNode = document.querySelector("#pharmacyList");
    let imageNode = document.createElement("img");

    cardNewNode.className = "card";
    cardText.className = "card-text";
    addressNewNode.className = "lighter"

    imageNode.src = "public/logo.svg";
    imageNode.className = "card-image";
    nameNewNode.textContent = pharmacy.nombre;
    addressNewNode.textContent= pharmacy.direccion;
    extraInformationNewNode.textContent = "Telefono: " + pharmacy.telefono;

    cardText.appendChild(nameNewNode);
    cardText.appendChild(addressNewNode);
    cardText.appendChild(extraInformationNewNode);

    cardNewNode.appendChild(imageNode);
    cardNewNode.appendChild(cardText);

    cardNewNode.addEventListener("click",() => center(pharmacy));
    cardNewNode.addEventListener("mouseenter", () => {
        highlightPin(pharmacy.nombre,.2);
        highlightCard(pharmacy.nombre, .2);
    });
    cardNewNode.addEventListener("mouseleave", () => {
        resetPin(pharmacy.nombre,.2);
        resetCard(pharmacy.nombre);
    });

    pharmacyListNode.appendChild(cardNewNode);

    cardDictionary[pharmacy.nombre] = cardNewNode;
}

function dropPin(pharmacy){
    let farmaciaLogoPin = document.createElement("img");
    let animationSeconds = .2;
    farmaciaLogoPin.src = "public/logo.svg";
    farmaciaLogoPin.style.width = '25px';
    let marker = new maplibregl.Marker({element:farmaciaLogoPin, anchor: 'bottom'}).setLngLat([pharmacy.longitud, pharmacy.latitud]).addTo(map);

    //console.log("latitud: " + pharmacy.latitud + " longitud: " + pharmacy.longitud);

    let pinElement = marker.getElement();
    pinElement.addEventListener("mouseenter", () => highlightCard(pharmacy.nombre,animationSeconds));
    pinElement.addEventListener("mouseleave", () => resetCard(pharmacy.nombre,animationSeconds));

    pinDictionary[pharmacy.nombre] = marker;
}

function highlightCard(pharmacyName, animationSeconds) {
    let card = cardDictionary[pharmacyName];

    if (card) {
        card.style.transition = "background-color " + animationSeconds + "s ease-in-out";
        card.style.backgroundColor = "#a4e4c8";
    }
    scrollToCard(pharmacyName)

}

function scrollToCard(pharmacyName, callback) {
    let container = document.querySelector(".card-list");
    let cards = document.querySelectorAll(".card");

    cards.forEach(card => {
        if (card.querySelector("h4").textContent === pharmacyName) {
            card.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
            let isScrolling;
            container.addEventListener("scroll", () => {
                clearTimeout(isScrolling);
                isScrolling = setTimeout(() => {
                    scrollCounter++;
                    //console.log("Scrolling to " + pharmacyName + " finished! Total scrolls: " + scrollCounter);
                    if (callback) callback(pharmacyName); // Execute the callback when done
                }, 100);
            });
        }
    });
}

function resetCard(pharmacyName, animationSeconds) {
    let card = cardDictionary[pharmacyName];
    if (card) {
        card.style.backgroundColor = "white";
    }
}

function addPharmacy(pharmacy){
    addCard(pharmacy);
    dropPin(pharmacy);
}

function highlightPin(pharmacyName, animationSeconds) {
    let marker = pinDictionary[pharmacyName];
    if (marker) {
        let pin = marker.getElement();
        pin.style.transition = "transform " + animationSeconds + "s ease-in-out";
        marker.setOffset([0, -10]);
    }
}

function resetPin(pharmacyName, animationSeconds) {
    let marker = pinDictionary[pharmacyName];
    resetCard(pharmacyName);
    if (marker) {
        let pin = marker.getElement();
        pin.style.transition = "transform " + animationSeconds + "s ease-in-out";
        marker.setOffset([0, 0]);

        //if I don't add this timeout, animation ends abruptly after your mouse leaves the card
        setTimeout(() => {
            pin.style.transition = "";
        }, animationSeconds*1000); // timeout is in milliseconds
    }
}

function center(pharmacy){
    map.setCenter([pharmacy.longitud, pharmacy.latitud]);
    map.setZoom(15);
}

function getCurrentDate() {
    let today = new Date();
    let day = String(today.getDate()).padStart(2, '0');
    let month = String(today.getMonth() + 1).padStart(2, '0');
    return `${day}/${month}`;
}
function getCurrentDate2() {
    //an improvement on getcurrentDate1, to make sure this works outside of Argentina's time zone
    let today = new Date();
    let options = { timeZone: 'America/Argentina/Buenos_Aires', day: '2-digit', month: '2-digit' };
    let formattedDate = new Intl.DateTimeFormat('en-GB', options).format(today);
    return formattedDate;
}
function getCurrentHour() {
    let today = new Date();
    let options = { timeZone: 'America/Argentina/Buenos_Aires', hour: '2-digit', hour12: false };
    let currentHour = new Intl.DateTimeFormat('en-US', options).format(today);
    return currentHour;
}
function getPharmaciesOnDuty(turnosData, currentDate, currentHour) {
    let pharmacies = [];
    turnosData.forEach(entry => {
        if (currentHour >= 8){
            if (entry.datesFrom.includes(currentDate)) {
                pharmacies = pharmacies.concat(entry.pharmacies);
            }
        }
        else {
            if (entry.datesTo.includes(currentDate)) {
                pharmacies = pharmacies.concat(entry.pharmacies);
            }
        }
    });
    return pharmacies;
}

async function getCoordinates(address) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;

    try {
        const response = await fetch(url, {
            headers: { 'User-Agent': 'deturnoarBeta/1.0 (YourEmail@example.com)' }
        });

        if (!response.ok) {
            throw new Error("Failed to fetch data");
        }

        const data = await response.json();
        if (data.length === 0) {
            console.error("No coordinates found for this address.");
            return null;
        }

        const { lat, lon } = data[0];
        console.log(`Latitude: ${lat}, Longitude: ${lon}`);
        return { lat, lon };
    } catch (error) {
        console.error("Error fetching coordinates:", error);
        return null;
    }
}

function calculateDistance(fromLat, fromLon, toLat, toLon) {
    const DEG_TO_RAD = 0.017453292519943295769236907684886;
    const EARTH_RADIUS_IN_METERS = 6372797.560856;
    let latitudeArc = (fromLat - toLat) * DEG_TO_RAD;
    let longitudeArc = (fromLon - toLon) * DEG_TO_RAD;

    let latitudeH = Math.sin(latitudeArc * 0.5);
    latitudeH *= latitudeH;

    let longitudeH = Math.sin(longitudeArc * 0.5);
    longitudeH *= longitudeH;

    let tmp = Math.cos(fromLat * DEG_TO_RAD) * Math.cos(toLat * DEG_TO_RAD);

    return EARTH_RADIUS_IN_METERS * 2.0 * Math.asin(Math.sqrt(latitudeH + tmp * longitudeH));
}

function orderCardsByDistance(lat, lon) {
    let cardsArray = Array.from(document.querySelectorAll("#pharmacyList .card"));

    pharmaciesOnDutyData.forEach(pharmacy => {
            pharmacy.distance = Math.round(calculateDistance(lat,lon,pharmacy.latitud, pharmacy.longitud));
    });

    pharmaciesOnDutyData.sort((a, b) => a.distance - b.distance);

    cardsArray.forEach((card) => {
        card.remove();
    })

    Object.values(pinDictionary).forEach(pin => pin.remove());

    pharmaciesOnDutyData.forEach(pharmacy => {
        addPharmacy(pharmacy);
    });
}

function addSearchListener(){
    document.addEventListener("DOMContentLoaded", function () {
        // Select the form
        const searchForm = document.querySelector(".search-form");
        const searchButton = searchForm.querySelector("button"); // Select the button

        // Add event listener to handle submit
        searchForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevents the page from reloading

            // Get the input value
            const addressInput = searchForm.querySelector("input").value.trim();

            if (addressInput) {
                let searchInput = addressInput + ", SANTA FE DE LA VERA CRUZ, SANTA FE, ARGENTINA"
                console.log("Buscando:", searchInput);

                // pongo un indicador de que se está fetcheando la direccion
                searchButton.disabled = true;
                searchButton.innerHTML = `<img src="public/loading-spinner.svg" class="spinner" alt="loading">`;

                getCoordinates(searchInput).then(coords => {
                    if (coords) {
                        let { lat, lon } = coords;
                        console.log("lat: " + lat + " lon: " + lon);

                        let searchInputPin = document.createElement("img");
                        searchInputPin.src = "public/classic-pin.svg";
                        searchInputPin.style.width = '35px';

                        orderCardsByDistance(lat,lon);
                        if (personalAddressPin) {
                            personalAddressPin.remove()
                        }
                        personalAddressPin = new maplibregl.Marker({
                            element: searchInputPin,
                            anchor: 'bottom'
                        }).setLngLat([lon, lat]).addTo(map);

                    } else {
                        console.log("No se encontró la dirección");
                    }
                }).catch(error => {
                    console.error("Error de la api de coordenadas: ", error);
                }).finally(() => {
                    // Reset button state
                    searchButton.disabled = false;
                    searchButton.innerHTML = `<img src="public/search-button.svg">`;
                });
            } else {
                console.log("Por favor ingrese una dirección.");
            }
        });
    });
}

addSearchListener();
let map = new maplibregl.Map({
    style: 'https://tiles.openfreemap.org/styles/bright',
    container: 'map',
    center: [-60.705, -31.630],
    zoom: 12.2,
})

//por ahora lo dejo asi porque total hay una sola en santa fe
let farmacias24HS = {
    nombre: "ACOSTA (24hs)",
    direccion: "SUIPACHA 2506",
    telefono: "0342 - 4556677",
    latitud: -31.640134534867073,
    longitud: -60.70403018834733
};
let personalAddressPin;
let currentDate = getCurrentDate2();
console.log("current date: " + currentDate);
let currentHour = getCurrentHour();
console.log("current hour: " + currentHour);
let pharmaciesOnDuty = [];
let pharmaciesOnDutyData = [];

pharmaciesOnDutyData.push(farmacias24HS);
addPharmacy(farmacias24HS)
Promise.all([
    fetch("data/turnos.json").then(res => res.json()),
    fetch("data/pharmacies_with_phones.json").then(res => res.json())
]).then(([turnosData, pharmaciesData]) => {
    // Find pharmacies on duty today
    pharmaciesOnDuty = getPharmaciesOnDuty(turnosData, currentDate, currentHour);

    pharmaciesData.forEach(pharmacy => {
        pharmaciesWithDetails[pharmacy.nombre.toUpperCase()] = pharmacy;
    });

    pharmaciesOnDuty.forEach(pharmacyName => {
        let pharmacyDetails = pharmaciesWithDetails[pharmacyName];
        if (pharmacyDetails) {
            addPharmacy(pharmacyDetails);
            pharmaciesOnDutyData.push(pharmacyDetails);
        } else {
            console.warn("No se encontro la farmacia:", pharmacyName);
        }
    });
}).catch(error => console.error("Error loading JSON:", error));


setFromToText(currentHour);


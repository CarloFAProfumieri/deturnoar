let pinDictionary = {};
let cardDictionary = {};
let scrollCounter = 0;
let pharmaciesWithDetails = {};

function setFromToText(currentHour){
    let desdeHastaElement = document.getElementById("desdehasta");

    if (currentHour >= 8) {
        desdeHastaElement.textContent = "ABIERTAS HASTA LAS 8HS DE MAÑANA";
    } else {
        desdeHastaElement.textContent = "ABIERTAS HASTA LAS 8HS DE HOY";
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

    imageNode.addEventListener("click",() => center(pharmacy));
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
                }, 100); // Adjust timeout for accuracy
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

        //if you don't set this timeout, once your mouse leaves the card the animation will end abruptly
        setTimeout(() => {
            pin.style.transition = "";
        }, animationSeconds*1000);//miliseconds
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
    return `${day}/${month}`; // Return formatted date as "DD/MM HH:mm"
}
function getCurrentDate2() {
    let today = new Date();
    let options = { timeZone: 'America/Argentina/Buenos_Aires', day: '2-digit', month: '2-digit' };
    let formattedDate = new Intl.DateTimeFormat('en-GB', options).format(today);
    return formattedDate; // Returns the date in "DD/MM" format in Buenos Aires time
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

let map = new maplibregl.Map({
    style: 'https://tiles.openfreemap.org/styles/bright',
    container: 'map',
    center: [-60.705, -31.630],
    zoom: 12.2,
})


let currentDate = getCurrentDate2();
console.log("current date: " + currentDate);
let currentHour = getCurrentHour();
console.log("current hour: " + currentHour);
let pharmaciesOnDuty = [];

setFromToText(currentHour);

let farmacia = {
    nombre: "ACOSTA (24hs)",
    direccion: "SUIPACHA 2506",
    telefono: "0342 - 4556677",
    latitud: -31.640134534867073,
    longitud: -60.70403018834733
};

Promise.all([
    fetch("data/turnos.json").then(res => res.json()),
    fetch("data/pharmacies_with_phones.json").then(res => res.json())
]).then(([turnosData, pharmaciesData]) => {
    // Find pharmacies on duty today
    pharmaciesOnDuty = getPharmaciesOnDuty(turnosData, currentDate, currentHour);

    // Create a dictionary of pharmacies with details
    pharmaciesData.forEach(pharmacy => {
        pharmaciesWithDetails[pharmacy.nombre.toUpperCase()] = pharmacy;
    });

    // Match pharmacies on duty with their details
    pharmaciesOnDuty.forEach(pharmacyName => {
        let pharmacyDetails = pharmaciesWithDetails[pharmacyName];
        if (pharmacyDetails) {
            addPharmacy(pharmacyDetails);
        } else {
            console.warn("No details found for pharmacy:", pharmacyName);
        }
    });
}).catch(error => console.error("Error loading JSON:", error));

addPharmacy(farmacia);

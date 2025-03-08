let pharmacyDictionary = {};

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

    imageNode.src = "public/logo.svg";

    nameNewNode.textContent = pharmacy.nombre;
    addressNewNode.textContent= pharmacy.direccion;
    extraInformationNewNode.textContent = "Telefono: " + pharmacy.telefono;

    cardText.appendChild(nameNewNode);
    cardText.appendChild(addressNewNode);
    cardText.appendChild(extraInformationNewNode);

    cardNewNode.appendChild(imageNode);
    cardNewNode.appendChild(cardText);

    cardNewNode.addEventListener("mouseenter", () => highlightPin(pharmacy.nombre,.2));
    cardNewNode.addEventListener("mouseleave", () => resetPin(pharmacy.nombre,.2));

    pharmacyListNode.appendChild(cardNewNode);
}
function dropPin(pharmacy){
    let farmaciaLogoPin = document.createElement("img");
    farmaciaLogoPin.src = "public/logo-pin-mapa.svg";
    farmaciaLogoPin.style.width = '60px';
    farmaciaLogoPin.style.transformOrigin = "center"; // Ensure scaling happens from the center
    let marker = new maplibregl.Marker({element:farmaciaLogoPin}).setLngLat([pharmacy.longitud, pharmacy.latitud]).addTo(map);
    console.log("latitud: " + pharmacy.latitud + " longitud: " + pharmacy.longitud);
    pharmacyDictionary[pharmacy.nombre] = marker;
}
function addPharmacy(pharmacy){
    addCard(pharmacy);
    dropPin(pharmacy);
}
function highlightPin(pharmacyName, animationSeconds) {
    let marker = pharmacyDictionary[pharmacyName];
    if (marker) {
        let pin = marker.getElement();
        pin.style.transition = "transform " + animationSeconds + "s ease-in-out";
        pin.style.transform = "scale(1.5)";  // Make the pin bigger
        marker.setOffset([0, -10]); // Adjust position so it doesn't "float"
    }
}

function resetPin(pharmacyName, animationSeconds) {
    let marker = pharmacyDictionary[pharmacyName];
    if (marker) {
        let pin = marker.getElement();
        pin.style.transition = "transform " + animationSeconds + "s ease-in-out";
        pin.style.transform = "scale(1)";
        marker.setOffset([0, 0]);

        //if you don't set this timeout, once your mouse leaves the card the animation will end abruptly
        setTimeout(() => {
            pin.style.transition = "";
        }, animationSeconds*1000);//miliseconds
    }
}


let map = new maplibregl.Map({
    style: 'https://tiles.openfreemap.org/styles/bright',
    container: 'map',
    center: [-60.702068, -31.635],
    zoom: 12.7,
})

let farmacia = {
    nombre: "Acosta",
    direccion: "Suipacha 2506",
    telefono: "0342 - 455-6677",
    latitud: -31.640134534867073,
    longitud: -60.70403018834733
};
fetch("data/farmacias.json")
    .then(response => response.json())
    .then(data => {
        data.forEach(aPharmacy => {
            addPharmacy(aPharmacy);
            console.log(aPharmacy)})
    })
    .catch(error => console.error("Error loading JSON:", error));

addPharmacy(farmacia);
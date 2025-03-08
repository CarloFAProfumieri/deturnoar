let pinDictionary = {};
let cardDictionary = {};

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
        card.style.backgroundColor = "#d1f2eb";
    }
    scrollToCard(pharmacyName)

}

function scrollToCard(pharmacyName, callback) {
    let container = document.querySelector(".card-list");
    let cards = document.querySelectorAll(".card");

    cards.forEach(card => {
        if (card.querySelector("h4").textContent === pharmacyName) {
            card.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
            container.addEventListener("scroll", () => {
                let isScrolling;
                clearTimeout(isScrolling);
                isScrolling = setTimeout(() => {
                    console.log("Scrolling finished!");
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
    highlightCard(pharmacyName,animationSeconds);
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

let map = new maplibregl.Map({
    style: 'https://tiles.openfreemap.org/styles/bright',
    container: 'map',
    center: [-60.705, -31.630],
    zoom: 12.2,
})

let farmacia = {
    nombre: "Acosta",
    direccion: "Suipacha 2506",
    telefono: "0342 - 4556677",
    latitud: -31.640134534867073,
    longitud: -60.70403018834733
};
fetch("data/farmacias.json")
    .then(response => response.json())
    .then(data => {
        data.forEach(aPharmacy => {
            addPharmacy(aPharmacy);
            //console.log(aPharmacy)
            })
    })
    .catch(error => console.error("Error loading JSON:", error));

addPharmacy(farmacia);
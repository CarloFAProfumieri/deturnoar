function addCard(name, address, extraInformation){
    let nameNewNode = document.createElement("h4");
    let addressNewNode = document.createElement("h5");
    let extraInformationNewNode = document.createElement("p");
    let cardNewNode = document.createElement("div");
    let cardText = document.createElement("div");
    let pharmacyListNode = document.querySelector("#pharmacyList");
    let imageNode = document.createElement("img");

    cardNewNode.className = "card";
    cardText.className = "card-text";

    imageNode.src = "public/logo.svg";

    nameNewNode.textContent = name;
    addressNewNode.textContent= address;
    extraInformationNewNode.textContent = extraInformation;

    cardText.appendChild(nameNewNode);
    cardText.appendChild(addressNewNode);
    cardText.appendChild(extraInformationNewNode);
    cardNewNode.appendChild(imageNode);
    cardNewNode.appendChild(cardText);
    pharmacyListNode.appendChild(cardNewNode);
}

addCard("Bosch","Santiago del Estero 2764", "Atiende por IAPOS");
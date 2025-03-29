# deturno.ar

This project was created to display the shifts of my city's pharmacies on a map. You can access the webpage beta by clicking the link below:

🔗 [Visit deturno.ar](deturno.ar)
🔗 [Visit deturno.ar/santo-tome](deturno.ar/santo-tome)

---

## 📌 Why am I doing this?
Determining pharmacies' shifts in Argentina is a **legal requirement** for any **College of Pharmacists** in a given area. However, this does not mean that the information is easily accessible. More often than not, the shifts are presented in a way that **severely restricts usability**:

- The schedules are provided in an **image inside a PDF**, with **no alternative text**.
- The image **cannot be copied or clicked**, making it **unreadable for screen readers**.
- Addresses are only presented as **plain text**, making it difficult to determine the closest pharmacy unless you already know the entire city's street grid.
- This lack of accessibility is especially problematic for people in **urgent need of medication outside business hours**, who are often in a **critical situation**.

This project aims to **solve these issues** by providing an interactive and accessible map to easily find open pharmacies.

---

## 🛠️ How It Was Made
### **Frontend**
- Developed using just **HTML, CSS, JavaScript**, and Node.js live server
- The map module was built using **OpenStreetMap** (via OpenFreemap), which was extremely helpful since this project has been done with close to no budget
- **The page is responsive** and will place the map on top of the list in mobile view, this was a priority since the nature of the app will require mobile use. The buttons are touch friendly and a handle will appear if you open it in mobile!

### **Data Processing Pipeline (Precomputed Data)**
- **Python** was used to **scrape pharmacy data** (name, address, coordinates) from the local College of Pharmacists' website.
- The data was curated to remove inconsistencies.
- Each pharmacy was linked to a **Google Place ID** by searching the name and address via the **Google Places API**.
- The Place ID was then used to **retrieve updated phone numbers** for each pharmacy.
- The final data was saved in `data/pharmacies_with_phones.json`.

#### **Shift Extraction Process**
1. The **PDF file** from the College of Pharmacists was **converted to a PNG image**.
2. The image was **preprocessed using OpenCV**.
3. Text was extracted using **Tesseract OCR (pytesseract)**.
4. Errors in the OCR output were **corrected using regex and RapidFuzz**, since I already had a list of pharmacy names for spellchecking.
5. The final shift data was saved in `data/turnos.json`, which is then **consumed by the frontend** to display the pharmacies on the map.

---

## 🚀 Future Improvements
- **Better geolocation integration** for determining the nearest pharmacy via address search.
- More Locations
- Easy navigation button that pops up Google Maps to improve ease of use in mobile
- Report button to flag pharmacies that haven't actually stayed open on their shift (which is a relatively common ocurrency)
- Pipeline automation for the backend so the site run autonomously
---
<!--
## 📜 License
This project is open-source and available under the **MIT License**.

---
-->


## ♿ Accessibility
This was the central point of this project.

- The frontend was checked for **colorblindness accessibility** using the **Let's Get Colorblind** extension in Chrome, and later in Firefox because Chrome disabled Ublock Origin and now I hate Chrome.
- If you input any address in the search box, pharmacies are automatically sorted by closest first! :)
- The **HTML includes alternate text** to ensure **screen reader support**.
- The goal is to **get direct feedback from non-sighted individuals** to improve accessibility further.

## 💡 Contributions
Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

---

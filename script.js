let allItems = []; // stocke tous les éléments pour filtrer

// Fonction pour afficher la liste depuis Python
async function loadList() {
    allItems = await window.pywebview.api.get_items();
    displayList(allItems);
}

// Affiche une liste donnée
function displayList(items) {
    const ul = document.getElementById("ma-liste");
    ul.innerHTML = ""; // vide la liste
    items.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item;
        li.addEventListener("click", () => {
            document.querySelectorAll("#ma-liste li").forEach(el => el.classList.remove("selected"));
            li.classList.add("selected");
        });
        ul.appendChild(li);
    });
}

// Filtrer la liste à partir de la barre de recherche
document.getElementById("search").addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allItems.filter(item => item.toLowerCase().includes(query));
    displayList(filtered);
});

// Charger la liste quand PyWebview est prêt
window.addEventListener('pywebviewready', loadList);

// Bouton OK
document.getElementById("ok-btn").addEventListener("click", async () => {
    const selected = document.querySelector("#ma-liste li.selected");
    if (selected) {
        const response = await window.pywebview.api.item_selected(selected.textContent);
    } else {
        alert("Sélectionne un élément d'abord !");
    }
});

// Bouton Reload
document.getElementById("reload-btn").addEventListener("click", () => {
    location.reload();
});


document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
        if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
});


document.querySelectorAll("select[data-new-url]").forEach(function (select) {
    select.addEventListener("change", function () {
        if (select.value === "__new__") window.location.href = select.dataset.newUrl;
    });
});


var viewBox = document.querySelector("[data-view]");
var viewButtons = document.querySelectorAll("[data-view-btn]");
var setView = function (view) {
    if (viewBox) viewBox.dataset.view = view;
    viewButtons.forEach(function (b) { b.classList.toggle("active", b.dataset.viewBtn === view); });
    try { localStorage.setItem("libView", view); } catch (e) {}
};
var savedView = "list";
try { savedView = localStorage.getItem("libView") === "grid" ? "grid" : "list"; } catch (e) {}
setView(savedView);
viewButtons.forEach(function (b) {
    b.addEventListener("click", function () { setView(b.dataset.viewBtn); });
});


var modal = document.getElementById("authorModal");
if (modal) {
    var authorData = JSON.parse(document.getElementById("authorData").textContent);

    var closeModal = function () { modal.hidden = true; };
    var openModal = function (id) {
        var a = authorData[id];
        if (!a) return;
        var photo = document.getElementById("modalPhoto");
        photo.hidden = !a.photo;
        if (a.photo) photo.src = a.photo;
        document.getElementById("modalPhotoPh").hidden = !!a.photo;
        document.getElementById("modalName").textContent = a.name;
        document.getElementById("modalCountry").textContent = a.country;
        document.getElementById("modalCount").textContent =
            a.books.length === 0 ? "No books for this author yet." :
            "Books (" + a.books.length + ")";

        var list = document.getElementById("modalBooks");
        list.innerHTML = "";
        a.books.forEach(function (b) {
            var li = document.createElement("li");
            var cover = b.cover ? document.createElement("img") : document.createElement("span");
            cover.className = "thumb" + (b.cover ? "" : " ph");
            if (b.cover) { cover.src = b.cover; cover.alt = ""; }
            var title = document.createElement("span");
            title.className = "book-title";
            title.textContent = b.title;
            var price = document.createElement("span");
            price.className = "book-price";
            price.textContent = b.price;
            li.appendChild(cover); li.appendChild(title); li.appendChild(price);
            list.appendChild(li);
        });
        modal.hidden = false;
    };

    document.querySelectorAll("[data-author-id]").forEach(function (el) {
        el.addEventListener("click", function (e) {
            if (e.target.closest("a, button, form")) return;    
            openModal(el.dataset.authorId);
        });
    });
    modal.addEventListener("click", function (e) { if (e.target === modal) closeModal(); });
    modal.querySelector(".modal-close").addEventListener("click", closeModal);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });
}

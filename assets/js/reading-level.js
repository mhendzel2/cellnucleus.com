(function () {
    "use strict";

    var switchers = document.querySelectorAll("[data-reading-level-switcher]");
    if (!switchers.length) {
        return;
    }

    switchers.forEach(function (switcher) {
        switcher.addEventListener("click", function (event) {
            var link = event.target.closest("a[data-reading-level]");
            if (!link) {
                return;
            }
            try {
                window.localStorage.setItem("cellnucleus-reading-level", link.getAttribute("data-reading-level"));
            } catch (error) {
                return;
            }
        });
    });
}());

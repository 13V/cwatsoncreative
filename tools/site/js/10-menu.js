  // Menu. On phones it opens as a full screen, so the page behind is locked and set inert.
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var behind = document.querySelectorAll("main, .site-footer");
    var label = toggle.querySelector(".nav-toggle-label");
    var setMenu = function (open) {
      if (open === nav.classList.contains("is-open")) return;
      toggle.setAttribute("aria-expanded", String(open));
      if (label) label.textContent = open ? "Close" : "Menu";
      nav.classList.toggle("is-open", open);
      root.classList.toggle("menu-open", open);
      behind.forEach(function (el) { el.inert = open; });
      if (open) {
        var first = nav.querySelector("a[href]");
        if (first) first.focus({ preventScroll: true });
      }
    };
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
    // A link to somewhere on the same page closes the menu (other links leave the page anyway).
    nav.addEventListener("click", function (event) {
      var link = event.target.closest && event.target.closest("a[href]");
      if (link && nav.classList.contains("is-open") && link.getAttribute("href").charAt(0) === "#") setMenu(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        setMenu(false);
        toggle.focus();
      }
    });
    if (window.matchMedia) { // widening the window past the phone layout closes it
      var wide = window.matchMedia("(min-width: 861px)");
      var onWide = function () { if (wide.matches) setMenu(false); };
      if (wide.addEventListener) wide.addEventListener("change", onWide);
      else if (wide.addListener) wide.addListener(onWide);
    }
  }


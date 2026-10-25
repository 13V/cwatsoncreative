
  // Phone menu (M07): below 861px the shut sheet is inert; open, the page behind is.
  var toggle = document.querySelector(".nav-toggle"), nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var behind = document.querySelectorAll("main, .site-footer, .skip");
    var label = toggle.querySelector(".nav-toggle-label");
    var phone = matchMedia("(max-width: 860px)");
    var isOpen = function () { return nav.classList.contains("is-open"); };
    var setMenu = function (open) {
      nav.inert = !open && phone.matches;
      if (open === isOpen()) return;
      if (open && M.showHeader) M.showHeader(true);   // never in a moving header
      toggle.setAttribute("aria-expanded", String(open));
      if (label) label.textContent = open ? "Close" : "Menu";
      nav.classList.toggle("is-open", open);
      root.classList.toggle("menu-open", open);
      behind.forEach(function (el) { el.inert = open; });
      if (open) { var first = nav.querySelector("a[href]"); if (first) first.focus({ preventScroll: true }); }
    };
    toggle.addEventListener("click", function () { setMenu(!isOpen()); });
    // same-page links close it (the page change reads .menu-open)
    nav.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a[href]");
      if (a && a.getAttribute("href").charAt(0) === "#") setMenu(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) { setMenu(false); toggle.focus(); }
    });
    var onWidth = function () { setMenu(isOpen() && phone.matches); };
    phone.addEventListener("change", onWidth);
    onWidth();
  }

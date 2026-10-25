
  // Header (§4.2): hides going down, back going up; never near the top, menu open, focus inside or no motion.
  // html.header-hidden moves the index bar.
  var siteHeader = document.querySelector(".site-header");
  if (siteHeader) {
    var lastY = Math.max(0, scrollY), ticking = false;
    var hideHeader = function (hide, now) {
      if (now) siteHeader.style.transition = "none";
      siteHeader.classList.toggle("is-hidden", hide);
      root.classList.toggle("header-hidden", hide);
      if (now) { void siteHeader.offsetWidth; siteHeader.style.transition = ""; }
    };
    M.showHeader = function (now) { hideHeader(false, now); };
    var updateHeader = function () {
      var y = Math.max(0, scrollY), dy = y - lastY;
      ticking = false;
      siteHeader.classList.toggle("is-scrolled", y > 0);
      if (Math.abs(dy) <= 6) return;
      hideHeader(dy > 0 && y > siteHeader.offsetHeight * 2 && motionOK() && !root.classList.contains("menu-open") &&
        !siteHeader.contains(document.activeElement));
      lastY = y;
    };
    addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(updateHeader); }
    }, { passive: true });
    siteHeader.addEventListener("focusin", function () { M.showHeader(); });
    updateHeader();
  }

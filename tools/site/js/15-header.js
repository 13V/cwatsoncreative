
  // Header: sticky. It gains a hairline once the page has scrolled, slides away while you scroll down and comes back
  // as soon as you scroll up. It never hides near the top, while the menu is open or while it holds focus, and never
  // with reduced motion or "Hold still", where it simply stays.
  var siteHeader = document.querySelector(".site-header");
  if (siteHeader) {
    var lastY = Math.max(0, window.scrollY || 0), ticking = false;
    var updateHeader = function () {
      ticking = false;
      var y = Math.max(0, window.scrollY || 0), dy = y - lastY;
      siteHeader.classList.toggle("is-scrolled", y > 0);
      if (Math.abs(dy) <= 6) return;
      var tall = siteHeader.offsetHeight * 2;
      var hide = dy > 0 && y > tall && motionOK() && !root.classList.contains("menu-open") && !siteHeader.contains(document.activeElement);
      siteHeader.classList.toggle("is-hidden", hide);
      root.classList.toggle("header-hidden", hide);
      lastY = y;
    };
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(updateHeader); }
    }, { passive: true });
    siteHeader.addEventListener("focusin", function () { siteHeader.classList.remove("is-hidden"); root.classList.remove("header-hidden"); });
    updateHeader();
  }

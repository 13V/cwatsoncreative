  // Photo viewer: arrows, keys and swipes; the next photo loads while you look at this one.
  var viewer = document.querySelector(".lightbox");
  var links = Array.prototype.slice.call(document.querySelectorAll(".masonry a[data-lightbox]"));
  if (viewer && links.length && typeof viewer.showModal === "function") {
    var figure = viewer.querySelector(".lb-figure");
    figure.innerHTML = '<picture><source type="image/webp"><img alt=""></picture>';
    var big = figure.querySelector("img");
    var bigSource = figure.querySelector("source");
    var preload = document.createElement("picture");
    preload.hidden = true;
    preload.innerHTML = '<source type="image/webp"><img alt="">';
    viewer.appendChild(preload);
    var count = viewer.querySelector(".lb-count");
    var live = viewer.querySelector(".lb-live");
    var current = 0;
    var two = function (n) { return (n < 10 ? "0" : "") + n; };
    var visible = function () {
      return links.filter(function (link) { return !link.closest(".ph").classList.contains("is-missing"); });
    };
    var load = function (picture, href) {
      picture.querySelector("source").setAttribute("srcset", href.replace(/\.jpe?g$/i, ".webp"));
      picture.querySelector("img").src = href;
    };
    big.addEventListener("load", function () { big.classList.remove("is-switching"); });
    big.addEventListener("error", function () {
      if (bigSource.hasAttribute("srcset")) bigSource.removeAttribute("srcset"); // no WebP copy, so use the JPEG
      else big.classList.remove("is-switching");
    });
    var show = function (index) {
      var list = visible();
      if (!list.length) return;
      current = (index + list.length) % list.length;
      var link = list[current];
      var thumb = link.querySelector("img");
      big.classList.add("is-switching");
      load(figure.querySelector("picture"), link.getAttribute("href"));
      big.alt = thumb.alt;
      count.textContent = two(current + 1) + " / " + two(list.length);
      live.textContent = "Photo " + (current + 1) + " of " + list.length + ": " + thumb.alt;
      load(preload, list[(current + 1) % list.length].getAttribute("href"));
    };
    links.forEach(function (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        show(visible().indexOf(link));
        viewer.showModal();
        root.classList.add("viewer-open");
      });
    });
    viewer.addEventListener("close", function () { root.classList.remove("viewer-open"); });
    viewer.querySelector(".lb-prev").addEventListener("click", function () { show(current - 1); });
    viewer.querySelector(".lb-next").addEventListener("click", function () { show(current + 1); });
    viewer.querySelector(".lb-close").addEventListener("click", function () { viewer.close(); });
    viewer.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") show(current - 1);
      if (event.key === "ArrowRight") show(current + 1);
    });
    viewer.addEventListener("click", function (event) { // a tap beside the photo closes it
      if (event.target === viewer || event.target === figure || event.target.classList.contains("lightbox-inner")) viewer.close();
    });
    var startX = null;
    var startY = 0;
    viewer.addEventListener("touchstart", function (event) {
      var zoomed = window.visualViewport && window.visualViewport.scale > 1.01;
      if (event.touches.length !== 1 || zoomed) { startX = null; return; }
      startX = event.touches[0].clientX;
      startY = event.touches[0].clientY;
    }, { passive: true });
    viewer.addEventListener("touchend", function (event) { // swipe sideways for the next photo, down to close
      if (startX === null) return;
      var dx = event.changedTouches[0].clientX - startX;
      var dy = event.changedTouches[0].clientY - startY;
      startX = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.3) show(current + (dx < 0 ? 1 : -1));
      else if (dy > 90 && dy > Math.abs(dx) * 1.5) viewer.close();
    }, { passive: true });
  }


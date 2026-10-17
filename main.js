// Sunday Light: menu, photos, gentle reveals, the sessions list, the photo viewer and the enquiry form.
(function () {
  "use strict";
  var root = document.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Menu. On phones it opens as a full screen, so the page behind is locked and set inert.
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var behind = document.querySelectorAll("main, .site-footer");
    var setMenu = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
      root.classList.toggle("menu-open", open);
      behind.forEach(function (el) { el.inert = open; });
    };
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        setMenu(false);
        toggle.focus();
      }
    });
    if (window.matchMedia) { // widening the window past the phone layout closes it
      var wide = window.matchMedia("(min-width: 821px)");
      var onWide = function () { if (wide.matches) setMenu(false); };
      if (wide.addEventListener) wide.addEventListener("change", onWide);
      else if (wide.addListener) wide.addListener(onWide);
    }
  }

  // Photos: the WebP copies first, then the JPEG, then the landscape art if the file has gone.
  var photoFailed = function (image) {
    var picture = image.parentNode;
    var sources = picture && picture.nodeName === "PICTURE" ? picture.querySelectorAll("source") : [];
    if (sources.length) {
      sources.forEach(function (source) { picture.removeChild(source); }); // the browser retries with the JPEG
      return;
    }
    var figure = image.closest(".ph");
    if (figure) figure.classList.add("is-missing");
  };
  document.querySelectorAll(".ph img").forEach(function (image) {
    image.addEventListener("load", function () { image.classList.add("is-loaded"); });
    image.addEventListener("error", function () { photoFailed(image); });
    if (image.complete) {
      if (image.naturalWidth) image.classList.add("is-loaded");
      else photoFailed(image);
    }
  });
  root.classList.add("fade-ready"); // photos that haven't arrived yet now fade in when they do

  // Sections ease in as they scroll into view. Anything already on screen is left alone.
  if ("IntersectionObserver" in window && !reduceMotion) {
    var staggered = ".tiles, .steps, .duo-grid, .faq";
    var targets = document.querySelectorAll(
      ".quote .wrap > *, .intro-grid > *, .duo a, .center-title, .tiles li, .center, .words, .package, .review, " +
      ".steps li, .faq details, .aside > div, .gallery-head, .text > *"
    );
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -6% 0px" });
    targets.forEach(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) return;
      if (el.parentNode.matches && el.parentNode.matches(staggered)) {
        var index = Array.prototype.indexOf.call(el.parentNode.children, el);
        el.style.transitionDelay = (index % 4) * 90 + "ms";
        el.addEventListener("transitionend", function () { el.style.transitionDelay = ""; }, { once: true });
      }
      el.classList.add("reveal");
      observer.observe(el);
    });
  }

  // Kind words: one review at a time, with arrows and swipes.
  document.querySelectorAll(".words").forEach(function (box) {
    var items = box.querySelectorAll(".words-item");
    var photos = box.querySelectorAll(".words-photo");
    var count = box.querySelector(".words-count");
    if (items.length < 2 || !count) return;
    var current = 0;
    var go = function (index) {
      current = (index + items.length) % items.length;
      items.forEach(function (item, i) { item.classList.toggle("is-current", i === current); });
      photos.forEach(function (photo, i) { photo.classList.toggle("is-current", i === current); });
      count.textContent = (current + 1) + " / " + items.length;
    };
    box.querySelector(".words-prev").addEventListener("click", function () { go(current - 1); });
    box.querySelector(".words-next").addEventListener("click", function () { go(current + 1); });
    var startX = null;
    var startY = 0;
    box.addEventListener("touchstart", function (event) {
      if (event.touches.length !== 1) { startX = null; return; }
      startX = event.touches[0].clientX;
      startY = event.touches[0].clientY;
    }, { passive: true });
    box.addEventListener("touchend", function (event) {
      if (startX === null) return;
      var dx = event.changedTouches[0].clientX - startX;
      var dy = event.changedTouches[0].clientY - startY;
      startX = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.3) go(current + (dx < 0 ? 1 : -1));
    }, { passive: true });
  });

  // Contact: "Enquire about…" links arrive with the session already chosen.
  var sessionField = document.getElementById("session");
  if (sessionField && window.URLSearchParams) {
    var wanted = new URLSearchParams(location.search).get("session");
    Array.prototype.forEach.call(sessionField.options, function (option) {
      if (wanted && option.value === wanted) sessionField.value = option.value;
    });
  }

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

  // Enquiry form: posts JSON to the webhook in data-endpoint.
  var form = document.getElementById("enquiry-form");
  if (form) {
    var status = document.getElementById("form-status");
    var failure = document.getElementById("form-error");
    var success = document.getElementById("form-success");
    var button = form.querySelector('button[type="submit"]');
    var sending = false;
    var emailOk = function (value) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value); };

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (sending) return;
      failure.hidden = true;
      var firstProblem = null;
      ["name", "email", "message"].forEach(function (name) {
        var field = form.elements[name];
        var value = field.value.trim();
        var bad = !value || (name === "email" && !emailOk(value));
        if (bad) {
          field.setAttribute("aria-invalid", "true");
          firstProblem = firstProblem || field;
        } else {
          field.removeAttribute("aria-invalid");
        }
      });
      if (firstProblem) {
        status.textContent = "Please add your name, a valid email and a short message.";
        firstProblem.focus();
        return;
      }
      if (form.elements.company.value) { // filled in by bots only
        form.hidden = true;
        success.hidden = false;
        return;
      }
      var data = {};
      new FormData(form).forEach(function (value, key) {
        if (key !== "company") data[key] = String(value).trim();
      });
      data.submitted = new Date().toISOString();
      data.source = location.host + location.pathname;

      sending = true;
      button.disabled = true;
      status.textContent = "Sending…";
      var controller = typeof AbortController === "function" ? new AbortController() : null;
      var timer = controller ? setTimeout(function () { controller.abort(); }, 20000) : null;
      fetch(form.getAttribute("data-endpoint"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        signal: controller ? controller.signal : undefined
      }).then(function (response) {
        if (!response.ok) throw new Error("Enquiry failed");
        status.textContent = "";
        form.hidden = true;
        success.hidden = false;
        success.querySelector("h2").focus();
      }).catch(function () {
        status.textContent = "";
        failure.hidden = false;
        failure.focus();
      }).then(function () {
        if (timer) clearTimeout(timer);
        sending = false;
        button.disabled = false;
      });
    });
  }

  document.querySelectorAll("[data-year]").forEach(function (node) {
    node.textContent = String(new Date().getFullYear());
  });
})();

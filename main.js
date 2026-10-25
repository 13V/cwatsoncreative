// Sunday Light. Built from tools/site/js/ by tools/site/build.py: edit the parts there.
// Sunday Light: motion kernel, menu, photos, the kind words slider, the photo viewer, the enquiry form and the
// golden-hour clock. The page's finished, still state is the CSS default; motion only ever starts from .m.
(function () {
  "use strict";
  var root = document.documentElement;
  var reduceQuery = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var motionOK = function () { return root.classList.contains("m"); };

  // ---------------------------------------------------------------- motion kernel
  // One observer plays every one-shot moment. Anything on screen when first seen stays finished; anything below the
  // fold is armed (put in its start state while off-screen) and plays once when enough of it arrives. The shared
  // pieces live on window.SL so later parts (and the tests) can use them.
  var M = window.SL = {};
  M.motionOK = motionOK;
  var wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  M.wait = wait;

  // Queues: at most two lines drawing and four photos developing at once, with a small gap between starts.
  var Q = { draw: { n: 2, gap: 120, busy: 0, last: 0, wait: [] }, print: { n: 4, gap: 100, busy: 0, last: 0, wait: [] } };
  var pump = function (q) {
    if (q.busy >= q.n || !q.wait.length || q.timer) return;
    q.timer = setTimeout(function () {
      var job = q.wait.shift();
      q.timer = 0; q.busy++; q.last = performance.now();
      Promise.race([Promise.resolve().then(job[0]), wait(job[1] + 150)]).then(function () { q.busy--; pump(q); }, function () { q.busy--; pump(q); });
      pump(q);
    }, Math.max(0, q.last + q.gap - performance.now()));
  };
  M.queue = function (kind, start, ms) { var q = Q[kind]; q.wait.push([start, ms]); pump(q); };

  var jobs = new Map();
  var seen = typeof WeakSet === "function" ? new WeakSet() : null;
  M.done = function (el) {
    el.classList.remove("is-armed", "is-developing");
    el.classList.add("is-done");
    if (observer) observer.unobserve(el);
    jobs.delete(el);
  };
  var observer = ("IntersectionObserver" in window && seen) ? new IntersectionObserver(function (entries) {
    var ready = [];
    entries.forEach(function (entry) {
      var el = entry.target, list = jobs.get(el);
      if (!list) return;
      if (!seen.has(el)) {
        seen.add(el);
        if (entry.isIntersecting || !motionOK()) {
          // On screen at first sight: finished, except jobs whose start state is in the CSS from first paint.
          list = list.filter(function (job) { return job.fromStart && motionOK(); });
          if (!list.length) { M.done(el); return; }
          jobs.set(el, list);
        } else {
          el.classList.add("is-armed");
          return;
        }
      }
      var view = entry.rootBounds ? entry.rootBounds.height : window.innerHeight;
      list.forEach(function (job) {
        if (job.done) return;
        if (entry.intersectionRatio >= job.ratio || (entry.isIntersecting && entry.intersectionRect.height >= job.ratio * view)) {
          job.done = true;
          ready.push([entry.boundingClientRect, el, job]);
        }
      });
      if (list.every(function (job) { return job.done; })) { observer.unobserve(el); jobs.delete(el); }
    });
    // Reading order: by on-screen top (to the nearest 8px), then left.
    ready.sort(function (a, b) { return (Math.round(a[0].top / 8) - Math.round(b[0].top / 8)) || (a[0].left - b[0].left); })
      .forEach(function (r) { Promise.resolve(window.slSettled).then(function () { r[2].run(r[1]); }); });
  }, { threshold: [0, .05, .1, .15, .2, .25, .3, .5, .75, .9, 1] }) : null;
  // Register a job: run(el) once when `ratio` of el is in view (or that share of the screen is filled by it).
  M.once = function (el, ratio, run, fromStart) {
    if (!observer || !el) return;
    var list = jobs.get(el);
    if (!list) { list = []; jobs.set(el, list); observer.observe(el); }
    list.push({ ratio: ratio, run: run, done: false, fromStart: !!fromStart });
  };
  var once = M.once;

  // The one animation allowed without motion: a 150ms fade for things that appear from or leave to display: none.
  M.calm = function (el, dir) {
    if (!el || !el.animate) return Promise.resolve();
    var a = el.animate({ opacity: dir === "in" ? [0, 1] : [1, 0] }, { duration: 150, easing: "linear", fill: dir === "in" ? "none" : "forwards" });
    return a.finished.then(function () { return a; }, function () {});
  };

  // Everything jumps to its finished frame (Hold still pressed, or reduced motion switched on mid-visit).
  var settle = function (hold) {
    if (hold) root.classList.add("still");   // first: the kill switch now cancels every CSS animation and transition
    root.classList.remove("m");
    if (document.getAnimations) document.getAnimations().forEach(function (a) {
      var t = a.effect && a.effect.getTiming ? a.effect.getTiming() : {};
      try { if (t.iterations === Infinity) throw 0; a.finish(); } catch (e) { a.cancel(); }
    });
    document.querySelectorAll(".is-armed").forEach(M.done);
  };
  var isStill = function () { return root.classList.contains("still"); };
  var stillButton = document.querySelector(".still-toggle");
  var syncStill = function () {
    if (!stillButton) return;
    stillButton.setAttribute("aria-pressed", String(isStill()));
    stillButton.parentNode.hidden = !!(reduceQuery && reduceQuery.matches);   // it could change nothing
  };
  if (stillButton) {
    syncStill();
    stillButton.addEventListener("click", function () {
      var on = !isStill();
      try { localStorage.setItem("sl-still", on ? "1" : "0"); } catch (e) {}
      if (on) settle(true);
      else { root.classList.remove("still"); if (!(reduceQuery && reduceQuery.matches)) root.classList.add("m"); }
      syncStill();
    });
  }
  if (reduceQuery) {
    var onPreference = function () {
      if (reduceQuery.matches) settle(false);
      else if (!isStill()) root.classList.add("m");
      syncStill();
    };
    if (reduceQuery.addEventListener) reduceQuery.addEventListener("change", onPreference);
    else if (reduceQuery.addListener) reduceQuery.addListener(onPreference);
  }

  // Through the arch: remember where a link was tapped (or which doorway), then hand over as the page leaves.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]"), W = window.innerWidth, r, d, b;
    if (!a || e.defaultPrevented || a.target || a.hasAttribute("download") || a.origin !== location.origin) return;
    r = { at: Date.now(), hash: !!a.hash };
    d = a.querySelector("[data-door]"); b = d && d.getBoundingClientRect();
    if (b && b.top >= 0 && b.bottom <= window.innerHeight) {
      r.x = (b.left + b.width / 2) / W * 100 + "%"; r.top = b.top + "px"; r.w = b.width + "px"; r.h = b.height + "px";
    } else r.x = (e.detail ? Math.min(80, Math.max(20, e.clientX / W * 100)) : 50) + "%";   // keyboard: centre
    try { sessionStorage.setItem("sl-vt", JSON.stringify(r)); } catch (x) {}
  });
  window.addEventListener("pageswap", function (e) {
    var vt = e.viewTransition, r = {}, c = root.classList, hd;
    if (!vt) return;
    if (e.activation && /traverse|reload/.test(e.activation.navigationType)) { vt.skipTransition(); return; }
    try { r = JSON.parse(sessionStorage.getItem("sl-vt") || "{}"); } catch (x) {}
    r.quiet = c.contains("menu-open") || !!r.hash;
    hd = document.querySelector(".site-header");
    r.keep = !r.quiet && !!hd && hd.getBoundingClientRect().top > -1;
    c.toggle("vt-keep", r.keep);   // toggle, never just add: a restored page must not keep it
    try { sessionStorage.setItem("sl-vt", JSON.stringify(r)); } catch (x) {}
  });
  // iOS only applies :active reliably when a touch listener exists, and every tap should answer within a frame.
  document.addEventListener("touchstart", function () {}, { passive: true });

  // Ruled in: eyebrow dashes and the rules of steps, questions, the contact column and the wedding tiers.
  var draw = function (el) { el.classList.add("is-drawn"); };
  document.querySelectorAll(".eyebrow, [data-rules]").forEach(function (el) { once(el, .25, draw); });
  // Sundown: the footer's gold line draws once when the scene is in view; where scroll timelines are missing, the
  // sunset also plays once.
  var sundown = document.querySelector(".sundown");
  once(sundown, .9, function (el) {
    M.queue("draw", function () { el.classList.add("is-drawn"); return wait(2300); }, 2300);
  });
  once(sundown, .5, function (el) { el.classList.add("is-dusk"); });
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

  // ---------------------------------------------------------------- golden hour in Adelaide
  // NOAA sunset equation for Adelaide; golden hour is taken as the hour before sunset. Shown in Adelaide time.
  var golden = document.querySelector("[data-golden]");
  var sunsetMinutesUTC = function (y, m, d) {
    var rad = Math.PI / 180, lat = -34.9285, lng = 138.6007;
    var t = (Date.UTC(y, m - 1, d) / 86400000 + 2440587.5 - 2451545) / 36525;
    var L0 = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360;
    var M = 357.52911 + t * (35999.05029 - 0.0001537 * t);
    var ecc = 0.016708634 - t * (0.000042037 + 0.0000001267 * t);
    var C = Math.sin(M * rad) * (1.914602 - t * (0.004817 + 0.000014 * t)) + Math.sin(2 * M * rad) * (0.019993 - 0.000101 * t) +
      Math.sin(3 * M * rad) * 0.000289;
    var omega = 125.04 - 1934.136 * t;
    var lambda = L0 + C - 0.00569 - 0.00478 * Math.sin(omega * rad);
    var eps = 23 + (26 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60) / 60 + 0.00256 * Math.cos(omega * rad);
    var decl = Math.asin(Math.sin(eps * rad) * Math.sin(lambda * rad));
    var yy = Math.pow(Math.tan(eps / 2 * rad), 2);
    var eqTime = 4 / rad * (yy * Math.sin(2 * L0 * rad) - 2 * ecc * Math.sin(M * rad) + 4 * ecc * yy * Math.sin(M * rad) * Math.cos(2 * L0 * rad) -
      0.5 * yy * yy * Math.sin(4 * L0 * rad) - 1.25 * ecc * ecc * Math.sin(2 * M * rad));
    var ha = Math.acos(Math.cos(90.833 * rad) / (Math.cos(lat * rad) * Math.cos(decl)) - Math.tan(lat * rad) * Math.tan(decl)) / rad;
    return 720 - 4 * lng - eqTime + 4 * ha;
  };
  window.slSunset = sunsetMinutesUTC; // for checking against published tables
  var showGoldenHour = function () {
    if (!golden || !window.Intl || !Intl.DateTimeFormat) return;
    try {
      var zone = "Australia/Adelaide";
      var dateParts = function (when) {
        var parts = {};
        new Intl.DateTimeFormat("en-AU", { timeZone: zone, year: "numeric", month: "numeric", day: "numeric" })
          .formatToParts(when).forEach(function (p) { parts[p.type] = Number(p.value); });
        return parts;
      };
      var sunsetOn = function (when) {
        var p = dateParts(when);
        return Date.UTC(p.year, p.month - 1, p.day) + sunsetMinutesUTC(p.year, p.month, p.day) * 60000;
      };
      var time = new Intl.DateTimeFormat("en-AU", { timeZone: zone, hour: "numeric", minute: "2-digit" });
      var now = Date.now(), sunset = sunsetOn(new Date(now)), start = sunset - 3600000, text;
      if (!isFinite(sunset)) return;
      if (now < start) text = "Golden hour in Adelaide tonight \u00b7 from " + time.format(start);
      else if (now < sunset) text = "Golden hour in Adelaide now \u00b7 until " + time.format(sunset);
      else text = "Golden hour tomorrow \u00b7 from " + time.format(sunsetOn(new Date(now + 86400000)) - 3600000);
      golden.classList.add("is-swapping");
      setTimeout(function () { golden.textContent = text; golden.classList.remove("is-swapping"); }, motionOK() ? 300 : 0);
    } catch (e) {}
  };
  // Only worked out as the footer comes near: the time-zone formatter is costly to create on a slow phone.
  if (golden) {
    var later = function () {
      if ("requestIdleCallback" in window) requestIdleCallback(showGoldenHour, { timeout: 1500 });
      else setTimeout(showGoldenHour, 200);
    };
    if ("IntersectionObserver" in window) {
      var near = new IntersectionObserver(function (entries) {
        if (!entries.some(function (entry) { return entry.isIntersecting; })) return;
        near.disconnect();
        later();
      }, { rootMargin: "0px 0px 900px 0px" });
      near.observe(golden);
    } else later();
  }
})();

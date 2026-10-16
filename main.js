// Sunday Light: menu, photo slots, gallery viewer and the enquiry form.
(function () {
  "use strict";

  // Mobile menu
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        toggle.click();
        toggle.focus();
      }
    });
  }

  // Photo slots: a missing file shows the arch placeholder, and galleries hide it.
  function updateGalleries() {
    document.querySelectorAll(".gallery").forEach(function (gallery) {
      var figures = gallery.querySelectorAll(".masonry .ph");
      var shown = 0;
      figures.forEach(function (figure) {
        if (!figure.classList.contains("is-missing")) shown += 1;
      });
      gallery.classList.toggle("is-empty", figures.length > 0 && shown === 0);
      var chip = document.querySelector('.chips a[href="#' + gallery.id + '"]');
      if (chip) chip.hidden = shown === 0;
    });
  }
  function markMissing(image) {
    var figure = image.closest(".ph");
    if (figure) figure.classList.add("is-missing");
    updateGalleries();
  }
  document.querySelectorAll(".ph img").forEach(function (image) {
    if (image.complete && image.naturalWidth === 0) markMissing(image);
    else image.addEventListener("error", function () { markMissing(image); }, { once: true });
  });

  // Each gallery checks its first photo straight away, so an empty gallery hides before anyone scrolls to it.
  document.querySelectorAll(".gallery").forEach(function (gallery) {
    var first = gallery.querySelector(".masonry img");
    if (!first) return;
    gallery.classList.add("is-probing");
    var probe = new Image();
    probe.onload = function () { gallery.classList.remove("is-probing"); };
    probe.onerror = function () {
      gallery.classList.remove("is-probing");
      gallery.querySelectorAll(".masonry .ph").forEach(function (figure) { figure.classList.add("is-missing"); });
      updateGalleries();
    };
    probe.src = first.getAttribute("src");
  });

  // Gallery viewer
  var viewer = document.querySelector(".lightbox");
  var links = Array.prototype.slice.call(document.querySelectorAll(".masonry a[data-lightbox]"));
  if (viewer && links.length && typeof viewer.showModal === "function") {
    var big = viewer.querySelector("img");
    var caption = viewer.querySelector("figcaption");
    var current = 0;
    var visible = function () {
      return links.filter(function (link) { return !link.closest(".ph").classList.contains("is-missing"); });
    };
    var show = function (index) {
      var list = visible();
      if (!list.length) return;
      current = (index + list.length) % list.length;
      var link = list[current];
      var thumb = link.querySelector("img");
      big.src = link.getAttribute("href");
      big.alt = thumb.alt;
      caption.textContent = thumb.alt;
    };
    links.forEach(function (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        show(visible().indexOf(link));
        viewer.showModal();
      });
    });
    viewer.querySelector(".lb-prev").addEventListener("click", function () { show(current - 1); });
    viewer.querySelector(".lb-next").addEventListener("click", function () { show(current + 1); });
    viewer.querySelector(".lb-close").addEventListener("click", function () { viewer.close(); });
    viewer.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") show(current - 1);
      if (event.key === "ArrowRight") show(current + 1);
    });
    viewer.addEventListener("click", function (event) {
      if (event.target === viewer || event.target.classList.contains("lightbox-inner")) viewer.close();
    });
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

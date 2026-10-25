
  // Photos: WebP, then the JPEG, then .is-missing.
  var photoFailed = function (img) {
    var pic = img.parentNode, ph = img.closest(".ph"), sources = pic.querySelectorAll("source");
    if (sources.length) sources.forEach(function (s) { pic.removeChild(s); });
    else if (ph) ph.classList.add("is-missing");
  };
  document.querySelectorAll(".ph img").forEach(function (img) {
    img.addEventListener("load", function () { img.classList.add("is-loaded"); });
    img.addEventListener("error", function () { photoFailed(img); });
    if (img.complete) { if (img.naturalWidth) img.classList.add("is-loaded"); else photoFailed(img); }
  });
  // Prints in the tray (M10): develops at 20% once decoded; not decoded in 2.5s, missing or done: the veil just goes.
  document.querySelectorAll(".ph--tray").forEach(function (ph) {
    var img = ph.querySelector("img"), armed = function () { return ph.classList.contains("is-armed"); };
    if (img) once(ph, .2, function () {
      M.queue("print", function () {
        if (!armed()) return;
        return Promise.race([img.decode().then(function () { return 1; }), wait(2500)]).then(function (ok) {
          if (!ok || !motionOK() || !armed() || ph.classList.contains("is-missing")) return M.done(ph);
          return new Promise(function (resolve) {
            var end = function (e) {
              if (e && e.target !== img) return;
              img.removeEventListener("transitionend", end);
              M.done(ph); resolve();
            };
            requestAnimationFrame(function () {
              img.addEventListener("transitionend", end);
              ph.classList.add("is-developing");
              setTimeout(end, 1550);
            });
          });
        }, function () { M.done(ph); });
      }, 3900);
    });
  });

// Sunday Light: motion kernel, menu, photos, the kind words slider, the photo viewer, the enquiry form and the
// golden-hour clock. The page's finished, still state is the CSS default; motion only ever starts from .m.
(function () {
  "use strict";
  var root = document.documentElement;
  var reduceQuery = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var motionOK = function () { return root.classList.contains("m"); };

  // ---------------------------------------------------------------- motion kernel
  // One observer for every one-shot moment. Anything on screen when first seen stays finished; anything below the
  // fold is armed (put in its start state while off-screen) and plays once when enough of it arrives.
  var jobs = new Map();
  var seen = typeof WeakSet === "function" ? new WeakSet() : null;
  var settled = function () { return window.slSettled || Promise.resolve(); };
  var observer = ("IntersectionObserver" in window) ? new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var el = entry.target, list = jobs.get(el);
      if (!list) return;
      if (seen && !seen.has(el)) {
        seen.add(el);
        if (entry.isIntersecting || !motionOK()) { jobs.delete(el); observer.unobserve(el); return; }
        el.classList.add("is-armed");
        return;
      }
      list.forEach(function (job) {
        if (job.done || entry.intersectionRatio < job.ratio) return;
        job.done = true;
        settled().then(function () { job.run(el); });
      });
      if (list.every(function (job) { return job.done; })) { jobs.delete(el); observer.unobserve(el); }
    });
  }, { threshold: [0, .1, .2, .25, .3] }) : null;
  var once = function (el, ratio, run) {
    if (!observer || !seen || !el) return;
    var list = jobs.get(el);
    if (!list) { list = []; jobs.set(el, list); observer.observe(el); }
    list.push({ ratio: ratio, run: run, done: false });
  };
  // Everything jumps to its finished frame (reduced motion switched on, or "Hold still").
  var settleAll = function () {
    root.classList.remove("m");
    if (document.getAnimations) document.getAnimations().forEach(function (a) { try { a.finish(); } catch (e) { a.cancel(); } });
    document.querySelectorAll(".is-armed").forEach(function (el) { el.classList.add("is-done"); });
  };
  var stillButton = document.querySelector(".still-toggle");
  var isStill = function () { return root.classList.contains("still"); };
  if (stillButton) {
    stillButton.setAttribute("aria-pressed", String(isStill()));
    stillButton.addEventListener("click", function () {
      var on = !isStill();
      root.classList.toggle("still", on);
      stillButton.setAttribute("aria-pressed", String(on));
      try { localStorage.setItem("sl-still", on ? "1" : "0"); } catch (e) {}
      if (on) settleAll();
      else if (!(reduceQuery && reduceQuery.matches)) root.classList.add("m");
    });
  }
  if (reduceQuery) {
    var onPreference = function () {
      if (reduceQuery.matches) settleAll();
      else if (!isStill()) root.classList.add("m");
    };
    if (reduceQuery.addEventListener) reduceQuery.addEventListener("change", onPreference);
    else if (reduceQuery.addListener) reduceQuery.addListener(onPreference);
  }
  var draw = function (el) { el.classList.add("is-drawn"); };

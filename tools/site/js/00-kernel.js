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


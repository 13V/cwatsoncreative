// Sunday Light. The finished, still page is the CSS default; motion only starts from html.m (motion plan §5).
(function () {
  "use strict";
  var root = document.documentElement;
  var reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var motionOK = function () { return root.classList.contains("m"); };
  var M = window.SL = { motionOK: motionOK };
  var wait = M.wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };

  // Queues: 2 lines draw, 4 prints develop at once, starts a gap apart; a slot frees when start() settles or after ms+150.
  var Q = { draw: { n: 2, gap: 120, busy: 0, last: 0, wait: [] }, print: { n: 4, gap: 100, busy: 0, last: 0, wait: [] } };
  var pump = function (q) {
    if (q.busy >= q.n || !q.wait.length || q.timer) return;
    q.timer = setTimeout(function () {
      var job = q.wait.shift(), free = function () { q.busy--; pump(q); };
      q.timer = 0; q.busy++; q.last = performance.now();
      Promise.race([Promise.resolve().then(job[0]), wait(job[1] + 150)]).then(free, free);
      pump(q);
    }, Math.max(0, q.last + q.gap - performance.now()));
  };
  M.queue = function (kind, start, ms) { var q = Q[kind]; q.wait.push([start, ms]); pump(q); };

  // One observer plays every one-shot: on screen at first sight it is done; below the fold armed until `ratio` is seen.
  // A cold load at #id jumps after the observer's first look, so that look judges where the jump lands.
  var jobs = new Map(), seen = new WeakSet(), land = document.getElementById(location.hash.slice(1));
  M.done = function (el) {
    el.classList.remove("is-armed", "is-developing");
    el.classList.add("is-done");
    if (observer) observer.unobserve(el);
    jobs.delete(el);
  };
  var observer = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    var ready = [], r, top = land ? Math.min(land.getBoundingClientRect().top - (parseFloat(getComputedStyle(root).scrollPaddingTop) || 0),
      root.scrollHeight - innerHeight - scrollY) : null;
    land = null;
    entries.forEach(function (entry) {
      var el = entry.target, list = jobs.get(el), view;
      if (!list) return;
      if (!seen.has(el)) {
        seen.add(el);
        if (entry.isIntersecting || !motionOK() || (top !== null && (r = el.getBoundingClientRect()).bottom > top && r.top < top + innerHeight)) {
          list = list.filter(function (job) { return job.fromStart && motionOK(); });
          if (!list.length) { M.done(el); return; }
          jobs.set(el, list);
        } else { el.classList.add("is-armed"); return; }
      }
      view = entry.rootBounds ? entry.rootBounds.height : innerHeight;
      list.forEach(function (job) {
        if (!job.done && (entry.intersectionRatio >= job.ratio || (entry.isIntersecting && entry.intersectionRect.height >= job.ratio * view))) {
          job.done = true;
          ready.push([entry.boundingClientRect, el, job]);
        }
      });
      if (list.every(function (job) { return job.done; })) { observer.unobserve(el); jobs.delete(el); }
    });
    // reading order; nothing plays under the page change
    ready.sort(function (a, b) { return (Math.round(a[0].top / 8) - Math.round(b[0].top / 8)) || (a[0].left - b[0].left); })
      .forEach(function (r) { Promise.resolve(window.slSettled).then(function () { r[2].run(r[1]); }); });
  }, { threshold: [0, .05, .1, .15, .2, .25, .3, .5, .75, .9, 1] }) : null;
  var once = M.once = function (el, ratio, run, fromStart) {
    if (!observer || !el) return;
    var list = jobs.get(el);
    if (!list) { jobs.set(el, list = []); observer.observe(el); }
    list.push({ ratio: ratio, run: run, done: false, fromStart: !!fromStart });
  };

  // The one animation allowed without motion: 150ms opacity, to and from display: none.
  M.calm = function (el, dir) {
    if (!el || !el.animate) return Promise.resolve();
    var a = el.animate({ opacity: dir === "in" ? [0, 1] : [1, 0] }, { duration: 150, easing: "linear", fill: dir === "in" ? "none" : "forwards" });
    return a.finished.then(function () { return a; }, function () {});
  };

  // Settle: every moment jumps to its finished frame (Hold still, or Reduce Motion turned on).
  var settle = function (hold) {
    if (hold) root.classList.add("still");   // first: the CSS kill switch
    root.classList.remove("m");
    if (document.getAnimations) document.getAnimations().forEach(function (a) {
      var t = a.effect && a.effect.getTiming ? a.effect.getTiming() : {};
      try { if (t.iterations === Infinity) throw 0; a.finish(); } catch (e) { a.cancel(); }
    });
    document.querySelectorAll(".is-armed").forEach(M.done);
    if (M.showHeader) M.showHeader();
  };
  var isStill = function () { return root.classList.contains("still"); };
  var stillButton = document.querySelector(".still-toggle");
  var syncStill = function () {
    if (!stillButton) return;
    stillButton.setAttribute("aria-pressed", String(isStill()));
    stillButton.parentNode.hidden = reduceQuery.matches;
  };
  if (stillButton) {
    syncStill();
    stillButton.addEventListener("click", function () {
      var on = !isStill();
      try { localStorage.setItem("sl-still", on ? "1" : "0"); } catch (e) {}
      if (on) settle(true);
      else { root.classList.remove("still"); if (!reduceQuery.matches) root.classList.add("m"); }
      syncStill();
    });
  }
  reduceQuery.addEventListener("change", function () {
    if (reduceQuery.matches) settle(false);
    else if (!isStill()) root.classList.add("m");
    syncStill();
  });

  // Through the arch (M01): remember the tap or doorway (M14); hand over as the page leaves.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]"), W = innerWidth, r, d, f, b;
    if (!a || e.defaultPrevented || a.target || a.hasAttribute("download") || a.origin !== location.origin) return;
    r = { at: Date.now(), hash: !!a.hash };
    d = a.closest("[data-door]"); f = d && (d.querySelector("[data-door-frame]") || d); b = f && f.getBoundingClientRect();
    if (b && b.top >= 0 && b.bottom <= innerHeight) {
      r.x = (b.left + b.width / 2) / W * 100 + "%"; r.top = b.top + "px"; r.w = b.width + "px"; r.h = b.height + "px";
    } else r.x = (e.detail ? Math.min(80, Math.max(20, e.clientX / W * 100)) : 50) + "%";   // keyboard: centre
    try { sessionStorage.setItem("sl-vt", JSON.stringify(r)); } catch (x) {}
  });
  addEventListener("pageswap", function (e) {
    var vt = e.viewTransition, r = {}, c = root.classList, hd;
    if (!vt) return;
    if (e.activation && /traverse|reload/.test(e.activation.navigationType)) { vt.skipTransition(); return; }
    try { r = JSON.parse(sessionStorage.getItem("sl-vt") || "{}"); } catch (x) {}
    r.quiet = c.contains("menu-open") || !!r.hash;
    hd = document.querySelector(".site-header");
    r.keep = !r.quiet && !!hd && hd.getBoundingClientRect().top > -1;
    c.toggle("vt-keep", r.keep);   // toggle: a restored page must not keep it
    try { sessionStorage.setItem("sl-vt", JSON.stringify(r)); } catch (x) {}
  });
  // iOS needs a touch listener for :active
  document.addEventListener("touchstart", function () {}, { passive: true });

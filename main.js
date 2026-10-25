// Sunday Light. Built from tools/site/js/ by tools/site/build.py: edit the parts there.
// Sunday Light. The still page is the CSS default; motion starts only from html.m (motion plan §5).
(function () {
  "use strict";
  var root = document.documentElement;
  var reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var motionOK = function () { return root.classList.contains("m"); };
  var M = window.SL = { motionOK: motionOK };
  var wait = M.wait = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };

  // Queues: 2 draws, 4 prints at once, a gap apart; a slot frees when start() settles or at ms+150.
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

  // One observer plays every one-shot: in view at first sight, done; else armed until `ratio` is seen. A cold
  // load at #id jumps after the first look, which judges where it lands.
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

  // The one move without motion: 150ms opacity, to and from display: none.
  M.calm = function (el, dir) {
    if (!el || !el.animate) return Promise.resolve();
    var a = el.animate({ opacity: dir === "in" ? [0, 1] : [1, 0] }, { duration: 150, easing: "linear", fill: dir === "in" ? "none" : "forwards" });
    return a.finished.then(function () { return a; }, function () {});
  };

  // Settle: every moment jumps to its end (Hold still, or Reduce Motion on).
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

  // Through the arch (M01): note the tap or doorway (M14); hand over as the page leaves.
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
    c.toggle("vt-keep", r.keep);   // a restored page must not keep it
    try { sessionStorage.setItem("sl-vt", JSON.stringify(r)); } catch (x) {}
  });
  // In-page jumps glide only after load, so a cold load at #id lands at once, its first view finished (rule 3).
  var glide = function () { requestAnimationFrame(function () { root.classList.add("glide"); }); };
  if (document.readyState === "complete") glide(); else addEventListener("load", glide);
  // iOS needs a touch listener for :active
  document.addEventListener("touchstart", function () {}, { passive: true });

  // Moments (CSS: 97-motion.css).
  var drawn = function (el) { el.classList.add("is-drawn"); };
  // Ruled in (M12) at 25%.
  document.querySelectorAll("[data-rules]").forEach(function (el) { once(el, .25, drawn); });
  // Windows (M02): the arcade draws at 90%, cells 120ms apart.
  document.querySelectorAll(".window-arches").forEach(function (el) {
    var ms = 780 + 120 * el.children.length;
    once(el, .9, function () { M.queue("draw", function () { drawn(el); return wait(ms); }, ms); });
  });
  // Sundown (M03): the line; .is-dusk sets the sun without scroll timelines.
  var scene = document.querySelector(".sundown-scene");
  once(scene, .9, function () { M.queue("draw", function () { drawn(scene); return wait(3000); }, 3000); });
  once(scene, .5, function () { scene.classList.add("is-dusk"); });
  // 404 (D12): the mark starts in CSS at first paint, then goes to dusk once.
  once(document.getElementById("nf-mark"), .9, function (el) { el.classList.add("is-dusk"); }, true);

  // Phone menu (M07): below 861px the shut sheet is inert; open, the page behind is.
  var toggle = document.querySelector(".nav-toggle"), nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var behind = document.querySelectorAll("main, .site-footer, .skip");
    var label = toggle.querySelector(".nav-toggle-label");
    var phone = matchMedia("(max-width: 860px)");
    var isOpen = function () { return nav.classList.contains("is-open"); };
    var setMenu = function (open) {
      nav.inert = !open && phone.matches;
      if (open === isOpen()) return;
      if (open && M.showHeader) M.showHeader(true);   // never in a moving header
      toggle.setAttribute("aria-expanded", String(open));
      if (label) label.textContent = open ? "Close" : "Menu";
      nav.classList.toggle("is-open", open);
      root.classList.toggle("menu-open", open);
      behind.forEach(function (el) { el.inert = open; });
      if (open) { var first = nav.querySelector("a[href]"); if (first) first.focus({ preventScroll: true }); }
    };
    toggle.addEventListener("click", function () { setMenu(!isOpen()); });
    // same-page links close it (the page change reads .menu-open)
    nav.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a[href]");
      if (a && a.getAttribute("href").charAt(0) === "#") setMenu(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) { setMenu(false); toggle.focus(); }
    });
    var onWidth = function () { setMenu(isOpen() && phone.matches); };
    phone.addEventListener("change", onWidth);
    onWidth();
  }

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

  // Photos: WebP, then JPEG, then .is-missing.
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
  // Tray prints (M10) develop at 20% once decoded; undecoded in 2.5s, missing or done: the veil goes.
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

  // Index spy (§4.10): the top target in the band is current; none above the first or past the last.
  {
    const bar = document.querySelector(".index-bar"), ix = bar && bar.querySelector(".index"), owner = new Map(), band = new Set();
    let current = null;
    const show = (a) => {   // never scrollIntoView
      let left = 0;
      if (a) {
        const r = a.getBoundingClientRect(), s = ix.getBoundingClientRect();
        if (r.left >= s.left + 8 && r.right <= s.right - 40) return;
        left = ix.scrollLeft + r.left - s.left - (s.width - r.width) / 2;
      }
      ix.scrollTo({ left, behavior: motionOK() ? "smooth" : "auto" });
    };
    const mark = (a, past) => {
      if (a && a === current) return;
      if (current) current.removeAttribute("aria-current");
      if ((current = a)) a.setAttribute("aria-current", "true");
      if (!past) show(a);
    };
    if (ix) {
      ix.querySelectorAll("a[data-spy]").forEach((a) => a.dataset.spy.split(" ").forEach((id) => {
        const t = document.getElementById(id);
        if (t) owner.set(t, a);
      }));
      const targets = [...owner.keys()].sort((a, b) => a.compareDocumentPosition(b) & 2 ? 1 : -1);
      const edge = 8 + Math.max(document.querySelector(".site-header").offsetHeight + bar.offsetHeight,
        parseFloat(getComputedStyle(root).scrollPaddingTop) || 0);   // 8px below landing
      const spy = new IntersectionObserver((entries) => {
        entries.forEach((e) => band[e.isIntersecting && e.intersectionRatio > 0 ? "add" : "delete"](e.target));
        const top = targets.find((t) => band.has(t));
        if (top) mark(owner.get(top));
        else if (targets[0]?.getBoundingClientRect().top >= bar.getBoundingClientRect().bottom - 1) mark(null);
        else if (targets.at(-1)?.getBoundingClientRect().bottom <= edge + 1) mark(null, 1);
      }, { rootMargin: `-${edge}px 0px -55% 0px`, threshold: [0, .001] });
      [bar.previousElementSibling, ...targets].forEach((t) => t && spy.observe(t));   // the head: a jump up
      ix.addEventListener("focusin", (e) => show(e.target));
    }
  }

  // The arch opens (M05): the ring draws once the whole frame is seen; without scroll timelines the arch opens at 25%.
  {
    const frame = document.querySelector(".statement .frame");
    if (frame) {
      once(frame, .9, function () { M.queue("draw", function () { frame.classList.add("is-drawn"); return wait(900); }, 900); });
      if (!(window.CSS && CSS.supports("animation-timeline: view()"))) once(frame, .25, function () { frame.classList.add("is-open"); });
    }
  }
  // Hours of light (M08, D11): the tiers light once 90% is on screen, one draw job; every sun lands at 1200ms.
  {
    const tiers = document.querySelector(".tiers");
    if (tiers) once(tiers, .9, () => M.queue("draw", () => { tiers.classList.add("is-lit"); return wait(1200); }, 1200));
  }
  // Contact: ?session=Wedding arrives with that chip chosen (§4.18).
  for (const r of document.querySelectorAll('[name="session"]')) if (r.value == new URLSearchParams(location.search).get("session")) r.checked = true;
  // Viewer (§4.12; M06, M11); fades are CSS; the close event cleans up
  viewer: {
  const dlg = document.querySelector(".viewer"), links = [...document.querySelectorAll("[data-viewer]")];
  if (!links[0] || !dlg?.showModal) break viewer;
  const $ = s => dlg.querySelector(s), dark = $(".viewer-dark"), stage = $(".viewer-stage"), full = new Map(),
    [front, back] = dlg.querySelectorAll(".viewer-img"), EL = "cubic-bezier(.2,.65,.25,1)", ES = "cubic-bezier(.65,0,.35,1)",
    ARCH = "50% 50% 0 0/33.3% 33.3% 0 0", ph = a => a.querySelector(".ph"), img = a => a.querySelector("img"),
    two = n => ("0" + n).slice(-2), cover = a => a.matches(".chapter-cover"),
    fx = (el, k, duration, easing, delay, fill) => el.animate(k, { duration, easing, delay, fill }),
    stop = (el, keep) => el.getAnimations().forEach(x => (keep && x.commitStyles(), x.cancel()));
  let list, cur, pos, shut, gen = 0, hid, sx, sy, dy, drag, t0;

  // the full file, decoded off the page: WebP srcset, else JPEG
  const load = (a, s = a.querySelector("source"), get = ss => {
    const i = new Image();
    if (ss) i.sizes = dlg.dataset.sizes, i.srcset = ss; else i.src = a.href;
    return i.decode().then(() => i.currentSrc);
  }) => full.get(a) || full.set(a, get(s && s.srcset).catch(() => get()).catch(() => "")).get(a);
  const place = a => {   // arithmetic, never the big image
    const i = img(a), b = stage.getBoundingClientRect(), r = i.getAttribute("height") / i.getAttribute("width"),
      w = Math.min(b.width, b.height / r), h = w * r;
    front.style.width = w + "px"; front.style.height = h + "px";
    pos = { x: b.left + (b.width - w) / 2, y: b.top + (b.height - h) / 2, w, h };
  };
  const at = r => `translate(${r.left - pos.x}px,${r.top - pos.y}px) scale(${r.width / pos.w})`;
  const info = (a, step, g = gen) => {
    const n = cur + 1, N = list.length;
    front.src = img(a).currentSrc;   // the decoded thumbnail ("": hidden)
    $(".viewer-caption").textContent = a.dataset.chapter;
    $(".viewer-total").textContent = two(N);
    dlg.style.setProperty("--p", n / N);
    $(".viewer-live").textContent = `Photo ${n} of ${N}: ${front.alt = img(a).alt}`;
    dlg.querySelectorAll(".wheel span").forEach((c, i) => {
      const o = c.textContent.slice(-1), d = two(n)[i];
      stop(c); c.textContent = d;
      if (o == d || !step || !motionOK()) return;
      c.innerHTML = o + "<br>" + d;
      fx(c, { transform: ["none", "translateY(-50%)"] }, 280, ES, 40 - 40 * i, "both").onfinish = () => { c.textContent = d; stop(c); };
    });
    M.done(ph(a));   // M10
    dlg.classList.add("is-loading");
    load(a).then(u => {
      if (g != gen) return;
      if (u) front.src = u;
      dlg.classList.remove("is-loading");
      load(list[(cur + 1) % N]); load(list[(cur + N - 1) % N]);
    });
  };
  const open = a => {
    list = links.filter(l => !ph(l).matches(".is-missing"));
    cur = list.indexOf(a);
    if (cur < 0) return;
    const r = ph(a).getBoundingClientRect();
    gen++; shut = 0; hid = img(a);
    dlg.showModal(); root.classList.add("viewer-open"); place(a);
    hid.style.visibility = "hidden"; info(a);
    if (!motionOK()) return M.calm(dlg, "in");
    fx(front, { transform: [at(r), "none"] }, 480, EL);
    if (cover(a)) fx(front, { borderRadius: [ARCH, "0"] }, 240, EL);
  };
  const go = step => {
    if (shut || !list[1]) return;
    const a = list[cur = (cur + step + list.length) % list.length], i = img(a), m = motionOK(), g = ++gen;
    stop(front, 1); stop(back);
    hid.style.visibility = ""; (hid = i).style.visibility = "hidden";
    back.style.cssText = front.style.cssText + ";opacity:0";
    if (m) back.src = front.currentSrc, fx(back, [{ opacity: 1 }, { opacity: 0, transform: `translateX(${-step * pos.w / 25}px)` }], 160,
      "cubic-bezier(.4,0,1,1)");
    front.style.cssText = "opacity:0"; place(a);
    info(a, step);
    Promise.resolve(i.currentSrc || load(a)).then(() => front.decode()).catch(() => {}).then(() => {
      if (g != gen) return;
      front.style.opacity = "";
      if (m) fx(front, { opacity: [0, 1], transform: [`translateX(${step * 4}%)`, "none"] }, 300, EL, 160, "backwards");
      else M.calm(front, "in");
    });
  };
  const close = () => {
    if (shut || !dlg.open) return;
    shut = 1; gen++;
    const a = list[cur], f = ph(a), o = f.getBoundingClientRect();
    if (o.bottom < 0 || o.top > innerHeight)
      root.style.scrollBehavior = "auto", f.scrollIntoView({ block: "center" }), root.style.scrollBehavior = "";
    if (!motionOK()) return M.calm(dlg, "out").then(() => dlg.close());
    stop(front, 1); front.style.opacity = ""; dlg.classList.add("is-closing");
    if (cover(a)) fx(front, [{ borderRadius: ARCH }], 240, EL, 160, "forwards");
    fx(front, [{ transform: at(f.getBoundingClientRect()) }], 400, ES, 0, "forwards").onfinish = () => {
      hid.style.visibility = ""; dlg.close();
    };
  };
  dlg.onclose = () => {
    dlg.classList.remove("is-loading", "is-closing"); root.classList.remove("viewer-open");
    dlg.getAnimations({ subtree: true }).forEach(x => x.cancel());
    [front, back, dark].forEach(el => el.removeAttribute("style"));
    hid.style.visibility = "";
    list[cur].focus({ preventScroll: true });
  };
  dlg.oncancel = e => { e.preventDefault(); close(); };
  for (const a of links) a.onclick = e => { if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return; e.preventDefault(); open(a); };   // a modified or middle click: the browser opens the JPEG
  $(".viewer-prev").onclick = () => go(-1);
  $(".viewer-next").onclick = () => go(1);
  $(".viewer-close").onclick = close;
  dlg.onclick = e => { if ([dlg, stage, dark].includes(e.target)) close(); };
  dlg.onkeydown = e => {
    const d = { ArrowLeft: -1, ArrowRight: 1 }[e.key];
    if (d) go(d);
  };
  addEventListener("resize", () => { if (dlg.open && !shut) place(list[cur]); });

  // swipe: 45px pages; down follows, closes past 90px or .5px/ms
  dlg.ontouchstart = e => {
    const f = e.touches[0];
    sx = !e.touches[1] && !shut && visualViewport.scale < 1.01 ? f.clientX : null;
    sy = f.clientY; drag = ""; t0 = e.timeStamp;
  };
  dlg.ontouchmove = e => {
    if (sx === null || drag == "x") return;
    const f = e.touches[0], dx = f.clientX - sx, p = Math.min(Math.max(dy = f.clientY - sy, 0) / 300, 1), s = 1 - p / 10;
    if (!drag) {
      if (Math.hypot(dx, dy) < 8 || (drag = dy > Math.abs(dx) ? "y" : "x") == "x") return;
      if (motionOK()) stop(front, 1);
    }
    e.preventDefault();
    if (!motionOK()) return;
    front.style.transform = `translate(${(1 - s) * pos.w / 2}px,${dy + (1 - s) * pos.h / 2}px) scale(${s})`;
    dark.style.opacity = 1 - p / 2;
  };
  dlg.ontouchend = dlg.ontouchcancel = e => {
    const d = drag, ok = e.type == "touchend", dx = e.changedTouches[0].clientX - sx,
      t = front.style.transform, o = dark.style.opacity;
    sx = null; drag = "";
    if (d == "x" && ok && Math.abs(dx) > 45) go(dx < 0 ? 1 : -1);
    if (d != "y") return;
    if (ok && (dy > 90 || (dy > 24 && dy / (e.timeStamp - t0) > .5))) return close();
    front.style.transform = dark.style.opacity = "";
    if (t) fx(front, { transform: [t, "none"] }, 240, EL);
    if (o) fx(dark, { opacity: [o, 1] }, 240, EL);
  };
  }
  // Enquiry (§4.18, M09, D15): a field checks on blur once typed in, and on send. #form-live sits outside the form.
  enquiry: {
    const form = document.getElementById("enquiry-form");
    if (!form) break enquiry;
    const $ = id => document.getElementById(id), err = n => $("err-" + n);
    const live = $("form-live"), card = $("form-success"), title = $("success-title"), sum = $("form-summary"),
      failure = $("form-error"), radios = [...form.elements.session], NAMES = ["name", "email", "session", "message"], typed = {};
    const attr = (el, a, on) => on ? el.setAttribute(a, "true") : el.removeAttribute(a);
    form.noValidate = true;   // without JS the browser checks

    const problem = n => {
      const d = err(n).dataset, v = n == "session" ? radios.some(r => r.checked) : form.elements[n].value.trim();
      return !v ? d.m : n == "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? d.bad : "";
    };
    const show = (n, m, s = err(n)) => {
      (n == "session" ? radios : [form.elements[n]]).forEach(el => attr(el, "aria-invalid", m));
      s.lastChild.textContent = m;
      s.classList.toggle("is-on", !!m);
    };
    form.addEventListener("input", e => {
      const n = e.target.name;
      if (NAMES.includes(n) && (typed[n] = 1) && err(n).classList.contains("is-on") && !problem(n)) show(n, "");
    });
    form.addEventListener("focusout", e => {
      const n = e.target.name;
      if (n == "session" ? !e.target.closest("fieldset").contains(e.relatedTarget) : typed[n]) show(n, problem(n));
    });
    sum.addEventListener("click", e => {
      const a = e.target.closest("a");
      if (a) { e.preventDefault(); $(a.hash.slice(1)).focus(); }
    });

    // M09: a couple whole (≤ 24 characters) or a clear first name; no titles, no surnames.
    const firstName = v => {
      v = v.trim().replace(/\s+/g, " ").replace(/[\s.,;:!?]+$/, "");
      if (/^((mr|mrs|ms|miss|mx|dr)\b|the )/i.test(v)) return "";
      if (/ (&|\+|and) /i.test(v)) return v.length > 24 ? "" : v;
      v = v.split(" ")[0];
      return !/^\p{L}[\p{L}'’-]{0,22}\p{L}$/u.test(v) ? "" : v == v.toLowerCase() || v == v.toUpperCase() ? v[0].toUpperCase() + v.slice(1).toLowerCase() : v;
    };
    const sending = on => { form.classList.toggle("is-sending", on); attr(form, "aria-busy", on); attr(form.querySelector("button"), "aria-disabled", on); };
    const sent = play => {   // motion: fields fade, the card rises through its arch (CSS)
      const n = firstName(form.elements.name.value), em = document.createElement("em"), hide = () => form.classList.add("is-sent");
      const focus = () => title.focus();
      em.textContent = n;
      title.textContent = n ? "Thank you, " : "Thank you.";
      if (n) title.append(em, ".");
      live.textContent = "Enquiry sent. " + title.textContent;
      card.hidden = false;
      form.inert = true;
      const top = card.getBoundingClientRect().top;
      if (top < 0) scrollBy(0, top - 16);   // short phones
      if (play && !motionOK()) return M.calm(form, "out").then(a => { hide(); a && a.cancel(); }), M.calm(card, "in").then(focus);
      hide();
      if (!play) return focus();
      form.parentNode.classList.add("is-sent");
      setTimeout(focus, 720);
    };

    form.addEventListener("submit", e => {
      e.preventDefault();
      if (form.classList.contains("is-sending")) return;
      failure.hidden = true;
      const bad = NAMES.filter(n => { const m = problem(n); show(n, m); return m; });
      sum.querySelectorAll("li").forEach(li => {
        li.hidden = !bad.includes(li.dataset.n);
        li.firstChild.textContent = err(li.dataset.n).lastChild.textContent;
      });
      if ((sum.hidden = !bad.length)) {
        if (form.elements._honey.value) return sent();   // honeypot: the card, nothing sent
        // FormSubmit emails it as a labelled table; Reply goes to the sender
        const v = n => form.elements[n].value.trim(), data = { _subject: `New enquiry: ${v("session")} from ${v("name")}`, _template: "table", _replyto: v("email") };
        for (const [k, n] of [["Name", "name"], ["Email", "email"], ["Phone", "phone"], ["Session", "session"], ["Date or season", "date"], ["Where", "location"], ["Message", "message"], ["How they found me", "heard"]]) if (v(n)) data[k] = v(n);
        sending(true);
        live.textContent = "Sending…";
        return fetch(form.dataset.endpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data), signal: AbortSignal.timeout(20000) })
          .then(r => r.ok ? r.json() : Promise.reject(r))
          .then(j => { if (j.success + "" != "true") throw j; sending(false); sent(1); })   // "false" until activated
          .catch(() => {   // in its kept space; values stay
            sending(false);
            failure.hidden = false;
            if (!motionOK()) M.calm(failure, "in");
            failure.focus();
            live.textContent = "Your enquiry didn’t send.";
          });
      }
      live.textContent = sum.firstChild.textContent = sum.dataset.n.split(",")[bad.length - 1] + " to check";
      sum.scrollIntoView({ block: "start" });
      sum.focus({ preventScroll: true });
    });
  }

  document.querySelectorAll("[data-year]").forEach(function (node) {
    node.textContent = String(new Date().getFullYear());
  });
  // Back to top: smooth only with motion, then focus the header. Without JS, #top is the page top.
  document.querySelectorAll(".to-top").forEach(function (a) {
    a.addEventListener("click", function (e) {
      var top = document.querySelector("#top, .site-header");
      if (!top) return;
      e.preventDefault();
      scrollTo({ top: 0, behavior: motionOK() ? "smooth" : "auto" });
      top.focus({ preventScroll: true });
    });
  });

  // Golden hour (M03): the hour before NOAA sunset in Adelaide.
  var golden = document.querySelector("[data-golden]");
  var sunsetMinutesUTC = window.slSunset = function (y, m, d) {
    var r = Math.PI / 180, sin = Math.sin, cos = Math.cos, tan = Math.tan, lat = -34.9285 * r;
    var t = (Date.UTC(y, m - 1, d) / 864e5 + 2440587.5 - 2451545) / 36525;
    var L = (280.46646 + t * (36000.76983 + t * .0003032)) % 360 * r;
    var A = (357.52911 + t * (35999.05029 - .0001537 * t)) * r;
    var e = .016708634 - t * (.000042037 + .0000001267 * t);
    var C = sin(A) * (1.914602 - t * (.004817 + .000014 * t)) + sin(2 * A) * (.019993 - .000101 * t) + sin(3 * A) * .000289;
    var o = (125.04 - 1934.136 * t) * r;
    var eps = (23 + (26 + (21.448 - t * (46.815 + t * (.00059 - t * .001813))) / 60) / 60 + .00256 * cos(o)) * r;
    var decl = Math.asin(sin(eps) * sin((L / r + C - .00569 - .00478 * sin(o)) * r));
    var yy = Math.pow(tan(eps / 2), 2);
    var eq = 4 / r * (yy * sin(2 * L) - 2 * e * sin(A) + 4 * e * yy * sin(A) * cos(2 * L) - .5 * yy * yy * sin(4 * L) - 1.25 * e * e * sin(2 * A));
    return 720 - 4 * 138.6007 - eq + 4 * Math.acos(cos(90.833 * r) / (cos(lat) * cos(decl)) - tan(lat) * tan(decl)) / r;
  };
  var showGoldenHour = function () {
    try {   // no Intl zones: the static text stays
      var zone = "Australia/Adelaide", day = new Intl.DateTimeFormat("en-AU", { timeZone: zone, year: "numeric", month: "numeric", day: "numeric" });
      var time = new Intl.DateTimeFormat("en-AU", { timeZone: zone, hour: "numeric", minute: "2-digit" });
      var sunsetOn = function (when) {
        var p = {};
        day.formatToParts(when).forEach(function (x) { p[x.type] = Number(x.value); });
        return Date.UTC(p.year, p.month - 1, p.day) + sunsetMinutesUTC(p.year, p.month, p.day) * 6e4;
      };
      var now = Date.now(), sunset = sunsetOn(new Date(now)), start = sunset - 36e5, text;
      if (!isFinite(sunset)) return;
      text = now < start ? "Golden hour in Adelaide tonight \u00b7 from " + time.format(start)
        : now < sunset ? "Golden hour in Adelaide now \u00b7 until " + time.format(sunset)
        : "Golden hour tomorrow \u00b7 from " + time.format(sunsetOn(new Date(now + 864e5)) - 36e5);
      golden.classList.add("is-swapping");
      setTimeout(function () { golden.textContent = text; golden.classList.remove("is-swapping"); }, motionOK() ? 300 : 0);
    } catch (e) {}
  };
  if (golden) {   // only near the footer: formatters are costly
    var near = new IntersectionObserver(function (entries) {
      if (!entries.some(function (x) { return x.isIntersecting; })) return;
      near.disconnect();
      if (window.requestIdleCallback) requestIdleCallback(showGoldenHour, { timeout: 1500 });
      else setTimeout(showGoldenHour, 200);
    }, { rootMargin: "0px 0px 900px 0px" });
    near.observe(golden);
  }
})();

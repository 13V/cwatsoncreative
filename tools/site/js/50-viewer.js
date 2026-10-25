  // Viewer (§4.12; M06, M11); fades in CSS; the close event cleans up; no showModal: plain links
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
  const close = () => {   // an off-screen slot is centred first
    if (shut || !dlg.open) return;
    shut = 1; gen++;
    const a = list[cur], f = ph(a), o = f.getBoundingClientRect();
    if (!motionOK()) return M.calm(dlg, "out").then(() => dlg.close());
    if (o.bottom < 0 || o.top > innerHeight)
      root.style.scrollBehavior = "auto", f.scrollIntoView({ block: "center" }), root.style.scrollBehavior = "";
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
  for (const a of links) a.onclick = e => { e.preventDefault(); open(a); };
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

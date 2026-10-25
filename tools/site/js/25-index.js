
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

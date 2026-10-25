
  // Index spy (spec §4.10): the topmost section in the band under the bars (to 45%) marks its data-spy link.
  {
    const bar = document.querySelector(".index-bar"), ix = bar && bar.querySelector(".index"), owner = new Map(), band = new Set();
    let current = null;
    const mark = (a) => {
      if (a === current) return;
      if (current) current.removeAttribute("aria-current");
      if ((current = a)) {
        a.setAttribute("aria-current", "true");
        const r = a.getBoundingClientRect(), s = ix.getBoundingClientRect();
        if (r.left < s.left || r.right > s.right - 32)   // never scrollIntoView
          ix.scrollTo({ left: ix.scrollLeft + r.left - s.left - (s.width - r.width) / 2, behavior: motionOK() ? "smooth" : "auto" });
      }
    };
    if (ix) {
      ix.querySelectorAll("a[data-spy]").forEach((a) => a.dataset.spy.split(" ").forEach((id) => {
        const t = document.getElementById(id);
        if (t) owner.set(t, a);
      }));
      const targets = [...owner.keys()].sort((a, b) => (a.compareDocumentPosition(b) & 2 ? 1 : -1));
      const spy = new IntersectionObserver((entries) => {
        entries.forEach((e) => band[e.isIntersecting && e.intersectionRatio > 0 ? "add" : "delete"](e.target));
        const top = targets.find((t) => band.has(t));
        if (top) mark(owner.get(top));
        else if (targets[0].getBoundingClientRect().top > bar.getBoundingClientRect().bottom) mark(null);
      }, { rootMargin: `-${8 + Math.max(document.querySelector(".site-header").offsetHeight + bar.offsetHeight,
        parseFloat(getComputedStyle(root).scrollPaddingTop) || 0)}px 0px -55% 0px`, threshold: [0, .001] });   // 8px under a jump's landing line
      targets.forEach((t) => spy.observe(t));
    }
  }

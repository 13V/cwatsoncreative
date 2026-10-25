
  // Index spy (§4.10): the top target in the band under the bars marks its link; none above the first.
  {
    const bar = document.querySelector(".index-bar"), ix = bar && bar.querySelector(".index"), owner = new Map(), band = new Set();
    let current = null;
    const mark = (a) => {
      if (a === current) return;
      if (current) current.removeAttribute("aria-current");
      let left = 0;
      if ((current = a)) {
        a.setAttribute("aria-current", "true");
        const r = a.getBoundingClientRect(), s = ix.getBoundingClientRect();
        if (r.left >= s.left && r.right <= s.right - 32) return;   // never scrollIntoView
        left = ix.scrollLeft + r.left - s.left - (s.width - r.width) / 2;
      }
      ix.scrollTo({ left, behavior: motionOK() ? "smooth" : "auto" });
    };
    if (ix) {
      ix.querySelectorAll("a[data-spy]").forEach((a) => a.dataset.spy.split(" ").forEach((id) => {
        const t = document.getElementById(id);
        if (t) owner.set(t, a);
      }));
      const targets = [...owner.keys()].sort((a, b) => a.compareDocumentPosition(b) & 2 ? 1 : -1);
      const spy = new IntersectionObserver((entries) => {
        entries.forEach((e) => band[e.isIntersecting && e.intersectionRatio > 0 ? "add" : "delete"](e.target));
        const top = targets.find((t) => band.has(t));
        if (top) mark(owner.get(top));
        else if (targets[0]?.getBoundingClientRect().top >= bar.getBoundingClientRect().bottom - 1) mark(null);
      }, { rootMargin: `-${8 + Math.max(document.querySelector(".site-header").offsetHeight + bar.offsetHeight,
        parseFloat(getComputedStyle(root).scrollPaddingTop) || 0)}px 0px -55% 0px`, threshold: [0, .001] });   // 8px below landing
      [bar.previousElementSibling, ...targets].forEach((t) => t && spy.observe(t));   // the head: a jump up
    }
  }


  // Hours of light (M08, D11): the tiers light once 90% is on screen, one draw job; every sun lands at 1200ms.
  // A cold load at a fragment (investment.html#family): where the jump lands is the first view, so it is finished
  // (the observer's first look comes before the browser's fragment scroll). Kernel candidate, see notes for merge.
  {
    const tiers = document.querySelector(".tiers"), id = location.hash.slice(1);
    if (tiers) once(tiers, .9, () => M.queue("draw", () => { tiers.classList.add("is-lit"); return wait(1200); }, 1200));
    const to = root.dataset.page === "investment" && id && document.getElementById(id);
    if (to) {
      const top = to.getBoundingClientRect().top - (parseFloat(getComputedStyle(root).scrollPaddingTop) || 0);
      document.querySelectorAll("[data-rules]").forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.bottom > top && r.top < top + innerHeight) M.done(el);
      });
    }
  }

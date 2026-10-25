  // Hours of light (M08, D11): the tiers light once 90% is on screen, one draw job; every sun lands at 1200ms.
  {
    const tiers = document.querySelector(".tiers");
    if (tiers) once(tiers, .9, () => M.queue("draw", () => { tiers.classList.add("is-lit"); return wait(1200); }, 1200));
  }

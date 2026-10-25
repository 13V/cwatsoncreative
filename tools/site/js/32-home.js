
  // The arch opens (M05): the ring draws once the whole frame is seen; without scroll timelines the arch opens at 25%.
  {
    const frame = document.querySelector(".statement .frame");
    if (frame) {
      once(frame, .9, function () { M.queue("draw", function () { frame.classList.add("is-drawn"); return wait(900); }, 900); });
      if (!(window.CSS && CSS.supports("animation-timeline: view()"))) once(frame, .25, function () { frame.classList.add("is-open"); });
    }
  }

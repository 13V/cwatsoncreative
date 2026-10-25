  // Ruled in: eyebrow dashes and the rules of steps, questions, the contact column and the wedding tiers.
  var draw = function (el) { el.classList.add("is-drawn"); };
  document.querySelectorAll(".eyebrow, [data-rules]").forEach(function (el) { once(el, .25, draw); });
  // Sundown: the footer's gold line draws once when the scene is in view; where scroll timelines are missing, the
  // sunset also plays once.
  var sundown = document.querySelector(".sundown");
  once(sundown, .9, function (el) {
    M.queue("draw", function () { el.classList.add("is-drawn"); return wait(2300); }, 2300);
  });
  once(sundown, .5, function (el) { el.classList.add("is-dusk"); });

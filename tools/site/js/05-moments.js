  // Ruled in: eyebrow dashes and the rules of steps, questions, the contact column and the wedding tiers.
  document.querySelectorAll(".eyebrow, [data-rules]").forEach(function (el) { once(el, .25, draw); });
  // Sundown: the footer line draws once; where scroll timelines are missing, the sunset also plays once.
  var footerEl = document.querySelector(".site-footer");
  once(footerEl, .1, draw);
  once(footerEl, .25, function (el) { el.classList.add("is-dusk"); });


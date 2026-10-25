
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

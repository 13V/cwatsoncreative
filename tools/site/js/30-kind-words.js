  // Kind words: one review at a time, with arrows and swipes.
  document.querySelectorAll(".words").forEach(function (box) {
    var items = box.querySelectorAll(".words-item");
    var photos = box.querySelectorAll(".words-photo");
    var count = box.querySelector(".words-count");
    if (items.length < 2 || !count) return;
    var current = 0;
    var go = function (index) {
      current = (index + items.length) % items.length;
      items.forEach(function (item, i) { item.classList.toggle("is-current", i === current); });
      photos.forEach(function (photo, i) { photo.classList.toggle("is-current", i === current); });
      count.textContent = (current + 1) + " / " + items.length;
    };
    box.querySelector(".words-prev").addEventListener("click", function () { go(current - 1); });
    box.querySelector(".words-next").addEventListener("click", function () { go(current + 1); });
    var startX = null;
    var startY = 0;
    box.addEventListener("touchstart", function (event) {
      if (event.touches.length !== 1) { startX = null; return; }
      startX = event.touches[0].clientX;
      startY = event.touches[0].clientY;
    }, { passive: true });
    box.addEventListener("touchend", function (event) {
      if (startX === null) return;
      var dx = event.changedTouches[0].clientX - startX;
      var dy = event.changedTouches[0].clientY - startY;
      startX = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.3) go(current + (dx < 0 ? 1 : -1));
    }, { passive: true });
  });


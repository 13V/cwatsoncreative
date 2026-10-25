  // Photos: the WebP copies first, then the JPEG, then the landscape art if the file has gone.
  var photoFailed = function (image) {
    var picture = image.parentNode;
    var sources = picture && picture.nodeName === "PICTURE" ? picture.querySelectorAll("source") : [];
    if (sources.length) {
      sources.forEach(function (source) { picture.removeChild(source); }); // the browser retries with the JPEG
      return;
    }
    var figure = image.closest(".ph");
    if (figure) figure.classList.add("is-missing");
  };
  document.querySelectorAll(".ph img").forEach(function (image) {
    image.addEventListener("load", function () { image.classList.add("is-loaded"); });
    image.addEventListener("error", function () { photoFailed(image); });
    if (image.complete) {
      if (image.naturalWidth) image.classList.add("is-loaded");
      else photoFailed(image);
    }
  });


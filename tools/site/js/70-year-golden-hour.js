
  document.querySelectorAll("[data-year]").forEach(function (node) {
    node.textContent = String(new Date().getFullYear());
  });

  // ---------------------------------------------------------------- golden hour in Adelaide
  // NOAA sunset equation for Adelaide; golden hour is taken as the hour before sunset. Shown in Adelaide time.
  var golden = document.querySelector("[data-golden]");
  var sunsetMinutesUTC = function (y, m, d) {
    var rad = Math.PI / 180, lat = -34.9285, lng = 138.6007;
    var t = (Date.UTC(y, m - 1, d) / 86400000 + 2440587.5 - 2451545) / 36525;
    var L0 = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360;
    var M = 357.52911 + t * (35999.05029 - 0.0001537 * t);
    var ecc = 0.016708634 - t * (0.000042037 + 0.0000001267 * t);
    var C = Math.sin(M * rad) * (1.914602 - t * (0.004817 + 0.000014 * t)) + Math.sin(2 * M * rad) * (0.019993 - 0.000101 * t) +
      Math.sin(3 * M * rad) * 0.000289;
    var omega = 125.04 - 1934.136 * t;
    var lambda = L0 + C - 0.00569 - 0.00478 * Math.sin(omega * rad);
    var eps = 23 + (26 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60) / 60 + 0.00256 * Math.cos(omega * rad);
    var decl = Math.asin(Math.sin(eps * rad) * Math.sin(lambda * rad));
    var yy = Math.pow(Math.tan(eps / 2 * rad), 2);
    var eqTime = 4 / rad * (yy * Math.sin(2 * L0 * rad) - 2 * ecc * Math.sin(M * rad) + 4 * ecc * yy * Math.sin(M * rad) * Math.cos(2 * L0 * rad) -
      0.5 * yy * yy * Math.sin(4 * L0 * rad) - 1.25 * ecc * ecc * Math.sin(2 * M * rad));
    var ha = Math.acos(Math.cos(90.833 * rad) / (Math.cos(lat * rad) * Math.cos(decl)) - Math.tan(lat * rad) * Math.tan(decl)) / rad;
    return 720 - 4 * lng - eqTime + 4 * ha;
  };
  window.slSunset = sunsetMinutesUTC; // for checking against published tables
  var showGoldenHour = function () {
    if (!golden || !window.Intl || !Intl.DateTimeFormat) return;
    try {
      var zone = "Australia/Adelaide";
      var dateParts = function (when) {
        var parts = {};
        new Intl.DateTimeFormat("en-AU", { timeZone: zone, year: "numeric", month: "numeric", day: "numeric" })
          .formatToParts(when).forEach(function (p) { parts[p.type] = Number(p.value); });
        return parts;
      };
      var sunsetOn = function (when) {
        var p = dateParts(when);
        return Date.UTC(p.year, p.month - 1, p.day) + sunsetMinutesUTC(p.year, p.month, p.day) * 60000;
      };
      var time = new Intl.DateTimeFormat("en-AU", { timeZone: zone, hour: "numeric", minute: "2-digit" });
      var now = Date.now(), sunset = sunsetOn(new Date(now)), start = sunset - 3600000, text;
      if (!isFinite(sunset)) return;
      if (now < start) text = "Golden hour in Adelaide tonight \u00b7 from " + time.format(start);
      else if (now < sunset) text = "Golden hour in Adelaide now \u00b7 until " + time.format(sunset);
      else text = "Golden hour tomorrow \u00b7 from " + time.format(sunsetOn(new Date(now + 86400000)) - 3600000);
      golden.classList.add("is-swapping");
      setTimeout(function () { golden.textContent = text; golden.classList.remove("is-swapping"); }, motionOK() ? 300 : 0);
    } catch (e) {}
  };
  // Only worked out as the footer comes near: the time-zone formatter is costly to create on a slow phone.
  if (golden) {
    var later = function () {
      if ("requestIdleCallback" in window) requestIdleCallback(showGoldenHour, { timeout: 1500 });
      else setTimeout(showGoldenHour, 200);
    };
    if ("IntersectionObserver" in window) {
      var near = new IntersectionObserver(function (entries) {
        if (!entries.some(function (entry) { return entry.isIntersecting; })) return;
        near.disconnect();
        later();
      }, { rootMargin: "0px 0px 900px 0px" });
      near.observe(golden);
    } else later();
  }

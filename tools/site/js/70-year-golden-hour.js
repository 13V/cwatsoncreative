
  document.querySelectorAll("[data-year]").forEach(function (node) {
    node.textContent = String(new Date().getFullYear());
  });
  // Back to top: smooth only with motion, then focus the header (tabindex=-1). Without JS, #top is the page top.
  document.querySelectorAll(".to-top").forEach(function (a) {
    a.addEventListener("click", function (e) {
      var top = document.querySelector("#top, .site-header");
      if (!top) return;
      e.preventDefault();
      scrollTo({ top: 0, behavior: motionOK() ? "smooth" : "auto" });
      top.focus({ preventScroll: true });
    });
  });

  // Golden hour (M03): the hour before NOAA sunset, for Adelaide's date.
  var golden = document.querySelector("[data-golden]");
  var sunsetMinutesUTC = window.slSunset = function (y, m, d) {   // minutes UTC
    var r = Math.PI / 180, sin = Math.sin, cos = Math.cos, tan = Math.tan, lat = -34.9285 * r;
    var t = (Date.UTC(y, m - 1, d) / 864e5 + 2440587.5 - 2451545) / 36525;
    var L = (280.46646 + t * (36000.76983 + t * .0003032)) % 360 * r;
    var A = (357.52911 + t * (35999.05029 - .0001537 * t)) * r;
    var e = .016708634 - t * (.000042037 + .0000001267 * t);
    var C = sin(A) * (1.914602 - t * (.004817 + .000014 * t)) + sin(2 * A) * (.019993 - .000101 * t) + sin(3 * A) * .000289;
    var o = (125.04 - 1934.136 * t) * r;
    var eps = (23 + (26 + (21.448 - t * (46.815 + t * (.00059 - t * .001813))) / 60) / 60 + .00256 * cos(o)) * r;
    var decl = Math.asin(sin(eps) * sin((L / r + C - .00569 - .00478 * sin(o)) * r));
    var yy = Math.pow(tan(eps / 2), 2);
    var eq = 4 / r * (yy * sin(2 * L) - 2 * e * sin(A) + 4 * e * yy * sin(A) * cos(2 * L) - .5 * yy * yy * sin(4 * L) - 1.25 * e * e * sin(2 * A));
    return 720 - 4 * 138.6007 - eq + 4 * Math.acos(cos(90.833 * r) / (cos(lat) * cos(decl)) - tan(lat) * tan(decl)) / r;
  };
  var showGoldenHour = function () {
    try {   // no Intl time zones: the static text stays
      var zone = "Australia/Adelaide", day = new Intl.DateTimeFormat("en-AU", { timeZone: zone, year: "numeric", month: "numeric", day: "numeric" });
      var time = new Intl.DateTimeFormat("en-AU", { timeZone: zone, hour: "numeric", minute: "2-digit" });
      var sunsetOn = function (when) {
        var p = {};
        day.formatToParts(when).forEach(function (x) { p[x.type] = Number(x.value); });
        return Date.UTC(p.year, p.month - 1, p.day) + sunsetMinutesUTC(p.year, p.month, p.day) * 6e4;
      };
      var now = Date.now(), sunset = sunsetOn(new Date(now)), start = sunset - 36e5, text;
      if (!isFinite(sunset)) return;
      text = now < start ? "Golden hour in Adelaide tonight \u00b7 from " + time.format(start)
        : now < sunset ? "Golden hour in Adelaide now \u00b7 until " + time.format(sunset)
        : "Golden hour tomorrow \u00b7 from " + time.format(sunsetOn(new Date(now + 864e5)) - 36e5);
      golden.classList.add("is-swapping");
      setTimeout(function () { golden.textContent = text; golden.classList.remove("is-swapping"); }, motionOK() ? 300 : 0);
    } catch (e) {}
  };
  if (golden) {   // only near the footer: formatters are costly
    var near = new IntersectionObserver(function (entries) {
      if (!entries.some(function (x) { return x.isIntersecting; })) return;
      near.disconnect();
      if (window.requestIdleCallback) requestIdleCallback(showGoldenHour, { timeout: 1500 });
      else setTimeout(showGoldenHour, 200);
    }, { rootMargin: "0px 0px 900px 0px" });
    near.observe(golden);
  }

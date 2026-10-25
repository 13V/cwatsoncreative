  // Contact: "Enquire about…" links arrive with the session already chosen.
  var sessionField = document.getElementById("session");
  if (sessionField && window.URLSearchParams) {
    var wanted = new URLSearchParams(location.search).get("session");
    Array.prototype.forEach.call(sessionField.options, function (option) {
      if (wanted && option.value === wanted) sessionField.value = option.value;
    });
  }


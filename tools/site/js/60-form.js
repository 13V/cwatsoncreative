  // Enquiry form: posts JSON to the webhook in data-endpoint.
  var form = document.getElementById("enquiry-form");
  if (form) {
    var status = document.getElementById("form-status");
    var failure = document.getElementById("form-error");
    var success = document.getElementById("form-success");
    var button = form.querySelector('button[type="submit"]');
    var sending = false;
    var emailOk = function (value) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value); };

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (sending) return;
      failure.hidden = true;
      var firstProblem = null;
      ["name", "email", "message"].forEach(function (name) {
        var field = form.elements[name];
        var value = field.value.trim();
        var bad = !value || (name === "email" && !emailOk(value));
        if (bad) {
          field.setAttribute("aria-invalid", "true");
          firstProblem = firstProblem || field;
        } else {
          field.removeAttribute("aria-invalid");
        }
      });
      if (firstProblem) {
        status.textContent = "Please add your name, a valid email and a short message.";
        firstProblem.focus();
        return;
      }
      if (form.elements.company.value) { // filled in by bots only
        form.hidden = true;
        success.hidden = false;
        return;
      }
      var data = {};
      new FormData(form).forEach(function (value, key) {
        if (key !== "company") data[key] = String(value).trim();
      });
      data.submitted = new Date().toISOString();
      data.source = location.host + location.pathname;

      sending = true;
      button.disabled = true;
      status.textContent = "Sending…";
      var controller = typeof AbortController === "function" ? new AbortController() : null;
      var timer = controller ? setTimeout(function () { controller.abort(); }, 20000) : null;
      fetch(form.getAttribute("data-endpoint"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        signal: controller ? controller.signal : undefined
      }).then(function (response) {
        if (!response.ok) throw new Error("Enquiry failed");
        status.textContent = "";
        form.hidden = true;
        success.hidden = false;
        success.querySelector("h2").focus();
      }).catch(function () {
        status.textContent = "";
        failure.hidden = false;
        failure.focus();
      }).then(function () {
        if (timer) clearTimeout(timer);
        sending = false;
        button.disabled = false;
      });
    });
  }

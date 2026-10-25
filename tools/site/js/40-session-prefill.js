  // Contact: ?session=Wedding arrives with that chip chosen (§4.18).
  for (const r of document.querySelectorAll('[name="session"]')) if (r.value == new URLSearchParams(location.search).get("session")) r.checked = true;

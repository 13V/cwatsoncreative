  // Contact: ?session=Wedding (the "Enquire about…" links) arrives with that chip chosen.
  for (const r of document.querySelectorAll('[name="session"]')) if (r.value == new URLSearchParams(location.search).get("session")) r.checked = true;

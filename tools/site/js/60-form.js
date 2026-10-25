  // Enquiry (§4.18, M09, D15): a field checks on blur once typed in, and on send. #form-live sits outside the form.
  enquiry: {
    const form = document.getElementById("enquiry-form");
    if (!form) break enquiry;
    const $ = id => document.getElementById(id), err = n => $("err-" + n);
    const live = $("form-live"), card = $("form-success"), title = $("success-title"), sum = $("form-summary"),
      failure = $("form-error"), radios = [...form.elements.session], NAMES = ["name", "email", "session", "message"], typed = {};
    const attr = (el, a, on) => on ? el.setAttribute(a, "true") : el.removeAttribute(a);
    form.noValidate = true;   // without JS the browser checks

    const problem = n => {
      const d = err(n).dataset, v = n == "session" ? radios.some(r => r.checked) : form.elements[n].value.trim();
      return !v ? d.m : n == "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? d.bad : "";
    };
    const show = (n, m, s = err(n)) => {
      (n == "session" ? radios : [form.elements[n]]).forEach(el => attr(el, "aria-invalid", m));
      s.lastChild.textContent = m;
      s.classList.toggle("is-on", !!m);
    };
    form.addEventListener("input", e => {
      const n = e.target.name;
      if (NAMES.includes(n) && (typed[n] = 1) && err(n).classList.contains("is-on") && !problem(n)) show(n, "");
    });
    form.addEventListener("focusout", e => {
      const n = e.target.name;
      if (n == "session" ? !e.target.closest("fieldset").contains(e.relatedTarget) : typed[n]) show(n, problem(n));
    });
    sum.addEventListener("click", e => {
      const a = e.target.closest("a");
      if (a) { e.preventDefault(); $(a.hash.slice(1)).focus(); }
    });

    // M09: a couple whole (≤ 24 characters) or a clear first name; no titles, no surnames.
    const firstName = v => {
      v = v.trim().replace(/\s+/g, " ").replace(/[\s.,;:!?]+$/, "");
      if (/^((mr|mrs|ms|miss|mx|dr)\b|the )/i.test(v)) return "";
      if (/ (&|\+|and) /i.test(v)) return v.length > 24 ? "" : v;
      v = v.split(" ")[0];
      return !/^\p{L}[\p{L}'’-]{0,22}\p{L}$/u.test(v) ? "" : v == v.toLowerCase() || v == v.toUpperCase() ? v[0].toUpperCase() + v.slice(1).toLowerCase() : v;
    };
    const sending = on => { form.classList.toggle("is-sending", on); attr(form, "aria-busy", on); attr(form.querySelector("button"), "aria-disabled", on); };
    const sent = play => {   // motion: fields fade, the card rises through its arch (CSS)
      const n = firstName(form.elements.name.value), em = document.createElement("em"), hide = () => form.classList.add("is-sent");
      const focus = () => title.focus();
      em.textContent = n;
      title.textContent = n ? "Thank you, " : "Thank you.";
      if (n) title.append(em, ".");
      live.textContent = "Enquiry sent. " + title.textContent;
      card.hidden = false;
      form.inert = true;
      const top = card.getBoundingClientRect().top;
      if (top < 0) scrollBy(0, top - 16);   // short phones
      if (play && !motionOK()) return M.calm(form, "out").then(a => { hide(); a && a.cancel(); }), M.calm(card, "in").then(focus);
      hide();
      if (!play) return focus();
      form.parentNode.classList.add("is-sent");
      setTimeout(focus, 720);
    };

    form.addEventListener("submit", e => {
      e.preventDefault();
      if (form.classList.contains("is-sending")) return;
      failure.hidden = true;
      const bad = NAMES.filter(n => { const m = problem(n); show(n, m); return m; });
      sum.querySelectorAll("li").forEach(li => {
        li.hidden = !bad.includes(li.dataset.n);
        li.firstChild.textContent = err(li.dataset.n).lastChild.textContent;
      });
      if ((sum.hidden = !bad.length)) {
        if (form.elements._honey.value) return sent();   // honeypot: the card, nothing sent
        // FormSubmit emails it as a labelled table; Reply goes to the sender
        const v = n => form.elements[n].value.trim(), data = { _subject: `New enquiry: ${v("session")} from ${v("name")}`, _template: "table", _replyto: v("email") };
        for (const [k, n] of [["Name", "name"], ["Email", "email"], ["Phone", "phone"], ["Session", "session"], ["Date or season", "date"], ["Where", "location"], ["Message", "message"], ["How they found me", "heard"]]) if (v(n)) data[k] = v(n);
        sending(true);
        live.textContent = "Sending…";
        return fetch(form.dataset.endpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data), signal: AbortSignal.timeout(20000) })
          .then(r => r.ok ? r.json() : Promise.reject(r))
          .then(j => { if (j.success + "" != "true") throw j; sending(false); sent(1); })   // "false" until activated
          .catch(() => {   // in its kept space; values stay
            sending(false);
            failure.hidden = false;
            if (!motionOK()) M.calm(failure, "in");
            failure.focus();
            live.textContent = "Your enquiry didn’t send.";
          });
      }
      live.textContent = sum.firstChild.textContent = sum.dataset.n.split(",")[bad.length - 1] + " to check";
      sum.scrollIntoView({ block: "start" });
      sum.focus({ preventScroll: true });
    });
  }

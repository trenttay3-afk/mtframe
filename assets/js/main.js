/* MT Frame Studio — site-wide interactions
   - Nav scroll/frost behavior
   - Mobile nav drawer (tap/overlay/ESC to close)
   - IntersectionObserver reveal animations (respects prefers-reduced-motion)
   - Lightbox: keyboard nav, focus trap, neighbor-image preload, touch swipe
   - Inquiry form: branching fields by session type, honeypot, client-side store
   - Footer year stamp
*/
(function () {
  "use strict";

  // Signal that JS is active. Reveal animations only HIDE content when this
  // class is present, so if the script ever fails to run the galleries stay
  // fully visible rather than stuck at opacity:0.
  document.documentElement.classList.add("js");

  const prefersReduced =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Nav scroll state ---------- */
  const nav = document.querySelector(".nav");
  if (nav) {
    const onScroll = () => {
      if (window.scrollY > 20) nav.classList.add("scrolled");
      else nav.classList.remove("scrolled");
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Mobile nav ---------- */
  const toggle = document.querySelector(".nav__toggle");
  const links = document.querySelector(".nav__links");
  if (toggle && links && nav) {
    const close = () => {
      links.classList.remove("open");
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    };
    const open = () => {
      links.classList.add("open");
      nav.classList.add("open");
      toggle.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
    };
    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      links.classList.contains("open") ? close() : open();
    });
    links.querySelectorAll("a").forEach((a) => a.addEventListener("click", close));
    links.addEventListener("click", (e) => {
      if (e.target === links) close();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && links.classList.contains("open")) close();
    });
  }

  /* ---------- Reveal on scroll ----------
     Gallery photos reveal individually with a gentle stagger. Each <figure>
     is a small element, so the observer fires reliably regardless of how tall
     the overall gallery is — this is the fix for galleries that stayed black
     on mobile, where the old container-level reveal could never cross a 10%
     visibility threshold on a very tall single-column grid. */
  const figures = Array.prototype.slice.call(
    document.querySelectorAll(".masonry figure")
  );
  figures.forEach((fig, i) => {
    fig.classList.add("reveal", "reveal--fig");
    // Stagger within a row group; cap the delay so later images aren't slow.
    fig.style.setProperty("--reveal-delay", (i % 3) * 90 + "ms");
  });

  const revealEls = Array.prototype.slice
    .call(document.querySelectorAll(".reveal"))
    .concat(figures);

  if (prefersReduced || !("IntersectionObserver" in window)) {
    revealEls.forEach((el) => el.classList.add("in"));
  } else {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      // threshold 0: fire as soon as ANY part enters — never depends on the
      // element being a fraction of its own (possibly huge) height.
      { threshold: 0, rootMargin: "0px 0px -8% 0px" }
    );
    revealEls.forEach((el) => io.observe(el));
  }

  /* ---------- Lightbox ---------- */
  const lb = document.querySelector(".lightbox");
  if (lb) {
    const lbImg = lb.querySelector("img");
    const lbCap = lb.querySelector(".lightbox__cap");
    const closeBtn = lb.querySelector(".lightbox__close");
    const prevBtn = lb.querySelector(".lightbox__prev");
    const nextBtn = lb.querySelector(".lightbox__next");
    const figures = Array.from(document.querySelectorAll(".masonry figure"));
    let idx = 0;
    let lastFocus = null;
    let touchStartX = 0;

    const preload = (i) => {
      if (i < 0 || i >= figures.length) return;
      const url =
        figures[i].dataset.full || figures[i].querySelector("img").src;
      const img = new Image();
      img.src = url;
    };

    const open = (i) => {
      idx = i;
      const fig = figures[idx];
      const full = fig.dataset.full || fig.querySelector("img").src;
      const cap = fig.querySelector("figcaption")?.textContent || "";
      lbImg.src = full;
      lbImg.alt = cap || "Photograph by MT Frame Studio";
      lbCap.textContent = cap;
      lb.classList.add("open");
      lb.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      lastFocus = document.activeElement;
      closeBtn.focus();
      // Preload neighbors for snappy arrow navigation
      preload((idx + 1) % figures.length);
      preload((idx - 1 + figures.length) % figures.length);
    };
    const close = () => {
      lb.classList.remove("open");
      lb.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    };
    const next = () => open((idx + 1) % figures.length);
    const prev = () => open((idx - 1 + figures.length) % figures.length);

    figures.forEach((fig, i) => {
      fig.setAttribute("tabindex", "0");
      fig.setAttribute("role", "button");
      fig.setAttribute(
        "aria-label",
        "View " + (fig.querySelector("figcaption")?.textContent || "photo") + " in lightbox"
      );
      fig.addEventListener("click", () => open(i));
      fig.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          open(i);
        }
      });
    });
    closeBtn.addEventListener("click", close);
    nextBtn.addEventListener("click", next);
    prevBtn.addEventListener("click", prev);
    lb.addEventListener("click", (e) => {
      if (e.target === lb) close();
    });
    document.addEventListener("keydown", (e) => {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowRight") next();
      else if (e.key === "ArrowLeft") prev();
      // Focus trap — keep tab cycling between the three controls
      else if (e.key === "Tab") {
        const focusables = [prevBtn, nextBtn, closeBtn];
        const cur = focusables.indexOf(document.activeElement);
        if (cur === -1) {
          e.preventDefault();
          closeBtn.focus();
          return;
        }
        if (e.shiftKey && cur === 0) {
          e.preventDefault();
          focusables[focusables.length - 1].focus();
        } else if (!e.shiftKey && cur === focusables.length - 1) {
          e.preventDefault();
          focusables[0].focus();
        }
      }
    });
    // Touch swipe
    lb.addEventListener(
      "touchstart",
      (e) => {
        touchStartX = e.changedTouches[0].screenX;
      },
      { passive: true }
    );
    lb.addEventListener(
      "touchend",
      (e) => {
        const dx = e.changedTouches[0].screenX - touchStartX;
        if (Math.abs(dx) > 40) {
          if (dx < 0) next();
          else prev();
        }
      },
      { passive: true }
    );
  }

  /* ---------- Success modal (floating confirmation) ---------- */
  const successModal = document.querySelector("#success-modal");
  let lastFocusBeforeModal = null;
  const openSuccessModal = () => {
    if (!successModal) return;
    lastFocusBeforeModal = document.activeElement;
    successModal.classList.add("open");
    successModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const closeBtn = successModal.querySelector(".success-modal__close");
    if (closeBtn) closeBtn.focus();
  };
  const closeSuccessModal = () => {
    if (!successModal) return;
    successModal.classList.remove("open");
    successModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (lastFocusBeforeModal && lastFocusBeforeModal.focus) lastFocusBeforeModal.focus();
  };
  if (successModal) {
    successModal
      .querySelectorAll("[data-close-success]")
      .forEach((el) => el.addEventListener("click", closeSuccessModal));
    successModal.addEventListener("click", (e) => {
      if (e.target === successModal) closeSuccessModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && successModal.classList.contains("open")) closeSuccessModal();
    });
  }

  /* ---------- Inquiry form: branching + honeypot + Formspree submit ---------- */
  const FORMSPREE_ENDPOINT = "https://formspree.io/f/mvznnvql";

  const form = document.querySelector("#contact-form");
  if (form) {
    const typeSel = form.querySelector("#c-type");
    const branches = form.querySelectorAll(".branch");

    const syncBranches = () => {
      const val = typeSel ? typeSel.value : "";
      branches.forEach((b) => {
        const allow = (b.dataset.branch || "").split(",").map((s) => s.trim());
        const show = allow.includes(val);
        b.hidden = !show;
        // Disable inputs in hidden branches so they don't submit
        b.querySelectorAll("input, select, textarea").forEach((el) => {
          el.disabled = !show;
        });
      });
    };
    /* Pre-fill from query params when arriving from an Investment collection,
       e.g. contact.html?type=Wedding&package=The%20Heirloom. Sets the session
       type (which reveals the matching branch), records the package for the
       submission, suggests a budget range, and shows a small confirmation. */
    const prefillFromQuery = () => {
      const params = new URLSearchParams(window.location.search);

      const typeVal = params.get("type");
      if (typeVal && typeSel) {
        const opt = Array.prototype.find.call(
          typeSel.options,
          (o) => o.value.toLowerCase() === typeVal.toLowerCase()
        );
        if (opt) typeSel.value = opt.value;
      }

      const pkg = params.get("package");
      if (pkg) {
        const pkgInput = form.querySelector("#c-package");
        if (pkgInput) pkgInput.value = pkg;

        const notice = document.querySelector("#package-notice");
        if (notice) {
          const nameEl = notice.querySelector("[data-package-name]");
          if (nameEl) nameEl.textContent = pkg;
          notice.hidden = false;
        }

        // Suggest a budget range to match the chosen collection (editable).
        const budgetByPackage = {
          "The Sonnet": "$1,000–$2,000",
          "The Heirloom": "$2,000–$3,500",
          "The Archive": "$3,500–$5,000",
          "Mini Session": "Under $500",
          "Signature Session": "$500–$1,000",
          "Maternity & Fresh 48": "$500–$1,000",
        };
        const budgetSel = form.querySelector("#c-budget");
        const wanted = budgetByPackage[pkg];
        if (budgetSel && wanted) {
          const match = Array.prototype.find.call(
            budgetSel.options,
            (o) => o.value === wanted || o.text === wanted
          );
          if (match) budgetSel.value = match.value || match.text;
        }
      }
    };
    prefillFromQuery();

    if (typeSel) {
      typeSel.addEventListener("change", syncBranches);
      syncBranches();
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const statusEl = form.querySelector(".form-status");
      const submitBtn = form.querySelector('button[type="submit"]');

      // Honeypot — if filled, silently pretend success and drop the request
      const hp = form.querySelector('[name="website"]');
      if (hp && hp.value) {
        form.reset();
        openSuccessModal();
        return;
      }

      // Build the FormData that actually gets sent. We append the pretty
      // subject line and Reply-To header directly onto the FormData so
      // Formspree picks them up (setting them on a sibling object did nothing).
      const fd = new FormData(form);
      const sessionType = fd.get("type") || "inquiry";
      const inquirer = fd.get("name") || "(no name)";
      fd.set("_subject", `New ${sessionType} inquiry from ${inquirer}`);
      const emailVal = fd.get("email");
      if (emailVal) fd.set("_replyto", emailVal);

      statusEl.style.color = "var(--gold)";
      statusEl.textContent = "Sending…";
      if (submitBtn) submitBtn.disabled = true;

      try {
        const res = await fetch(FORMSPREE_ENDPOINT, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: fd,
        });

        if (res.ok) {
          statusEl.textContent = "";
          form.reset();
          syncBranches();
          openSuccessModal();
        } else {
          // Surface whatever Formspree actually returned so we can see
          // the real reason (unactivated form, reCAPTCHA mismatch, etc.).
          let detail = `Formspree returned ${res.status}`;
          if (res.statusText) detail += " " + res.statusText;
          try {
            const body = await res.json();
            if (body) {
              if (Array.isArray(body.errors) && body.errors.length) {
                detail = body.errors
                  .map((x) => x.message || x.field || x.code || "error")
                  .join(", ");
              } else if (typeof body.error === "string") {
                detail = body.error;
              }
            }
          } catch (_) {
            /* non-JSON response — keep the HTTP status line */
          }
          statusEl.style.color = "#d97a6c";
          statusEl.textContent =
            detail +
            ". Please email trent@mtframestudio.com directly.";
          // Also log for the site owner's devtools
          console.warn("[MT Frame Studio] Formspree submission failed:", detail);
        }
      } catch (err) {
        statusEl.style.color = "#d97a6c";
        statusEl.textContent =
          "Network error: " +
          (err && err.message ? err.message : "unknown") +
          ". Please email trent@mtframestudio.com directly.";
        console.warn("[MT Frame Studio] Formspree network error:", err);
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  /* ---------- Mobile masonry: tag landscapes for full-width column-span ---------- */
  document.querySelectorAll(".masonry figure img").forEach((img) => {
    const w = parseInt(img.getAttribute("width") || 0);
    const h = parseInt(img.getAttribute("height") || 0);
    img.closest("figure").classList.add(h > w ? "orient-portrait" : "orient-landscape");
  });

  /* ---------- Footer year ---------- */
  const yr = document.querySelector("[data-year]");
  if (yr) yr.textContent = new Date().getFullYear();
})();

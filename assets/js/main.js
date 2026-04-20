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

  /* ---------- Reveal on scroll ---------- */
  if (prefersReduced) {
    document.querySelectorAll(".reveal").forEach((el) => el.classList.add("in"));
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
      { threshold: 0.1, rootMargin: "0px 0px -80px 0px" }
    );
    document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
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

  /* ---------- Inquiry form: branching + honeypot + Formspree submit ---------- */
  const FORMSPREE_ENDPOINT = "https://formspree.io/f/xjgjowon";

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
        statusEl.textContent = "Thank you. Your inquiry has been received.";
        form.reset();
        return;
      }

      // Build the submission payload
      const data = Object.fromEntries(new FormData(form).entries());
      const sessionType = data.type || "inquiry";
      const inquirer = data.name || "(no name)";
      // Pretty subject line for the email Formspree sends to your inbox
      data._subject = `New ${sessionType} inquiry from ${inquirer}`;
      // Make "reply" in Gmail go straight back to the inquirer
      if (data.email) data._replyto = data.email;

      statusEl.style.color = "var(--gold)";
      statusEl.textContent = "Sending…";
      if (submitBtn) submitBtn.disabled = true;

      try {
        const res = await fetch(FORMSPREE_ENDPOINT, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: new FormData(form),
        });

        if (res.ok) {
          statusEl.style.color = "var(--gold)";
          statusEl.textContent =
            "Thank you. Your inquiry has been received. Megan & Trent will be in touch within 48 business hours.";
          form.reset();
          syncBranches();
          setTimeout(() => {
            statusEl.textContent = "";
          }, 12000);
        } else {
          const body = await res.json().catch(() => ({}));
          const msg =
            (body && body.errors && body.errors.map((x) => x.message).join(", ")) ||
            "Something went wrong sending your inquiry. Please email mtframephotography@gmail.com directly.";
          statusEl.style.color = "#d97a6c";
          statusEl.textContent = msg;
        }
      } catch (err) {
        statusEl.style.color = "#d97a6c";
        statusEl.textContent =
          "Network error sending your inquiry. Please email mtframephotography@gmail.com directly.";
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  /* ---------- Footer year ---------- */
  const yr = document.querySelector("[data-year]");
  if (yr) yr.textContent = new Date().getFullYear();
})();

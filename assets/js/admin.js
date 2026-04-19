/* MT Frame Studio — admin (demo) */
(function () {
  "use strict";

  const SESSION_KEY = "mtfs_session";
  const GALLERY_KEY = "mtfs_gallery";
  const INQUIRY_KEY = "mtfs_inquiries";

  // --------- DEMO credentials ---------
  // NOTE: client-side auth only. Swap for a real backend before production.
  const DEMO_USER = "admin";
  const DEMO_PASS = "mtframe2026";

  // Default gallery seed — matches the filesystem layout produced by build_images.py
  const SEED = {
    weddings: [
      { id: "w01", src: "01", cap: "Snow Canyon engagement" },
      { id: "w02", src: "02", cap: "A stolen moment" },
      { id: "w03", src: "03", cap: "Winter whispers" },
    ],
    portraits: [
      { id: "p01", src: "01", cap: "Beach sunset portrait" },
      { id: "p02", src: "02", cap: "Golden hour profile" },
      { id: "p03", src: "03", cap: "Coastal evening" },
      { id: "p04", src: "04", cap: "Reflections at dusk" },
      { id: "p05", src: "05", cap: "Quiet breath" },
      { id: "p06", src: "06", cap: "Into the waves" },
      { id: "p07", src: "07", cap: "First snow" },
      { id: "p08", src: "08", cap: "Red rock reflection" },
      { id: "p09", src: "09", cap: "The adventurer" },
      { id: "p10", src: "10", cap: "Summer siblings" },
      { id: "p11", src: "11", cap: "Mother & son" },
    ],
    maternity: [
      { id: "m01", src: "01", cap: "Bridge at dawn" },
      { id: "m02", src: "02", cap: "Expecting joy" },
      { id: "m03", src: "03", cap: "The three of us" },
      { id: "m04", src: "04", cap: "Mommy to bee" },
      { id: "m05", src: "05", cap: "A little honey" },
      { id: "m06", src: "06", cap: "Welcome, Noah" },
      { id: "m07", src: "07", cap: "Mother & daughter" },
      { id: "m08", src: "08", cap: "Generations" },
      { id: "m09", src: "09", cap: "Sisters & the bump" },
      { id: "m10", src: "10", cap: "Best friends forever" },
      { id: "m11", src: "11", cap: "Garden trio" },
      { id: "m12", src: "12", cap: "Family portrait" },
    ],
    events: [
      { id: "e01", src: "01", cap: "Mommy to Bee welcome" },
      { id: "e02", src: "02", cap: "Honey favor table" },
      { id: "e03", src: "03", cap: "Don't Say Baby" },
      { id: "e04", src: "04", cap: "Themed sweets" },
      { id: "e05", src: "05", cap: "The bridal party" },
      { id: "e06", src: "06", cap: "Garden gathering" },
      { id: "e07", src: "07", cap: "Four friends" },
      { id: "e08", src: "08", cap: "Table of laughter" },
      { id: "e09", src: "09", cap: "Under the tent" },
      { id: "e10", src: "10", cap: "Welcome cake" },
    ],
  };

  function loadGallery() {
    try {
      const raw = localStorage.getItem(GALLERY_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return JSON.parse(JSON.stringify(SEED));
  }
  function saveGallery(g) { localStorage.setItem(GALLERY_KEY, JSON.stringify(g)); }
  function loadInquiries() {
    try { return JSON.parse(localStorage.getItem(INQUIRY_KEY) || "[]"); }
    catch (e) { return []; }
  }

  function requireAuth() {
    const s = localStorage.getItem(SESSION_KEY);
    if (!s) { window.location.href = "login.html"; return false; }
    try {
      const obj = JSON.parse(s);
      if (!obj.exp || obj.exp < Date.now()) {
        localStorage.removeItem(SESSION_KEY);
        window.location.href = "login.html";
        return false;
      }
    } catch (e) { window.location.href = "login.html"; return false; }
    return true;
  }

  // ---------- LOGIN PAGE ----------
  const loginForm = document.querySelector("#login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const u = loginForm.querySelector("[name=username]").value.trim();
      const p = loginForm.querySelector("[name=password]").value;
      const err = document.querySelector(".admin-error");
      if (u === DEMO_USER && p === DEMO_PASS) {
        localStorage.setItem(SESSION_KEY, JSON.stringify({
          user: u, exp: Date.now() + 1000 * 60 * 60 * 8   // 8 hours
        }));
        window.location.href = "dashboard.html";
      } else {
        err.textContent = "Invalid credentials. Try admin / mtframe2026 for the demo.";
      }
    });
  }

  // ---------- DASHBOARD ----------
  const dash = document.querySelector("#dashboard");
  if (dash) {
    if (!requireAuth()) return;

    // Logout
    document.querySelector("#logout")?.addEventListener("click", () => {
      localStorage.removeItem(SESSION_KEY);
      window.location.href = "login.html";
    });

    let gallery = loadGallery();
    const inquiries = loadInquiries();

    // Stats
    const total = Object.values(gallery).reduce((n, arr) => n + arr.length, 0);
    document.querySelector("[data-stat=photos]").textContent = total;
    document.querySelector("[data-stat=galleries]").textContent = Object.keys(gallery).length;
    document.querySelector("[data-stat=inquiries]").textContent = inquiries.length;
    document.querySelector("[data-stat=unread]").textContent =
      inquiries.filter(i => !i.read).length;

    // Tabs
    const tabs = dash.querySelectorAll(".dash-tabs button");
    const panels = dash.querySelectorAll(".dash-panel");
    tabs.forEach(t => t.addEventListener("click", () => {
      tabs.forEach(x => x.classList.remove("active"));
      panels.forEach(p => p.classList.remove("active"));
      t.classList.add("active");
      document.querySelector(`#panel-${t.dataset.tab}`).classList.add("active");
    }));

    // Gallery panels
    function renderGallery() {
      ["weddings", "portraits", "maternity", "events"].forEach(cat => {
        const host = document.querySelector(`#ge-${cat}`);
        if (!host) return;
        host.innerHTML = "";
        gallery[cat].forEach((item, i) => {
          const tile = document.createElement("div");
          tile.className = "tile";
          tile.draggable = true;
          tile.dataset.idx = i;
          tile.dataset.cat = cat;
          tile.innerHTML = `
            <img src="../assets/images/${cat}/${item.src}-thumb.jpg" alt="${item.cap}">
            <div class="tile__actions">
              <button data-action="up">◀</button>
              <button data-action="remove">remove</button>
              <button data-action="down">▶</button>
            </div>`;
          host.appendChild(tile);
        });
      });
    }
    renderGallery();

    // Action handlers (delegated)
    dash.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-action]");
      if (!btn) return;
      const tile = btn.closest(".tile");
      if (!tile) return;
      const cat = tile.dataset.cat;
      const i = parseInt(tile.dataset.idx, 10);
      const arr = gallery[cat];
      if (btn.dataset.action === "remove") {
        arr.splice(i, 1);
      } else if (btn.dataset.action === "up" && i > 0) {
        [arr[i - 1], arr[i]] = [arr[i], arr[i - 1]];
      } else if (btn.dataset.action === "down" && i < arr.length - 1) {
        [arr[i + 1], arr[i]] = [arr[i], arr[i + 1]];
      }
      saveGallery(gallery);
      renderGallery();
    });

    // Reset button
    document.querySelector("#reset-gallery")?.addEventListener("click", () => {
      if (confirm("Reset gallery order & removals to default? Inquiries will be kept.")) {
        localStorage.removeItem(GALLERY_KEY);
        gallery = loadGallery();
        renderGallery();
      }
    });

    // Inquiries panel
    const inqHost = document.querySelector("#inquiry-list");
    if (inqHost) {
      if (inquiries.length === 0) {
        inqHost.innerHTML = `<p class="muted">No inquiries yet. When someone submits the contact form, it'll appear here.</p>`;
      } else {
        inqHost.innerHTML = inquiries.map(inq => `
          <div class="inquiry">
            <div>
              <h4>${escapeHTML(inq.name || "Anonymous")}
                <span class="muted" style="font-weight:300;"> · ${escapeHTML(inq.type || "General")}</span>
              </h4>
              <div class="meta">${escapeHTML(inq.email || "")}${inq.date ? " · " + escapeHTML(inq.date) : ""}</div>
              <p>${escapeHTML(inq.message || "")}</p>
            </div>
            <div class="muted" style="font-size:.7rem;letter-spacing:.18em;">${new Date(inq.ts || Date.now()).toLocaleDateString()}</div>
          </div>
        `).join("");
      }
    }
  }

  function escapeHTML(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
    }[c]));
  }
})();

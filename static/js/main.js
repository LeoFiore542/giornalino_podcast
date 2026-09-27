(function () {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function revealOnLoad() {
    const nodes = document.querySelectorAll(".reveal");
    if (reduced) {
      nodes.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    if (!("IntersectionObserver" in window)) {
      nodes.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -5% 0px" }
    );

    nodes.forEach((el) => observer.observe(el));
  }

  function initViewToggle() {
    const catalog = document.querySelector(".media-catalog");
    const buttons = document.querySelectorAll(".view-btn");
    if (!catalog || !buttons.length) return;

    const storageKey = "voce-view-" + (document.body.classList.contains("page-podcast") ? "podcast" : "giornalino");
    const saved = localStorage.getItem(storageKey);
    if (saved === "grid" || saved === "list") {
      setView(saved);
    }

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const view = btn.getAttribute("data-view");
        if (!view) return;
        setView(view);
        localStorage.setItem(storageKey, view);
      });
    });

    function setView(view) {
      catalog.setAttribute("data-view", view);
      buttons.forEach((btn) => {
        const active = btn.getAttribute("data-view") === view;
        btn.classList.toggle("is-active", active);
        btn.setAttribute("aria-pressed", active ? "true" : "false");
      });
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    revealOnLoad();
    initViewToggle();
    initCookieBanner();
    initStorageModal();
    initPublishPreview();
  });

  function initCookieBanner() {
    const banner = document.getElementById("cookie-banner");
    const accept = document.getElementById("cookie-accept");
    if (!banner || !accept) return;

    const key = "voce-cookie-notice";
    if (!localStorage.getItem(key)) {
      banner.hidden = false;
    }

    accept.addEventListener("click", () => {
      localStorage.setItem(key, "1");
      banner.hidden = true;
    });
  }

  function initStorageModal() {
    const modal = document.getElementById("storage-modal");
    const openBtn = document.getElementById("storage-open");
    const form = document.getElementById("storage-modal-form");
    const errorEl = document.getElementById("storage-modal-error");
    const passwordInput = document.getElementById("storage-password");
    const submitBtn = document.getElementById("storage-submit");
    if (!modal || !form) return;

    function openModal() {
      modal.hidden = false;
      document.body.classList.add("modal-open");
      if (errorEl) {
        errorEl.hidden = true;
        errorEl.textContent = "";
      }
      if (form) form.reset();
      window.setTimeout(() => passwordInput && passwordInput.focus(), 50);
    }

    function closeModal() {
      modal.hidden = true;
      document.body.classList.remove("modal-open");
    }

    if (openBtn) {
      openBtn.addEventListener("click", openModal);
    }

    modal.querySelectorAll("[data-storage-close]").forEach((el) => {
      el.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !modal.hidden) closeModal();
    });

    const params = new URLSearchParams(window.location.search);
    if (params.get("storage_login") === "1" && openBtn) {
      openModal();
      params.delete("storage_login");
      const next = params.toString();
      const clean = window.location.pathname + (next ? "?" + next : "") + window.location.hash;
      window.history.replaceState({}, "", clean);
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (errorEl) {
        errorEl.hidden = true;
        errorEl.textContent = "";
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Verifica…";
      }

      try {
        const body = new FormData(form);
        const response = await fetch("/storage/auth", {
          method: "POST",
          body,
          credentials: "same-origin",
          headers: { Accept: "application/json" },
        });
        const data = await response.json().catch(() => ({}));

        if (!response.ok || !data.ok) {
          if (errorEl) {
            errorEl.textContent = data.error || "Password non corretta.";
            errorEl.hidden = false;
          }
          if (passwordInput) {
            passwordInput.focus();
            passwordInput.select();
          }
          return;
        }

        window.location.href = data.redirect || "/storage/dashboard";
      } catch (err) {
        if (errorEl) {
          errorEl.textContent = "Errore di connessione. Riprova.";
          errorEl.hidden = false;
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Entra";
        }
      }
    });
  }

  function initPublishPreview() {
    const form = document.getElementById("publish-form");
    if (!form) return;

    const nextVolume = Number(form.dataset.nextVolume || 1);
    const nextEpisode = Number(form.dataset.nextEpisode || 1);
    const todayLabel = form.dataset.todayLabel || "";

    const titleInput = document.getElementById("pub-title");
    const descInput = document.getElementById("pub-description");
    const numberInput = document.getElementById("pub-number");
    const mainInput = document.getElementById("pub-main");
    const coverInput = document.getElementById("pub-cover");
    const numberLabel = document.getElementById("number-label");
    const numberHint = document.getElementById("number-hint");
    const mainLabel = document.getElementById("main-label");
    const mainHint = document.getElementById("main-hint");

    const previewCover = document.getElementById("preview-cover");
    const previewMark = document.getElementById("preview-mark");
    const previewBadge = document.getElementById("preview-badge");
    const previewDate = document.getElementById("preview-date");
    const previewTitle = document.getElementById("preview-title");
    const previewDesc = document.getElementById("preview-desc");
    const previewCta = document.getElementById("preview-cta");

    let coverObjectUrl = null;

    function selectedKind() {
      const checked = form.querySelector('input[name="kind"]:checked');
      return checked ? checked.value : "giornalino";
    }

    function pad2(n) {
      const num = Number(n) || 0;
      return String(num).padStart(2, "0");
    }

    function syncKindUI() {
      const kind = selectedKind();
      const isGiornalino = kind === "giornalino";
      if (numberLabel) {
        numberLabel.textContent = isGiornalino ? "Numero volume" : "Numero episodio";
      }
      if (numberHint) {
        numberHint.textContent = isGiornalino
          ? "Suggerito dal sito: prossimo volume disponibile. Puoi modificarlo."
          : "Suggerito dal sito: prossimo episodio disponibile. Puoi modificarlo.";
      }
      if (mainLabel) {
        mainLabel.textContent = isGiornalino ? "File del corpo (PDF)" : "File del corpo (MP3)";
      }
      if (mainHint) {
        mainHint.textContent = isGiornalino
          ? "Per il giornalino carica un PDF."
          : "Per il podcast carica un file MP3.";
      }
      if (mainInput) {
        mainInput.accept = isGiornalino ? ".pdf,application/pdf" : ".mp3,audio/mpeg";
        mainInput.value = "";
      }
      if (numberInput) {
        numberInput.value = String(isGiornalino ? nextVolume : nextEpisode);
      }
      if (previewCover) {
        previewCover.classList.remove("cover-spring", "cover-mic", "has-image");
        previewCover.classList.add(isGiornalino ? "cover-spring" : "cover-mic");
        previewCover.style.backgroundImage = "";
      }
      if (coverObjectUrl) {
        URL.revokeObjectURL(coverObjectUrl);
        coverObjectUrl = null;
      }
      if (coverInput) coverInput.value = "";
      if (previewCta) {
        previewCta.textContent = isGiornalino ? "Apri PDF" : "Ascolta";
      }
      updatePreview();
    }

    function updatePreview() {
      const kind = selectedKind();
      const isGiornalino = kind === "giornalino";
      const number = numberInput && numberInput.value ? numberInput.value : isGiornalino ? nextVolume : nextEpisode;
      const title = (titleInput && titleInput.value.trim()) || "Titolo del contenuto";
      const desc =
        (descInput && descInput.value.trim()) || "La descrizione apparirà qui.";

      if (previewMark) {
        previewMark.textContent = (isGiornalino ? "Vol. " : "Ep. ") + pad2(number);
      }
      if (previewBadge) {
        previewBadge.textContent = (isGiornalino ? "Volume " : "Episodio ") + number;
      }
      if (previewDate) previewDate.textContent = todayLabel;
      if (previewTitle) previewTitle.textContent = title;
      if (previewDesc) previewDesc.textContent = desc;
    }

    form.querySelectorAll('input[name="kind"]').forEach((radio) => {
      radio.addEventListener("change", syncKindUI);
    });

    [titleInput, descInput, numberInput].forEach((el) => {
      if (el) el.addEventListener("input", updatePreview);
    });

    if (coverInput) {
      coverInput.addEventListener("change", () => {
        if (coverObjectUrl) {
          URL.revokeObjectURL(coverObjectUrl);
          coverObjectUrl = null;
        }
        const file = coverInput.files && coverInput.files[0];
        if (file && previewCover) {
          coverObjectUrl = URL.createObjectURL(file);
          previewCover.style.backgroundImage = "url('" + coverObjectUrl + "')";
          previewCover.classList.add("has-image");
        } else if (previewCover) {
          previewCover.style.backgroundImage = "";
          previewCover.classList.remove("has-image");
        }
      });
    }

    syncKindUI();
  }
})();

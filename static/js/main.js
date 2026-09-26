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
  });
})();

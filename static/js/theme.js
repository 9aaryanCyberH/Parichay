/**
 * Parichay — Shared Theme Controller
 * Handles Light/Dark mode state, button icons, and localStorage persistence.
 *
 * Requirements:
 * - Default to 'light' theme on initial load.
 * - In Light theme: Display Moon button (🌙) to switch to Dark mode.
 * - In Dark theme: Display Sun button (☀️) to switch to Light mode.
 * - Smooth transition and persistence in localStorage.
 */

(function () {
  "use strict";

  // Apply theme immediately if running after DOM or inline
  function applyTheme(theme) {
    const validTheme = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", validTheme);
    if (document.body) {
      document.body.setAttribute("data-theme", validTheme);
    }

    const themeBtn = document.getElementById("themeToggleBtn");
    if (themeBtn) {
      if (validTheme === "dark") {
        themeBtn.setAttribute("title", "Switch to light mode");
        themeBtn.setAttribute("aria-label", "Switch to light mode");
      } else {
        themeBtn.setAttribute("title", "Switch to dark mode");
        themeBtn.setAttribute("aria-label", "Switch to dark mode");
      }
    }

    // Update Chart.js if present on the page (Studio view)
    if (typeof window.updateRadarChartTheme === "function") {
      try {
        window.updateRadarChartTheme(validTheme);
      } catch (e) {
        console.warn("Chart theme update hook failed:", e);
      }
    }
  }

  // Toggle between light and dark
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    localStorage.setItem("parichay-theme", nextTheme);
    applyTheme(nextTheme);
  }

  // Initialize theme button click listener
  function initTheme() {
    // Determine stored preference, strictly defaulting to 'light'
    const stored = localStorage.getItem("parichay-theme");
    const activeTheme = stored === "dark" ? "dark" : "light";
    applyTheme(activeTheme);

    const themeBtn = document.getElementById("themeToggleBtn");
    if (themeBtn && !themeBtn._themeBound) {
      themeBtn._themeBound = true;
      themeBtn.addEventListener("click", (e) => {
        e.preventDefault();
        toggleTheme();
      });
    }
  }

  // Expose to window for external callers
  window.ParichayTheme = {
    applyTheme: applyTheme,
    toggleTheme: toggleTheme,
    initTheme: initTheme,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTheme);
  } else {
    initTheme();
  }
})();

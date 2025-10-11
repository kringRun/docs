/**
 * Minimal script to add CSS classes for hiding the sidebar.
 *
 * This script adds CSS classes to the body element based on URL
 */
(function () {
  "use strict";

  function addSidebarClasses() {
    const currentPath = window.location.pathname;
    const body = document.body;

    // Remove existing classes
    body.classList.remove("hide-sidebar");

    // Add appropriate class based on URL
    if (currentPath === "/" || currentPath === "/index") {
      body.classList.add("hide-sidebar");
    }
  }

  // Run immediately
  addSidebarClasses();

  // Run on page load
  document.addEventListener("DOMContentLoaded", addSidebarClasses);

  // Run on navigation
  window.addEventListener("popstate", addSidebarClasses);

  // Watch for URL changes (SPA navigation)
  let lastUrl = location.href;
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      addSidebarClasses();
    }
  }).observe(document, { subtree: true, childList: true });
})();

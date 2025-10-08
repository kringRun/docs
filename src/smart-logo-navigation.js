// Smart logo navigation - redirects to the current dropdown's first page
(function() {
  // Wait for DOM to be ready
  function initSmartLogoNav() {
    const logo = document.querySelector('a[href="/"]') || document.querySelector('a[href*="langchain.com"]');

    if (!logo) {
      // Try again after a short delay if logo not found
      setTimeout(initSmartLogoNav, 100);
      return;
    }

    logo.addEventListener('click', function(e) {
      const currentPath = window.location.pathname;
      let destination = '/'; // Default to homepage

      // Determine destination based on current path
      if (currentPath.includes('/oss/python/')) {
        destination = '/oss/python/langchain/overview';
      } else if (currentPath.includes('/oss/javascript/')) {
        destination = '/oss/javascript/langchain/overview';
      } else if (currentPath.includes('/langgraph-platform/')) {
        destination = '/langgraph-platform/index';
      } else if (currentPath.includes('/langsmith/')) {
        destination = '/langsmith/home';
      } else if (currentPath.includes('/labs/')) {
        destination = '/labs/index';
      }

      // If we determined a specific destination, navigate to it
      if (destination !== '/') {
        e.preventDefault();
        window.location.href = destination;
      }
      // Otherwise, let the default behavior happen (go to homepage)
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSmartLogoNav);
  } else {
    initSmartLogoNav();
  }
})();

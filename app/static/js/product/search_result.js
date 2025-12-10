// Use addEventListener instead of overriding window.onload to preserve existing functionality
window.addEventListener('load', function() {
  // Function to redirect to product detail page
  function redirectToProductDetail(slug) {
    // Show notification to select size on product detail page
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #dc2626;
      color: white;
      padding: 16px 24px;
      border-radius: 8px;
      font-family: 'Inter', sans-serif;
      font-size: 14px;
      font-weight: 500;
      z-index: 10000;
      animation: slideInRight 300ms ease-out;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    notification.textContent = 'Please select a size on the product detail page';
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.animation = 'slideOutRight 300ms ease-in';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
    
    // Redirect to product detail page after a short delay
    setTimeout(() => {
      window.location.href = `/productInfo/${slug}/`;
    }, 1000);
  }
  
  // Add notification animations to CSS
  const notificationStyles = document.createElement('style');
  notificationStyles.textContent = `
    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    @keyframes slideOutRight {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(notificationStyles);
  
  // Make the redirect function available globally
  window.redirectToProductDetail = redirectToProductDetail;
  
  // Touch device detection for hover effects
  function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  }
  
  if (isTouchDevice()) {
    // Remove hover effects on touch devices
    const style = document.createElement('style');
    style.textContent = `
      .dripspace-product-card:hover .product-hover-overlay {
        opacity: 0;
      }
      .dripspace-product-card:hover .product-image {
        transform: none;
      }
      .dripspace-product-card:hover .product-name::after {
        transform: scaleX(0);
      }
    `;
    document.head.appendChild(style);
  }
});

// Focus on search input when page loads if there's a query
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    // Small delay to ensure the element is ready
    setTimeout(function() {
      // Focus on the search input
      searchInput.focus();
      
      // Select all text if there's already a query
      if (searchInput.value) {
        searchInput.select();
      }
    }, 100);
    
    // Submit form when Enter is pressed in search input
    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const form = searchInput.closest('form');
        if (searchInput.value.trim()) {
          form.submit();
        }
      }
    });
  }
});
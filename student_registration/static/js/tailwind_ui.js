(function () {
  function hideModal(modal) {
    if (!modal) return;
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
  }

  function showModal(modal) {
    if (!modal) return;
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
  }

  function closeAllDropdowns(exceptMenu) {
    document.querySelectorAll('.dropdown-menu.show').forEach(function (menu) {
      if (menu !== exceptMenu) menu.classList.remove('show');
    });
  }

  document.addEventListener('click', function (event) {
    var dropdownToggle = event.target.closest('[data-toggle="dropdown"]');
    if (dropdownToggle) {
      event.preventDefault();
      var dropdown = dropdownToggle.closest('.dropdown, .btn-group') || dropdownToggle.parentElement;
      var menu = dropdown ? dropdown.querySelector('.dropdown-menu') : null;
      if (menu) {
        var willShow = !menu.classList.contains('show');
        closeAllDropdowns();
        if (willShow) menu.classList.add('show');
      }
      return;
    }

    var collapseToggle = event.target.closest('[data-toggle="collapse"]');
    if (collapseToggle) {
      event.preventDefault();
      var targetSelector = collapseToggle.getAttribute('data-target') || collapseToggle.getAttribute('href');
      var target = targetSelector ? document.querySelector(targetSelector) : null;
      if (target) target.classList.toggle('show');
      return;
    }

    var dismissModal = event.target.closest('[data-dismiss="modal"], [data-modal-hide]');
    if (dismissModal) {
      event.preventDefault();
      var selector = dismissModal.getAttribute('data-modal-hide');
      var modal = selector ? document.querySelector(selector) : dismissModal.closest('.modal');
      hideModal(modal);
      return;
    }

    if (!event.target.closest('.dropdown')) closeAllDropdowns();

    if (event.target.classList.contains('modal')) {
      hideModal(event.target);
    }
  });

  window.appModal = {
    show: function (selector) { showModal(document.querySelector(selector)); },
    hide: function (selector) { hideModal(document.querySelector(selector)); },
  };

  if (window.jQuery) {
    window.jQuery.fn.modal = function (action) {
      return this.each(function () {
        if (action === 'hide') hideModal(this);
        else showModal(this);
      });
    };
  }
})();

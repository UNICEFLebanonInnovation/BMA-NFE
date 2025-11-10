// Ensure SmartWizard doesn't throw when initialized on missing elements.
//
// The main bundle wires up event handlers that reference the SmartWizard
// plugin directly.  If the selector used during initialization matches no
// elements, the plugin would previously bubble an exception from jQuery's
// data layer.  We intercept assignment of `$.fn.smartWizard` so the wrapped
// version is used everywhere, even for references captured during bundle
// execution.
(function ($) {
  // Guard jQuery's data helper so calls with undefined elements simply no-op.
  var originalData = $.data;
  $.data = function (elem) {
    if (!elem) {
      return;
    }
    return originalData.apply(this, arguments);
  };

  function wrap(fn) {
    return function () {
      if (!this || this.length === 0 || !this[0]) {
        return this;
      }
      return fn.apply(this, arguments);
    };
  }

  if ($.fn.smartWizard) {
    $.fn.smartWizard = wrap($.fn.smartWizard);
  } else {
    Object.defineProperty($.fn, 'smartWizard', {
      configurable: true,
      get: function () {
        return this._smartWizard;
      },
      set: function (fn) {
        this._smartWizard = wrap(fn);
      }
    });
  }
})(jQuery);

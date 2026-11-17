(function () {
    "use strict";

    var photoSelector = "img[data-profile-photo]";

    function showFallback(photo) {
        if (!photo || photo.nodeType !== 1 || !photo.matches(photoSelector)) {
            return;
        }
        var container = photo.closest("[data-profile-photo-container]");
        if (!container) {
            return;
        }
        photo.hidden = true;
        photo.classList.add("d-none");
        var fallback = container.querySelector("[data-profile-photo-fallback]");
        if (fallback) {
            fallback.hidden = false;
            fallback.classList.remove("d-none");
        }
    }

    function checkPhoto(photo) {
        // A cached failure can finish before this script or a preview is inserted.
        if (photo.complete && photo.naturalWidth === 0) {
            showFallback(photo);
        }
    }

    function checkPhotos(container) {
        if (container.nodeType === 1 && container.matches(photoSelector)) {
            checkPhoto(container);
        }
        container.querySelectorAll(photoSelector).forEach(checkPhoto);
    }

    // Image errors do not bubble; capture them for AJAX-loaded profile previews.
    document.addEventListener("error", function (event) {
        showFallback(event.target);
    }, true);
    checkPhotos(document);

    new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === 1) {
                    checkPhotos(node);
                }
            });
        });
    }).observe(document.documentElement, {childList: true, subtree: true});
}());

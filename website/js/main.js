
if (!window.$) {
  var $ = require('./jquery.min.js');
}

$(function() {

  var headerVideo = document.querySelector('#header-video');
  var darbotManufacturingVideo1 = document.querySelector('#dartbot-manufacturing-video-1');
  var dartbotPrototypeVideo1 = document.querySelector('#dartbot-prototype-video-1');

  var $about = $('#about-dartbot');
  var $team = $('#dartbot-team');
  var $process = $('#dartbot-process');
  var $manufacturing = $('#dartbot-manufacturing');
  var $cad = $('#dartbot-cad');
  var $prototype = $('#dartbot-prototype');
  var sections = [$about, $team, $process, $manufacturing, $cad, $prototype];

  var lastSeekTime = new Date();
  $('body').mousemove(function(ev) {
    var now = new Date();
    if (now - lastSeekTime < 80) {
      return;
    }
    lastSeekTime = now;

    var x = ev.pageX;
    var percent = x / window.innerWidth;
    seekToPercent(headerVideo, percent);
  });

  var currentActiveMenuButton = null;
  var currentBottomElementID = null;

  var activeSectionBehaviors = {
    'dartbot-manufacturing': function(active) {
      if (active && darbotManufacturingVideo1.paused) {
        darbotManufacturingVideo1.play();
      } else if (!active && !darbotManufacturingVideo1.paused) {
        darbotManufacturingVideo1.pause();
      }
    },

    'dartbot-prototype': function(active) {
      if (active && dartbotPrototypeVideo1.paused) {
        dartbotPrototypeVideo1.play();
      } else if (!active && !dartbotPrototypeVideo1.paused) {
        dartbotPrototypeVideo1.pause();
      }
    }
  };

  updateActiveSection();
  $(document).scroll(updateActiveSection);

  function updateActiveSection() {
    var bottomElement = mostVisibleElement(sections);
    if (!bottomElement) {
      return;
    }

    var bottomElementID = bottomElement.attr('id');

    var bottomElementMenuButton = $('#' + bottomElementID + '-menu-button');
    if (!bottomElementMenuButton) {
      return;
    }

    if (bottomElementID !== currentBottomElementID) {
      if (currentActiveMenuButton) {
        currentActiveMenuButton.removeClass('active-menu-button');
      }

      if (currentBottomElementID && activeSectionBehaviors[currentBottomElementID]) {
        activeSectionBehaviors[currentBottomElementID](false);
      }
    }

    bottomElementMenuButton.addClass('active-menu-button');

    if (activeSectionBehaviors[bottomElementID]) {
      activeSectionBehaviors[bottomElementID](true);
    }

    currentActiveMenuButton = bottomElementMenuButton;
    currentBottomElementID = bottomElementID;
  }

  var processGallery = $('#process-gallery');
  addToGallery(processGallery, 'media/process/', 10, [2, 6]);

  var prototypeGallery = $('#prototype-gallery');
  addToGallery(prototypeGallery, 'media/prototype/', 4, [2]);
});

function seekToPercent(vid, percent) {
  var min = 0;
  var max = vid.duration;
  var seekLocation = (max - min) * percent;

  vid.currentTime = seekLocation;
}

function mostVisibleElement(elements, bottomMost, buffer) {
  if (!buffer) buffer = 100;

  var topBound = $(window).scrollTop() + (bottomMost? -buffer : -buffer);
  var bottomBound = topBound + window.innerHeight;

  var bestElement = null;
  var bestOffset = bottomMost? 0 : 10000000;

  for (var i = 0; i < elements.length; i++) {
    var $element = elements[i];
    var top = $element.offset().top;
    var nextTop = (i === elements.length - 1 ? null : elements[i + 1].offset().top);

    if ( (top >= topBound) || (nextTop && nextTop > bottomBound) ) {
      if ( (bottomMost && top > bestOffset) || (!bottomMost && top < bestOffset) ) {
        bestOffset = top;
        bestElement = $element;
      }
    }
  }

  return bestElement;
}

function addToGallery($gallery, folder, length, dyptichIndices) {
  for (var i = 1; i <= length; i++) {
    var imageName = folder + i + '.jpg';
    var image = $('<div class="gallery-image"><img src="' + imageName + '" /></div>');

    if (dyptichIndices.indexOf(i) !== -1 || dyptichIndices.indexOf(i - 1) !== -1) {
      image.addClass('dyptich');
    }

    $gallery.append(image);
  }
}

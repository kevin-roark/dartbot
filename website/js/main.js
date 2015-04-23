
if (!window.$) {
  var $ = require('./jquery.min.js');
}

$(function() {

  var headerVideo = document.querySelector('#header-video');

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
  highlightActiveMenuButton();
  $(document).scroll(highlightActiveMenuButton);

  function highlightActiveMenuButton() {
    var bottomElement = mostVisibleElement(sections);
    if (!bottomElement) {
      return;
    }

    var bottomElementMenuButton = $('#' + bottomElement.attr('id') + '-menu-button');
    if (!bottomElementMenuButton) {
      return;
    }

    if (currentActiveMenuButton) {
      currentActiveMenuButton.removeClass('active-menu-button');
    }

    bottomElementMenuButton.addClass('active-menu-button');
    currentActiveMenuButton = bottomElementMenuButton;
  }

  var processGallery = $('#process-gallery');
  addToGallery(processGallery, 'media/process/', 9, [2, 6]);
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

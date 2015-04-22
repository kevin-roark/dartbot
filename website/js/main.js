
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
      bottomElement = $about;
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

});

function seekToPercent(vid, percent) {
  var min = 0;
  var max = vid.duration;
  var seekLocation = (max - min) * percent;

  vid.currentTime = seekLocation;
}

function mostVisibleElement(elements, bottom, buffer) {
  if (!buffer) buffer = 400;

  var bottom = $(window).scrollTop() + (bottom? window.innerHeight : 0) + (bottom? -buffer : buffer);

  var bestElement = null;
  var bottomMostVisibleTop = 0;

  for (var i = 0; i < elements.length; i++) {
    var $element = elements[i];
    var top = $element.offset().top;

    if (top > bottomMostVisibleTop && top < bottom) {
      bestElement = $element;
      bottomMostVisibleTop = top;
    }
  }

  return bestElement;
}

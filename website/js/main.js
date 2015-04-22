
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

  var currentActiveMenuButton = null;

  $('body').mousemove(function(ev) {
    var x = ev.pageX;
    var percent = x / window.innerWidth;
    seekToPercent(headerVideo, percent);
  });

  $(document).scroll(function() {
    var bottomElement = bottomMostVisibleElement(sections);
    if (!bottomElement) {
      return;
    }

    var bottomElementMenuButton = $('#' + bottomElement.attr('id') + '-menu-button');
    console.log(bottomElementMenuButton);

    if (currentActiveMenuButton) {
      currentActiveMenuButton.removeClass('active-menu-button');
    }

    if (bottomElementMenuButton) {
      bottomElementMenuButton.addClass('active-menu-button');
      currentActiveMenuButton = bottomElementMenuButton;
    }
  });

});

function seekToPercent(vid, percent) {
  var min = 0;
  var max = vid.duration;
  var seekLocation = (max - min) * percent;

  vid.currentTime = seekLocation;
}

function bottomMostVisibleElement(elements, buffer) {
  if (!buffer) buffer = -200;

  var bottom = $(window).scrollTop() + window.innerHeight + buffer;

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

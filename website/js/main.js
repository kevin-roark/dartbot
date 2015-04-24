
if (!window.$) {
  var $ = require('./jquery.min.js');
}

$(function() {

  var headerVideo = document.querySelector('#header-video');
  var $headerVideo = $(headerVideo);
  var dartbotManufacturingVideo1 = document.querySelector('#dartbot-manufacturing-video-1');
  var dartbotPrototypeVideo1 = document.querySelector('#dartbot-prototype-video-1');
  var aboutDartbotVideo1 = document.querySelector('#about-dartbot-video-1');

  var $about = $('#about-dartbot');
  var $team = $('#dartbot-team');
  var $process = $('#dartbot-process');
  var $manufacturing = $('#dartbot-manufacturing');
  var $cad = $('#dartbot-cad');
  var $prototype = $('#dartbot-prototype');
  var sections = [$about, $team, $process, $manufacturing, $cad, $prototype];

  var processGallery = $('#process-gallery');
  addToGallery(processGallery, 'media/process/', 10, [2, 6]);

  var manufacturingGallery = $('#manufacturing-gallery');
  addToGallery(manufacturingGallery, 'media/manufacturing/', 2, [1]);

  var prototypeGallery = $('#prototype-gallery');
  addToGallery(prototypeGallery, 'media/prototype/', 4, [2]);

  swathSections();

  var lastSeekTime = new Date();
  $('body').mousemove(function(ev) {
    var now = new Date();
    if (now - lastSeekTime < 80 || $headerVideo.offset().top + $headerVideo.height() < $(window).scrollTop()) {
      return;
    }
    lastSeekTime = now;

    var x = ev.pageX;
    var percent = x / window.innerWidth;
    seekToPercent(headerVideo, percent);
  });

  var currentActiveMenuButton = null;
  var currentBottomElementID = null;
  var lastMenuChangeTime = new Date();
  var hasResetBackgroundColor = true;

  var activeSectionBehaviors = {
    'about-dartbot': function(active) {
      activateVideo(active, aboutDartbotVideo1);
    },

    'dartbot-manufacturing': function(active) {
      activateVideo(active, dartbotManufacturingVideo1);
    },

    'dartbot-prototype': function(active) {
      activateVideo(active, dartbotPrototypeVideo1);
    },
  };

  updateActiveSection();
  $(document).scroll(function() {
    updateActiveSection();
  });

  $('#dartbot-menu a').click(function() {
    var elementID = $(this).attr('href').substring(1);
    setColorForSection(elementID);
  });

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

      setColorForSection(bottomElementID);
    }

    bottomElementMenuButton.addClass('active-menu-button');

    if (activeSectionBehaviors[bottomElementID]) {
      activeSectionBehaviors[bottomElementID](true);
    }

    currentActiveMenuButton = bottomElementMenuButton;
    currentBottomElementID = bottomElementID;
  }

  function activateVideo(active, video) {
    if (active && video.paused && video.play) {
      video.play();
    } else if (!active && !video.paused && video.pause) {
      video.pause();
    }
  }

  function setColorForSection(section) {
    $('body').velocity('stop');
    $('body').velocity({backgroundColor: colorForSection(section)}, {duration: 300});
    hasResetBackgroundColor = false;
    lastMenuChangeTime = new Date();
    setTimeout(resetBackgroundColor, 600);
  }

  function resetBackgroundColor() {
    if (!hasResetBackgroundColor && new Date() - lastMenuChangeTime > 550) {
      $('body').velocity({backgroundColor: '#ffffff'}, {duration: 300});
      hasResetBackgroundColor = true;
    }
  }

  function swathSections() {
    for (var i = 0; i < sections.length; i++) {
      swath(sections[i].attr('id'));
    }
  }
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

function colorForSection(index) {
  switch (index) {
    case 0:
    case 'about-dartbot':
      return '#ffffff';
    case 1:
    case 'dartbot-team':
      return '#ffd559';
    case 2:
    case 'dartbot-process':
      return '#53ec80';
    case 3:
    case 'dartbot-manufacturing':
      return '#5375ff';
    case 4:
    case 'dartbot-cad':
      return '#a853ff';
    case 5:
    case 'dartbot-prototype':
      return '#ff7899';
  }
}

function swath(sectionID) {
  var header = $('#' + sectionID + ' .dartbot-section-header');
  header.css('background-color', colorForSection(sectionID));
  header.css('box-shadow', '1px 1px 10px 0px rgba(0, 0, 0, 0.75)');
}

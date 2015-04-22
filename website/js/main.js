$(function() {

  var headerVideo = document.querySelector('#header-video');

  $('body').mousemove(function(ev) {
    var x = ev.pageX;
    var percent = x / window.innerWidth;
    seekToPercent(headerVideo, percent);
  });

  function seekToPercent(vid, percent) {
    var min = 0;
    var max = vid.duration;
    var seekLocation = (max - min) * percent;

    vid.currentTime = seekLocation;
  }

});

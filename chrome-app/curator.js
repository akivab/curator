var curator = curator || {};

curator.HOST = "http://localhost:8080";
curator.SAVE_ICON = curator.HOST + "/img/check.png";
curator.LOVE_ICON = curator.HOST + "/img/favorite_love.png";
curator.CLOSE_ICON = curator.HOST + "/img/close_delete.png";
curator.OVERFLOW_Y = "";

/**
 * Sets up the page specially for turntable.fm and then sets an interval
 * for the updater to look for title and author information in the page
 */
curator.InitialSetup = function() {
  var imageSelector = new curator.ImageSelector();
  imageSelector.init();
  window.onload = function(){
    imageSelector.resetListeners();
  };

  var url = location.href;
  if(url.match(/turntable/i)) {
    curator.song.SetUpForTurntable();
  }
  if(url.match(/hypem|pandora/i)) {
    setInterval(curator.song.UpdateSongInfo, 1000);
  }
};

/**
 *  Sets the style of an element given a map
 */
curator.SetStyle = function(element, styleObj){
  var style = "";  
  for (var i in styleObj) {
    style += i + ":" + styleObj[i] + ";";
  }
  element.setAttribute('style', style);
};

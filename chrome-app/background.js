var curator = curator || {};
curator.CURRENT_INTERVAL = null;
curator.TIME = 200;

curator.Actor = function(){};

/**
 *  Set up functions for pulling to localStorage
 */

curator.Actor.SendMessage = function(id, data, action, returnFunc){
  if(!id){
    chrome.tabs.getSelected(null, 
      function(tab){
        curator.Actor.SendMessage(tab.id, data, action, returnFunc);
      });
  } else {
    chrome.tabs.sendRequest(id, {action: action, url: data}, returnFunc);
  }
};

curator.Actor.GetMusicUrl = function(details){
  var url = details.url;
  if(url.match(/audio.+pandora\.com\//) ||
      url.match(/.*\.mp3/))
    return url;
  //  if(url.match(/turntable\.fm\/getfile/))
  //    return url.replace(/rand=[\d\.]+/, "rand=" + Math.random());
  return null;
};

curator.Actor.GetMusicInfo = function(details){
  var sendMsgFunc = function(){
    curator.Actor.SendMessage(details.tabId, null, "update", function(response){
        localStorage.artist = response.artist;
      localStorage.song = response.song;
    });
  };
    
  if(curator.CURRENT_INTERVAL) clearInterval(curator.CURRENT_INTERVAL);
  curator.CURRENT_INTERVAL = setInterval(function(){ sendMsgFunc(); }, curator.TIME);
};
  
curator.Actor.CaptureScreen = function(){
  chrome.tabs.getSelected(null, function(tab){
    chrome.tabs.captureVisibleTab(null, {}, function(img){
      curator.Actor.SendMessage(tab.id, img, "snapshot", null);
    });
  });
};
  
curator.Actor.SetUpOptions = function(){
  alert("HI MOM!");
};

chrome.extension.onRequest.addListener(
    function(request, sender, sendResponse){        
      if(request.action == 'screenshot_action') {
        curator.Actor.SendMessage(null, localStorage, "prepare", 
          function(){
            curator.Actor.CaptureScreen(null);
          });
      } else if (request.action == 'images_action') {
        alert("IMAGES"); 
      } else if (request.action == 'songs_action') {
        curator.Actor.SendMessage(null, localStorage, "log", null);
      }
      sendResponse({});
    });

chrome.webRequest.onBeforeSendHeaders.addListener(
    function(details) {
      chrome.tabs.getSelected(null, function(tab) {
        var songUrl = curator.Actor.GetMusicUrl(details);
        if(songUrl){
          localStorage.url = songUrl;
          if(localStorage.song !== "undefined"){
            localStorage.oldSong = localStorage.song;
          }
          localStorage.artist = "undefined";
          localStorage.song = "undefined";
          curator.Actor.GetMusicInfo(details);
        }
      });
    },
    {urls: ["<all_urls>"]},
    ["requestHeaders"]
    );

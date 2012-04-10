if (!curator) {
  throw new ReferenceError("curator is not defined");
}

/**
 * Browser, listening for actions from extension (i.e. button presses). 
 */
chrome.extension.onRequest.addListener(
    function(request, sender, sendResponse) {
      /*
         OK so we have a song URL.
         Capture the song title and band name.
         Send them to last.fm to get album cover (not always available to us otherwise)
         Put picture of the album and title, name in top right corner
         Show it, then fade away.
         When the hand comes back, set visibility to visible, opacity to 1.
         */

      if (request.action === 'log'){
        console.log('my local storage:');
        console.log(localStorage);
        console.log('your local storage:');
        console.log(request.url);
      } else if(request.action === 'prepare'){
        console.log("got a prepare request!");
        curator.OVERFLOW_Y = document.body.style['overflow-y'];
        document.body.style['overflow-y'] = 'hidden';
        sendResponse({}); // snub them
      } else if(request.action === 'update'){
        console.log('sending response');
        sendResponse({artist: localStorage.artist, song: localStorage.song});
      } else if(request.action == 'snapshot'){
        var quiet = document.body;
        var screenObj = new curator.ScreenshotObject();
        screenObj.init(request.url);
        var crop = new curator.Crop(screenObj.img);
        crop.init();
        quiet.appendChild(screenObj.img);
      } else {
        sendResponse({}); // snub them.
      }
    }
);

curator.InitialSetup();

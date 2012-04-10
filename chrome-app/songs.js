var curator = curator || {};

curator.song = curator.song || {};

curator.song.SetUpForTurntable = function() {
  var quiet = document.getElementsByTagName('body')[0];
  var artistInfo = document.createElement('div');
  var songInfo = document.createElement('div');
  var CollectTurntableData = function(){
    setInterval(
        function() { 
          try {
            var tobj = null;
            for(var i in window) {
              if(i && window[i] && window[i]["marquee_texts"]) {
                tobj = window[i];
              }
            }
            tobj = tobj.marquee_texts;
            var artistObj = document.getElementById("SongObjectForCuratorArtist");
            var songObj = document.getElementById("SongObjectForCuratorSong");
            artistObj && (artistObj.innerHTML = tobj.songboard_artist);
            songObj && (songObj.innerHTML = tobj.songboard_title);
          } catch(x) {
            console.log(x);
          }
        }, 500);
  };
  artistInfo.id = 'SongObjectForCuratorArtist';
  songInfo.id = 'SongObjectForCuratorSong';
  quiet.appendChild(artistInfo);
  quiet.appendChild(songInfo);
  var script = document.createElement('script');
  script.type = 'text/javascript';
  script.innerHTML = '(' + CollectTurntableData + ')()';
  quiet.appendChild(script);
};


/**
 *  A function that looks for title and artist information in the page
 */
curator.song.UpdateSongInfo = function() {
  var artist = 'undefined';
  var song = 'undefined';
  var url = location.href;
  if(url.match(/hypem/i)) {
    var info = document.getElementById('player-nowplaying');
    var links = info.getElementsByTagName('a');
    if (info.getElementsByTagName('span').length == 0) {
      song = links[0].innerHTML;
    } else {
      artist = links[0].innerHTML;
      song = links[1].innerHTML;
    }
  } else if (url.match(/turntable/i)) {
    artist = document.getElementById('SongObjectForCuratorArtist').innerHTML;
    song = document.getElementById('SongObjectForCuratorSong').innerHTML;
  } else if (url.match(/pandora/i)) {
    song = document.getElementsByClassName('songTitle')[0].innerHTML;
    artist = document.getElementsByClassName('artistSummary')[0].innerHTML;
  }

  localStorage.artist =  artist;
  localStorage.song = song;
};

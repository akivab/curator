var curator = curator || {};

/**
 *  ScreenshotObject for capturing screen now
 */
curator.ScreenshotObject = function() {
  this.img = '';
};

/**
 *  Constructor for curator.ScreenshotObject (takes a url  which is the
 *  screenshot)
 */
curator.ScreenshotObject.prototype.init = function(url) {
    var image = document.createElement('img');
    var imgStyle = {
      width: '100%',
      position: 'fixed',
      top: '0px',
      left: '0px',
      'z-index': 9998
    };
    curator.SetStyle(image, imgStyle);
    image.setAttribute('src', url);
    image.setAttribute('id', 'screenshot');
    image.ondragstart = function(event){ return false; };
    this.img = image;
};

/**
 *  Crops a screenshot for us.
 */
curator.Crop = function(img){
  this.img = img;
};

curator.Crop.buttonSize = 30;

curator.Crop.overlayStyle = {
  'background-color':'rgba(256,256,256,0.5)',
  position:'fixed',
  'z-index':9999,
  border:'1px solid black'
};

curator.Crop.buttonStyle = {
  position:'fixed',
  'z-index':10000,
  width: (curator.Crop.buttonSize + 'px'),
  height: (curator.Crop.buttonSize + 'px')
};

/**
 *  Crop constructor
 */
curator.Crop.prototype.init = function(){
  this.overlay = document.createElement('div');
  this.closeButton = document.createElement('img');
  this.sendButton = document.createElement('img');
  this.origin = {x:0,y:0};
  this.current = {x:0,y:0};
  
  curator.SetStyle(this.overlay, curator.Crop.overlayStyle);
  curator.SetStyle(this.closeButton, curator.Crop.buttonStyle);
  curator.SetStyle(this.sendButton, curator.Crop.buttonStyle);
  
  this.closeButton.src = curator.CLOSE_ICON;
  this.sendButton.src = curator.SAVE_ICON;
  this.closeButton.onclick = this.close();
  this.sendButton.onclick = this.send();
  this.overlay.onmousemove = this.onmousemove();
  this.overlay.onmousedown = this.onmousedown();
  this.overlay.onmouseup = this.onmouseup();
  this.img.onmousemove = this.onmousemove();
  this.img.onmousedown = this.onmousedown();
  this.img.onmouseup = this.onmouseup();
  this.clicked = false;
};

/**
 *  Destroy method. Removes the crop box.
 */
curator.Crop.prototype.destroy = function(){
  document.body.removeChild(this.overlay);
  document.body.removeChild(this.sendButton);
  document.body.removeChild(this.closeButton);
  document.body.removeChild(this.img);
  document.body.style['overflow-y'] = curator.OVERFLOW_Y;
  delete this;
};

/**
 *  Closes a crop (a button action)
 */
curator.Crop.prototype.close = function(){
  var crop = this;
  return function(event){
    crop.destroy();
  };
};

/**
 *  Sends a cropped region of an image to the server
 */
curator.Crop.prototype.send = function(){
  var crop = this;
  return function(event){
    var cvs = document.createElement('canvas');
    var box = crop.boxDimensions();
    var orig = {};
    var scale = crop.img.naturalWidth / window.innerWidth;
    cvs.width = box.width;
    cvs.height = box.height;
    document.body.appendChild(cvs);

    var ctx = cvs.getContext('2d');
    console.log(box);
    for(var i in box) orig[i] = box[i] * scale;
    ctx.drawImage(crop.img, orig.left, orig.top, orig.width, orig.height, 0, 0, box.width, box.height);
    setTimeout(function(){
      var data = cvs.toDataURL();
      var img = document.createElement('img');
      img.src = data;
      document.body.removeChild(cvs);
      document.body.appendChild(img);
      crop.destroy();
    }, 0);
  };
};

/**
 *  Returns a mousedown function for screenshot
 */
curator.Crop.prototype.onmousedown = function(){
  var crop = this;
  return function(event){
    crop.sendButton.style.visibility = 'hidden';
    crop.closeButton.style.visibility = 'hidden';
    if(crop.origin != undefined){
      document.body.appendChild(crop.overlay);
      document.body.appendChild(crop.sendButton);
      document.body.appendChild(crop.closeButton);
      var pos = curator.Crop.mousePosition(event);
      crop.origin.x = pos.x;
      crop.origin.y = pos.y;
    }
    console.log(crop);
    crop.clicked = true;
  };
};

curator.Crop.mousePosition = function(event){
  var x = event.clientX;
  var y = event.clientY;
  return {x:x, y:y};
};

/**
 *  Returns a mouseup function for screenshot
 */
curator.Crop.prototype.onmouseup = function(){
  var crop = this;
  return function(event){
    crop.clicked = false;
    var pos = curator.Crop.mousePosition(event);
    // we position the send and close buttons below
    crop.sendButton.style.visibility = 'visible';
    crop.closeButton.style.visibility = 'visible';
    crop.closeButton.style.top = pos.y + 'px';
    crop.closeButton.style.left = pos.x + 'px';
    crop.sendButton.style.top = pos.y + 'px';
    crop.sendButton.style.left = (pos.x - curator.Crop.buttonSize) + 'px';;
  };
};

curator.Crop.prototype.boxDimensions = function(){
  var crop = this;
  var top = Math.min(crop.current.y, crop.origin.y);
  var left = Math.min(crop.current.x, crop.origin.x);
  var width = Math.abs(crop.current.x - crop.origin.x);
  var height = Math.abs(crop.current.y - crop.origin.y);
  return {
    top: top,
    left: left,
    width: width,
    height: height
  };
};

curator.Crop.prototype.onmousemove = function(){
  var crop = this;
  return function(event){
    if(!crop.clicked || crop.current == undefined || crop.origin == undefined){
      return;
    }
    var pos = curator.Crop.mousePosition(event);
    crop.current.x = pos.x;
    crop.current.y = pos.y;
    var box = crop.boxDimensions();
    crop.overlay.style.top = box.top + 'px';
    crop.overlay.style.left = box.left + 'px';
    crop.overlay.style.width = box.width + 'px';
    crop.overlay.style.height = box.height + 'px';
  };
};

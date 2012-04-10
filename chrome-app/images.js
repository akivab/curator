var curator = curator || {};

curator.ImageSelector = function(){ 
  this.currentImage = null;
  this.id = 'CuratorSelectorId';
};

curator.ImageSelector.prototype.init = function(){
  var imageSelector = this;
  this.selectorIcon = document.createElement('img');
  this.selectorIcon.style.position = 'absolute';
  this.selectorIcon.style.visibility = 'hidden';
  this.selectorIcon.style.cursor = 'pointer';
  this.selectorIcon.src = curator.LOVE_ICON;
  this.selectorIcon.setAttribute('id', this.id);
  this.selectorIcon.onclick = this.clickIcon();
  this.selectorIcon.onmouseout = function(){ imageSelector.hideIcon(); };
  this.selectorIcon.onmouseover = function(){ imageSelector.hoverIcon(); };
  this.resetListeners();
  document.body.appendChild(this.selectorIcon);
};

curator.ImageSelector.prototype.resetListeners = function(){
  var images = document.getElementsByTagName('img');
  for(var i in images){
    var image = images[i];
    if(image.id == this.id) continue;
    image.onmouseover = this.onmouseover();
    image.onmouseout = this.onmouseout();
  }
};

//TODO: Flesh this out to send image to server if clicked.
curator.ImageSelector.prototype.clickIcon = function(){
  var imageSelector = this;
  return function(event){
    console.log(imageSelector.currentImage);
  };
};

curator.ImageSelector.prototype.onmouseout = function(){
  var imageSelector = this;
  return function(event){
    console.log(imageSelector);
    imageSelector.selectorIcon.style.opacity = 0;
  };
};

curator.ImageSelector.prototype.hoverIcon = function(){
  this.selectorIcon.style.opacity = 1;
};

curator.ImageSelector.prototype.hideIcon = function(){
  this.selectorIcon.style.opacity = 0;
};

curator.ImageSelector.getOffset = function(element){
  var curleft = curtop = 0;
  var obj = element;
  do{
    curleft += obj.offsetLeft;
    curtop += obj.offsetTop;
  } while (obj = obj.offsetParent);
  return {
    curleft: curleft,
    curtop: curtop
  };
};

curator.ImageSelector.prototype.onmouseover = function(){
  var imageSelector = this;
  return function(){
    var upper = 50;
    var lower = 20;
    var size = (Math.min(this.width, this.height) / 4);
    if(size < 20) return;
    size = Math.max(Math.min(size, upper), lower);
    var offset = curator.ImageSelector.getOffset(this);
    var curleft = offset.curleft;
    var curtop = offset.curtop;
    curtop += this.height - size;
    imageSelector.currentImage = this;
    imageSelector.selectorIcon.style['-webkit-transition-duration'] = '0s';
    imageSelector.selectorIcon.style.width = size + 'px';
    imageSelector.selectorIcon.style.height = size + 'px';
    imageSelector.selectorIcon.style.visibility = 'visible';
    imageSelector.selectorIcon.style.left = curleft + 'px';
    imageSelector.selectorIcon.style.top = curtop + 'px';
    window.setTimeout(
        function(){
          imageSelector.selectorIcon.style['-webkit-transition-duration'] = '1s';
          imageSelector.selectorIcon.style.opacity = 1;
        }, 0);
  };
};

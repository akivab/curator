var curator = curator || {};

curator.HOST = "http://localhost:8080";
curator.IS_SIGNED_IN = false;
curator.Popup = function(){
  this.form_ = '';
};

curator.GetBackgroundPage = function() {
  var request = new XMLHttpRequest();
  request.open('GET', curator.HOST + "/test", false); 
  request.send("get_background_page");

  if (request.status === 200) {
    var obj = JSON.parse(request.responseText);
    if(obj['is_signed_in']){
      curator.IS_SIGNED_IN = true;
      var name_ = obj['name'];
      var url_ = obj['logout_url'];
      return "Hey, "+name_+". <a target='_blank' href='"+curator.HOST+url_+"'>Log out?</a>";
    }
    else {
      var url_ = obj['login_url'];
      var image_ = obj['image'];
      return "<a target='_blank' href='"+curator.HOST + url_+"'><img src='http://"+image_+"' /></a>";      
    }
  } else {
    return "Server's down. Sorry, broski.";
  }
};

curator.Popup.prototype.setupForm = function(){
  this.form_ = document.createElement("form");
  document.body.appendChild(this.form_);
  var options = {'screenshot':true, 'songs':true, 'images':true};
  if (!!localStorage['checkbox_options'] &&
    localStorage['checkbox_options'] != '') {
      options = JSON.parse(localStorage['checkbox_options']);
  } else {
    localStorage['checkbox_options'] = JSON.stringify(options);
  }
  for(var option in options){
    var label = document.createElement('label');
    var input = document.createElement("input");
    input.id = option;
    input.type = "checkbox";
    if(!!options[option])
      input.setAttribute('checked', 'checked');
    label['for'] = option;
    label.appendChild(input);
    input.onchange = function(){
      options[this.id] = !options[this.id];
      localStorage['checkbox_options'] = JSON.stringify(options);
    };
    label.insertAdjacentHTML('beforeend', option + "<br/>");
    this.form_.appendChild(label);
  }
}

curator.Popup.prototype.init = function(){
  document.body.innerHTML = curator.GetBackgroundPage();
  if(curator.IS_SIGNED_IN){
    this.setupForm();
  }
}

window.onload = function(){
  var popup = new curator.Popup();
  popup.init();
};

function get_item_rect(id, name, day, time) {
  var div = document.createElement("div");
  var size_h = (1) / 20.0;
  var size_v = 3.0 / 12.0;
  var right = (parseFloat(day) - 13.0) / 20.0;
  var top = (parseFloat(time) - 6.0) / 12.0;
  div.setAttribute("style", "width: " + size_h*100.0 + "%; height: " + size_v*100.0 + "%; right: " + right*100.0 + "%; top: " + top*30.0 + "em;");

    div.setAttribute("id", id);
    div.setAttribute("class", "unit-item item-normal "+id);

  
  var p1 = document.createElement("p");
  p1.setAttribute("class", "item-text item-name");
  var t1 = document.createTextNode(name);
  p1.appendChild(t1);
  
  div.appendChild(p1);
  
  //div.setAttribute("title",id+"\n\n"+name+"\n"+"\n"+instructor);
  //div.setAttribute("data-placement","bottom");
  
  return div;
}

function disp_exam(id, name, day, time) {
  var div1 = get_item_rect(id, name, day, time);
  
  document.getElementById("schedule-table").appendChild(div1);
}



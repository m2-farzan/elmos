function hide_connecting_icon() {
  $("#connecting").addClass("invisible");
}

function show_connecting_icon() {
  $("#connecting").removeClass("invisible");
}

function upstream_add_remove(id, is_remove)
{
  var path = "/schedule/pick/" + id;
  if (is_remove)
    path = "/schedule/remove/" + id;
  
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
     //document.getElementById("demo").innerHTML = this.responseText;
     if (this.responseText == "done")
      hide_connecting_icon();
    }
  };
  xhttp.open("GET", path, true);
  xhttp.send();
  show_connecting_icon();
}

function get_item_rect(id, name, instructor, weekday_1, start_time_1, end_time_1, registered, capacity, temp) {
    var div = document.createElement("div");
  var size_h = (end_time_1 - start_time_1) / 15.0;
  var size_v = 1.0 / 7.0;
  var right = (start_time_1 - 6.0) / 15.0 * 1.005;
  var top = (parseFloat(weekday_1) + 1.01) / 7.0;
  div.setAttribute("style", "width: " + size_h*100.0 + "%; height: " + size_v*100.0 + "%; right: " + right*100.0 + "%; top: " + top*30.0 + "em;");
  
  if (temp)
  {
    div.setAttribute("id", id + "-temp");
    div.setAttribute("class", "unit-item item-temp "+id+"-temp");
  }
  else
  {
    div.setAttribute("id", id);
    div.setAttribute("class", "unit-item item-normal "+id);
  }
  
  var p1 = document.createElement("p");
  p1.setAttribute("class", "item-text item-name");
  var t1 = document.createTextNode(name);
  p1.appendChild(t1);
  
  var p2 = document.createElement("p");
  p2.setAttribute("class", "item-text item-instructor");
  var t2 = document.createTextNode(instructor);
  p2.appendChild(t2);
  
  div.appendChild(p1);
  div.appendChild(p2);
  
  div.setAttribute("title",id+"\n\n"+name+"\n"+"\n"+instructor+"\n\n"+registered+"/"+capacity);
  div.setAttribute("data-placement","bottom");
  
  return div;
}

function disp_item(id, name, instructor, weekday_1, start_time_1, end_time_1, weekday_2, start_time_2, end_time_2, weekday_3, start_time_3, end_time_3, registered, capacity, temp) {
  var div1 = get_item_rect(id, name, instructor, weekday_1, start_time_1, end_time_1, registered, capacity, temp);
  var div2 = get_item_rect(id, name, instructor, weekday_2, start_time_2, end_time_2, registered, capacity, temp);
  var div3 = get_item_rect(id, name, instructor, weekday_3, start_time_3, end_time_3, registered, capacity, temp);
  
  document.getElementById("schedule-table").appendChild(div1);
  document.getElementById("schedule-table").appendChild(div2);
  document.getElementById("schedule-table").appendChild(div3);
  
  //$('.unit-item').tooltip({container:'body'});
  if(!temp) {
    
    var click_remove = function()
      {
        rem_item(id, false);
        $('.unit_select').selectpicker('deselectAll');
        arr = []
        $(".unit-item").each(function(index) { arr.push( $(this).attr("id")); });
        $('.unit_select').selectpicker('val', arr );
        $('.unit_select').selectpicker('refresh');
      }
    
    $(div1).click(click_remove);
    $(div2).click(click_remove);
    $(div3).click(click_remove);
  }
}

function disp_p(p, temp)
{
  var id = p.attr("data-id");
  var name = p.attr("data-name");
  var instructor = p.attr("data-instructor");
  var start_time_1 = p.attr("data-time-start-1");
  var end_time_1 = p.attr("data-time-end-1");
  var weekday_1 = p.attr("data-weekday-1");
  var start_time_2 = p.attr("data-time-start-2");
  var end_time_2 = p.attr("data-time-end-2");
  var weekday_2 = p.attr("data-weekday-2");
  var start_time_3 = p.attr("data-time-start-3");
  var end_time_3 = p.attr("data-time-end-3");
  var weekday_3 = p.attr("data-weekday-3");
  var registered = p.attr("data-registered");
  var capacity = p.attr("data-capacity");

  disp_item(id, name, instructor, weekday_1, start_time_1, end_time_1, weekday_2, start_time_2, end_time_2, weekday_3, start_time_3, end_time_3, registered, capacity, temp);
  
  if (!temp)
    upstream_add_remove(id, false);
}

function rem_item(id, temp) {
  if (temp)
    $("." + id + "-temp").remove();
  else
    $("." + id ).remove();
  
  if(!temp)
    upstream_add_remove(id, true);
}


var myDefaultWhiteList = $.fn.selectpicker.Constructor.DEFAULTS.whiteList;
myDefaultWhiteList.p = ['data-id', 'data-name', 'data-instructor', 'data-time-start-1', 'data-time-end-1', 'data-weekday-1', 'data-time-start-2', 'data-time-end-2', 'data-weekday-2', 'data-time-start-3', 'data-time-end-3', 'data-weekday-3', 'data-registered', 'data-capacity'];

$(".unit_select").on('shown.bs.select', function() {

$("li").filter(":not(.once)").hover(function(){
  $(this).addClass("once");
  
  var p = $(this).find("p");
  disp_p(p, true);

  
  }, function(){
    var p = $(this).find("p");
    var id = p.attr("data-id");
    rem_item(id, true);
});

$('input').on('input',function(e){
    $('.item-temp').remove();
});

});

$('.unit_select').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
  var unit_id = this.options[clickedIndex].text;
  if ( $("#"+unit_id).length > 0 )
  {
    rem_item(unit_id, false);
    return;
  }
  //if (!previousValue)
  //{
    //rem_item(unit_id, false);
    //return;
  //}
  var p = $("#" + unit_id + "_data");
  disp_p(p, false);
});

$( document ).ready(function() {
  //$('.unit-item').tooltip({container:'body'});
});



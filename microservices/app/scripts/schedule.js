window.mobileCheck = function() {
  let check = false;
  (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
  return check;
};

var is_mobile = window.mobileCheck();


var myDefaultWhiteList = $.fn.selectpicker.Constructor.DEFAULTS.whiteList;
myDefaultWhiteList.p = ['data-unit'];

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

function get_item_geometry(start_time, end_time, weekday) {
  if (!is_mobile) {
    var size_h = (end_time - start_time) / 15.0;
    var size_v = 1.0 / 7.0;
    var right = (start_time - 6.0) / 15.0 * 1.005;
    var top = (parseFloat(weekday) + 1.01) / 7.0;
  } else {
    var size_h = (end_time - start_time) / 15.0 * 0.97;
    var size_v = 1.0 / 7.0;
    var right = (start_time - 6.0) / 15.0 * 1.005 * 0.96 + 0.04;
    var top = (parseFloat(weekday) + 1.01) / 7.0 * 0.5;
  }
  return [size_h, size_v, right, top]
}

function get_item_rects(unit, temp) {
  r = [];
  schedule_data = JSON.parse(unit.schedule)
  for (i=0; i<schedule_data.length; i++) {
    r.push( get_item_rect(unit, i, temp) );
  }
  return r;
}

function get_item_rect(unit, no, temp) {
  current_schedule_data = JSON.parse(unit.schedule)[no];
  var div = document.createElement("div");
  var geo = get_item_geometry(current_schedule_data[1], current_schedule_data[2], current_schedule_data[0]);
  var size_h = geo[0];
  var size_v = geo[1];
  var right = geo[2];
  var top = geo[3];
  div.setAttribute("style", "width: " + size_h*100.0 + "%; height: " + size_v*100.0 + "%; right: " + right*100.0 + "%; top: " + top*30.0 + "em;");
  
  if (temp)
  {
    div.setAttribute("id", unit.id + "-temp");
    div.setAttribute("class", "unit-item item-temp " + unit.id + "-temp");
  }
  else
  {
    div.setAttribute("id", unit.id);
    div.setAttribute("class", "unit-item item-normal " + unit.id);
  }
  
  var p1 = document.createElement("p");
  p1.setAttribute("class", "item-text item-name");
  var t1 = document.createTextNode(unit.name);
  if (unit.name.length >= 20)
  {
    p1.setAttribute("style", "font-size: x-small");
  }
  p1.appendChild(t1);
  
  var p2 = document.createElement("p");
  p2.setAttribute("class", "item-text item-instructor");
  var t2 = document.createTextNode(unit.instructor);
  if (unit.name.length > 12 && unit.instructor.length > 16)
  {
    p2.setAttribute("style", "font-size: xx-small");
  }
  p2.appendChild(t2);
  
  div.appendChild(p1);
  div.appendChild(p2);
  
  if (!temp) {
    div.setAttribute("title",
      "<p>" + unit.id + "</p>" + 
      "<p><b>" + unit.name + "</b></p>" + 
      "<p>" + unit.instructor + "</p>" + 
      "<p>" + unit.registered_count+"/"+unit.capacity + "</p>"
    );
    $(div).tooltip({
      container: div,
      delay: { "show": 500, "hide": 0 },
      placement: 'bottom',
      offset: '80, 5',
      animation: false,
      html: true,
    });
  }
  
  return div;
}

function disp_item(unit, temp) {
  var divs = get_item_rects(unit, temp);
  
  for (i=0; i<divs.length; i++) {
    document.getElementById("schedule-table").appendChild(divs[i]);
  }
  
  //$('.unit-item').tooltip({container:'body'});
  if(!temp) {
    
    var click_remove = function()
      {
        rem_item(unit.id, false);
        $('.unit_select').selectpicker('deselectAll');
        arr = []
        $(".unit-item").each(function(index) { arr.push( $(this).attr("id")); });
        $('.unit_select').selectpicker('val', arr );
        $('.unit_select').selectpicker('refresh');
      }

    for (i=0; i<divs.length; i++) {
      $(divs[i]).click(click_remove);
    }
  }
}

function disp_p(p, temp)
{
  var unit = JSON.parse(unescape(p.attr("data-unit")));

  disp_item(unit, temp);
  
  if (!temp)
    upstream_add_remove(unit.id, false);
}

function rem_item(id, temp) {
  if (temp)
    $("." + id + "-temp").remove();
  else
    $("." + id ).remove();
  
  if(!temp)
    upstream_add_remove(id, true);
}

function setup_hover_events() {
  if (is_mobile)
    return;

  $("li").filter(":not(.once)").hover(function(){
    $(this).addClass("once");

    var p = $(this).find("p");
    disp_p(p, true);


    }, function(){
      var p = $(this).find("p");
      var id = p.attr("id").substr(0, 9); // they are like 191110902_data so I strip the trailing chars.
      rem_item(id, true);
  });

  $('input').on('input',function(e){
      $('.item-temp').remove();
  });
}

$(".unit_select").on('shown.bs.select', setup_hover_events);

$('.unit_select').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
  if (!this.options[clickedIndex]) {
    return; // this happens when the page loads
  }
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

$('#lazy_list').on('show.bs.select', function() {
  if (lazy_list_initialized)
    return;

  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      $('#lazy_list').html(this.responseText);
      $('#lazy_list').selectpicker('refresh');
      setup_hover_events();
      lazy_list_initialized = true;
    }
  };
  xhttp.open("GET", "/lazy-list", true);
  xhttp.send();
});
lazy_list_initialized = false;

$("body").on('DOMSubtreeModified', "#lazy_list_div", function() {
    setup_hover_events();
});

$('.unit_select').on('hidden.bs.select', function () {
  $('.item-temp').remove();
});

// Tuning for mobile
if (is_mobile) {
  $('.unit_select').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
    $(document.activeElement).blur();
  });

  $('.unit_select').on('show.bs.select', function () {
    $(document.activeElement).blur();
  });

  $('.unit_select').attr('data-size', 10);
  $('.left-panel').css('opacity', 0.85);
  $('html').css('font-size', 'xx-large');
  $('main').css('padding', 0);
  $('.schedule-table').css({
    width: '100%',
    height: '15em',
  });
}

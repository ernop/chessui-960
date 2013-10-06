sort_by_field = function(obj,field){
    var sortable = [];
    $.each(obj,function(index,guy){
            sortable.push([guy,guy[field]])
    })
    sortable.sort(function(a, b) {
        if (a[1] >b[1]){return -1}
        if (a[1] <b[1]){return 1}
        if (a[1] ==b[1]){return 0}
})
    var res=[]
    $.each(sortable, function(index,guy){
            res.push(guy[0])
    })
    return res
}

function reset_blundermove_info(target){
  target.find('tr').remove();
}

function clear_current_move_info(){
    current_move_information={}
    clear_static_hovers();
    clear_board_highlights()
    }

function clear_board_highlights(){
    $('div').removeClass("drag-value-highlighted");
    $('div').removeClass("static-value-highlighted");
    $('div').removeClass("green")
    $('div').removeClass("lgreen")
    $('div').removeClass("llgreen")
    $('div').removeClass("blue")
    $('div').removeClass("lblue")
    $('div').removeClass("red")
    $('div').removeClass("rred")
    $('div').removeClass("rrred")
    $('div').removeClass("bestmove");
    $('div').removeClass("mating");
    $('div').removeClass("mated");
    $('div').removeClass("played");
}


function sort_by_strength(moves){
    //put mating moves first if positive, last if negative.
    var sortable = [];
    $.each(moves,function(index,guy){
        if (guy['mate']){
            //mateval=Math.abs(guy['mate'])
            mateval=guy['mate']*(Math.pow(-1,movenumber))
        }else{
            mateval=0;
        }
        sortable.push([guy,[mateval,guy['value']]])
    })
    //fucking javascript.  when comparing arrays like [2,3] to [12,2] it fucking converts them to strings first.
    sortable.sort(function(a, b) {
        if (a[1][0]*10000+a[1][1] >b[1][0]*10000+b[1][1]){return -1}
        if (a[1][0]*10000+a[1][1] <b[1][0]*10000+b[1][1]){return 1}
        if (a[1][0]*10000+a[1][1] ==b[1][0]*10000+b[1][1]){return 0}
    })
    var res=[]
    $.each(sortable, function(index,guy){
            res.push(guy[0])
    })
    return res
}

function max(array){
  var val=null;
  $.each(array, function(index,guy){
      if (!val||guy>val){
          val=guy
      }
  })
  return val
}

function min(array){
  var val=null;
  $.each(array, function(index,guy){
      if (val==null||guy<val){
          val=guy
      }
  })
  return val
}

function remove_castling_from_fen(fen){
    var fsp=fen.split(' ')
    fsp[2]='-'
    var nowfen=''
    $.each(fsp, function(index,guy){nowfen+=' '+guy})
    nowfen=nowfen.slice(1)
    return nowfen
}

get_json = function (my_url) {
    //doesnt actually do anything.
    return testjson
    var json = null;
    $.ajax({
        'async': false,
        'global': false,
        'url': my_url,
        'dataType': "json",
        'success': function (data) {
            json = data;
        }
    });
    return json;
};


function clear_static_hovers(){
    $('.movedesc').removeClass('hovered-movedesc');
    $.each($('.static-value-highlighted'), function(index,guy){
    $(guy).unbind('mouseenter mouseleave')
    })
}
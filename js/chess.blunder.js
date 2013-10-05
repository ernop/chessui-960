gamedata=null;
game=null;
movenumber=0
current_move_information={}
mainline_disabled=false;

function load_movenum(num,instant){
    mainline_disabled=false
    var state=gamedata['states'][num];
    if (!gamedata['states'][num]){
        statusEl.html('end of game record '+gamedata['result'])
        return
    }
    if (instant){
        load_slowly=false
    }else{load_slowly=true}
    board.position(gamedata['states'][num].nowfen, load_slowly);
    game.load(remove_castling_from_fen(gamedata['states'][num].nowfen));
    movenumber=num;
    setup_current_move_info(num)
    highlight_static_squares()
    show_move_values()
    reset_pv();
}

function reset_pv(){
pvEl.html('&nbsp;');
}

function setup_current_move_info(num){
    //precalculations etc.
    var state=gamedata['states'][num];
    clear_current_move_info()
    $.each(state['moves'],function(index,guy){
        //how to check if its the realmove?
        var move={'move':guy['move'],'value':guy['value'],'bestmove':guy['bestmove'],'mate':guy['mate'],'nodes':guy['nodes']}
        current_move_information[move['move']]=move;
    })
    eval_current_move_info()
}

function show_move_values(){
    //right side
    var target=$("#blunderinfo");
    reset_blundermove_info(target)
    var moves=sort_by_strength(current_move_information);
    if (movenumber%2==1){
        moves.reverse()
    }
    var best_move_here=null;
    //TODO: top move should have value 0, other moves show by how much worse they are.
    //$.each(moves, function(index,guy){
        //if (best_move_here == null || guy['value']>0){}
    //})
    $.each(moves, function(index,guy){
        draw_move_value(guy, target)  ;
    })
}

function loss2klass(loss){
    if (loss==null ||loss==undefined){
        debugger;
    }
    //a move this bad gets this klass
      if (loss==-9999){klass='mating'}
      else if  (loss==9999){klass='mated'}
      else if (loss==0){klass='bestmove'}
      else if (loss<5){klass='green'}
      else if (loss<10){klass='lgreen'}
      else if (loss<25){klass='llgreen'}
      else if (loss<50){klass='lblue'}
      else if (loss<100){klass='blue'}
      else if (loss<200){klass='red'}
      else if (loss<300){klass='rred'}
      else {klass='rrred'}
      return klass
}

function eval_current_move_info(){
  //look in that object, which lists all the moves available now with their values and stuff, and add klasses to each one showing
  //the value etc.

  //and for each starting square, also tint the square a bit.
    bestval=null;
    $.each(current_move_information, function(index,guy){
        workingval=guy['value']*Math.pow(-1,movenumber);
        if (!bestval || workingval >bestval)
          {bestval = workingval}
    })
    bestval=bestval*Math.pow(-1,movenumber)
    //flip the sign back if black.
    //if (movenumber==5){
        //debugger;
    //}
    //for each move we have analysis for, set their class so when they get highlighted, itll show.
    $.each(current_move_information, function(index,guy){
        //prepare the klasses
      var klass=null;
      if (guy['mate']){
        if (guy['mate']>0){
            loss=-9999;
        }else{
            loss=9999
        }
        klass=loss2klass(loss)
      }
      else if (guy['bestmove']==true){
        klass='bestmove'
        loss=0
      }else{
        var loss=(guy['value']-bestval)*Math.pow(-1, movenumber+1);
        klass=loss2klass(loss)
        }
      guy['klass']=klass
      })
      //we also calculated the startsquare values of submoves - highlight them according to their best one.
}

function highlight_static_squares(){
    startsquares={}
    played_coord=gamedata['states'][movenumber]['thismove'].split("-");
    $.each(current_move_information, function(index,guy){
        startsquare=guy['move'].split('-')[0]
        endsquare=guy['move'].split('-')[1]
        var loss;
        if (guy['bestmove']==true){
            if (guy['mate']){
                if (guy['mate']>0){loss=-9999}  //mateed available
                else{loss=9999//mating}
                }
            }else{
                loss=0}
        }else{
            if (guy['mate']){
                if (guy['mate']>0){
                    loss=-9999
                }else{
                    loss=9999
                }
            }else{
                  loss=(guy['value']-bestval)*Math.pow(-1, movenumber+1);
            }
        }
        if (startsquares[startsquare]){
            startsquares[startsquare].push([loss,startsquare,endsquare])
        }else{
            startsquares[startsquare]=[[loss,startsquare,endsquare]]
        }
    })
    $.each(startsquares,function(coord,lossstartend){
          var destsquare = $('div[data-square='+coord+']');
          //debugger;
          var this_startsquare_losses=[]
          $.each(lossstartend,function(index,thisloss){this_startsquare_losses.push(thisloss[0])});
          var minloss=min(this_startsquare_losses)
          klass=loss2klass(minloss)
          destsquare.addClass('static-value-highlighted');
          destsquare.addClass(klass);
    })
    set_static_hoversquares();
    $('div[data-square='+played_coord[0]+']').addClass('played');
}

function static_hoverin(e){
            clearhover();
            var square=$(e.target).closest('div').attr('data-square')
            am_hovering_square(square);
        }
        function static_hoverout(){
            clearhover()
        }

function set_static_hoversquares(){
    clear_static_hovers()
    $.each($('.static-value-highlighted'), function(index,guy){
        //set a hover action
        $(guy).hover(static_hoverin, static_hoverout)
    })
}

function clearhover(){
    $('.movedesc').removeClass('hovered-movedesc');

}

function am_hovering_square(square){
    //highlight all movechoice rows which start with this.
    clearhover();
    var rows=$('tr.blunder-row[start-square='+square+']')
    $.each(rows, function(index,guy){$(guy).find('.movedesc').addClass('hovered-movedesc')})

    statusEl.html('hovering on'+square)
}

function highlight_moves_on_drag(source, piece, position, orientation, fen){
    clear_board_highlights();
    $.each(current_move_information, function(index, guy){
      if (index.indexOf(source)!=-1){
        var destcoord = index.split('-')[1];
        var destsquare = $('div[data-square='+destcoord+']');
        destsquare.addClass('drag-value-highlighted');
        destsquare.addClass(guy['klass']);
        played_coord=gamedata['states'][movenumber]['thismove'].split("-");
        if (played_coord.indexOf(index.split('-')[0])!=-1){
            //hightlight the played dest square.
            $('div[data-square='+played_coord[1]+']').addClass('played')
        }
      }
    })
  }

function draw_move_value(guy, target){
    var played;
    if (gamedata['states'][movenumber]['thismove']==guy['move']){
        played='played';
    }else{
        played='';
    }
    var calcval=''
    if (guy['mate']){
        var mateval=parseInt(guy['mate'])
        if (mateval<0){
            calcval='mated in '+Math.abs(mateval);
        }else{
            calcval='mate in '+Math.abs(mateval);
        }
    }else{
        calcval=guy['value'];
    }
    //should set up start / end square descriptors here for ease.
    var start=guy['move'].split("-")[0]
    var end=guy['move'].split("-")[1]
  var res='<tr class="blunder-row" start-square='+start+' end-square='+end+'><td class="movedesc '+played+'">'+played+'<td class="movechoice '+guy['klass']+'" move='+guy['move']+'>'+guy['move']+'<td class="movevalue">'+calcval;
  target.append(res);
}

function setup_buttons(){
    $('#navigate-back').click(function(){
        if (movenumber>0){
            load_movenum(movenumber-1);
        }
    });
    $('#navigate-forward').click(function(){
        load_movenum(movenumber+1);
    });
}

function load_pv(pv){
    pvEl.html('<div class="pvzone"></div>')
    global_pv=pv;
    hovering=false;
    var_start_fen=game.fen();
    nowindex=0;
    //debugger;
    var pv_start_square=pv[0].split('-')[0];
    var pv_end_square=pv[0].split('-')[1];
    //debugger;
    //$('.blunder-row[start-square='+pv_start_square+'][end-square='+pv_end_square+']')
    $('.blunder-row[start-square='+pv_start_square+'][end-square='+pv_end_square+']').find('.movedesc').addClass('examining-var').html("variation");
    pvEl.append($('<div class="medium">Variation:</div>'))
    $.each(pv, function(index,guy){
        var pvblock=$('<div pv-index='+index+' class="pvmove">'+guy+'</div>');
        pvEl.append(pvblock);
        pvblock.hover(function(thing){
                //debugger;
                if (hovering){return}
                hovering=true;

                var guy=$(thing.target).closest('.pvmove');
                //advance the game to this point.
                var pvindex=parseInt(guy.attr('pv-index'));
                if (nowindex==pvindex){hovering=false;return}
                //debugger;
                //game.load(var_start_fen)
                //board.position(game.fen(),0)
                //moev to the nth var of the pv
                //debugger;
                if (nowindex<pvindex){
                    for (ii=nowindex+1;ii<=pvindex;ii++){
                        var thismove=pv[ii];
                        var source=thismove.split('-')[0];
                        var target=thismove.split('-')[1];
                        var move = game.move({
                            from: source,
                            to: target
                            //promotion: 'q'
                            //todo fix this
                        });
                        //board.position(game.fen(),0)
                        console.log("going forward: "+source+'-'+target);
                        if (move == null){debugger;}
                    }
                }else if (nowindex>pvindex){
                    for (ii=nowindex;ii>pvindex;ii--){
                        game.undo();
                        console.log("undoing");
                    }
                }
                board.position(game.fen(),0)
                console.log("setting to game fen.",game.fen())
                hovering=false
                nowindex=pvindex;
        })
    })
    pvEl.append($('<div class="medium"  id="navigate-restore">back to main line</div>'))
    $('#navigate-restore').click(function(){
        load_movenum(movenumber);
    });
  //lock the board, load the pv for display.
}

function setup_base_board(){
    game = new Chess()
    statusEl = $('#status')
    pvEl=$('#pv')
    fenEl = $('#fen')
    pgnEl = $('#pgn');
    //functions all in other js.
    var cfg = {
        draggable: true,
        position: 'start',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        onMoveEnd: onMoveEnd
    };
    board = new ChessBoard('board', cfg);
    updateStatus();
}

function start_blunder(){
    codeEl=$('#code')
    setup_base_board();
    gamedata=get_json()
    load_movenum(0);
    setup_buttons();
}
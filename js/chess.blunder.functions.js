function onDragStart(source, piece, position, orientation) {
    codeEl.html('drag start');
    //debugger;
    clear_static_hovers();
    if (!mainline_disabled){
        highlight_moves_on_drag(source, piece, position, orientation, game.fen)
    }
    if (game.game_over() === true ||
        (game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
        clear_board_highlights();
        //highlight_static_squares();
        return false;
    }
};

var onDrop = function(source, target) {
      var move = game.move({
          from: source,
          to: target,
          promotion: 'q'
      });
      if (move === null){
          codeEl.html('illegal move.')
          clear_board_highlights();
          if (!mainline_disabled){
              highlight_static_squares()
          }
          return 'snapback';
      }
      updateStatus();
      clear_board_highlights()
      //debugger;
      //if it was the game move, load the next blundermove
      if (gamedata['states'][movenumber]){
          var state=gamedata['states'][movenumber];
          actualmove=source+'-'+target;
          //maybe have an x in here?
          if (actualmove==state['thislanmove']  && !mainline_disabled ){
              //advance
              load_movenum(movenumber+1,true)
          }else{
            load_variations(state, actualmove);
            }
    }
}

function load_variations(state, actualmove, in_mainline){
    //actually we should show the main variation for game moves, too.
    //otherwise, just lock the board and show the pv

    //actualmove refers to the move on the board.  if the user is playing a variation, it will not be the played move & will be sent along
    // if the main var is shown as a result of navigation/playing the game move, we show the expected continuation anyway
    //and just figure out the actualmove based on the current bestmove.
    //debugger;
    var thisguy=null;
    $.each(state['moves'], function(index,guy){
        if (thisguy){return}
        if (guy['bestmove'] && actualmove==null){
            thisguy=guy;
            //when not given the move, just show the best var
        }
        else if (guy['lanmove']==actualmove){
            thisguy=guy;
        }
    })
    if (thisguy){
        load_pv(thisguy['pv'], in_mainline);
    }
    clear_static_hovers()
    if (in_mainline){}else{mainline_disabled=true;}
    //it'll be unset if this was called from load_movenum.
}

var updateStatus = function() {
      var status = '';
      var moveColor = 'White';
      if (game.turn() === 'b') {
        moveColor = 'Black';
      }
      if (game.in_checkmate() === true) {
        status = 'Game over, ' + moveColor + ' is in checkmate.';
      }
      else if (game.in_draw() === true) {
        status = 'Game over, drawn position';
      }
      else {
        status = moveColor + ' to move';
        if (game.in_check() === true) {
          status += ', ' + moveColor + ' is in check';
        }
      }
      statusEl.html(status);
      fenEl.html(game.fen());
      pgnEl.html(game.pgn());
    };

var onSnapEnd = function() {
};

function onMoveEnd (oldPos, newPos) {

  updateStatus()
}


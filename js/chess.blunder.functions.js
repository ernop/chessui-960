function onDragStart(source, piece, position, orientation) {
    codeEl.html('drag start');
    clear_static_hovers();
    highlight_moves_on_drag(source, piece, position, orientation, game.fen)
    if (game.game_over() === true ||
        (game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
        clear_board_highlights();
        highlight_static_squares();
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
          highlight_static_squares()
          return 'snapback';
      }
      updateStatus();
      clear_board_highlights()
      //debugger;
      //if it was the game move, load the next blundermove
      if (gamedata['states'][movenumber]){
          var state=gamedata['states'][movenumber];
          combomove=source+'-'+target;
          //maybe have an x in here?
          if (combomove==state['thismove']  && !mainline_disabled ){
              //advance
              load_movenum(movenumber+1,true)
          }
          else{
            //debugger;
            //otherwise, just lock the board and show the pv
            if (!mainline_disabled){
            var thisguy=null;
            $.each(state['moves'], function(index,guy){
                if (guy['move']==combomove){
                    thisguy=guy;
                }
            })
            if (thisguy){
                load_pv(thisguy['pv']);
            }
            mainline_disabled=true;
            clear_static_hovers()
            }else{
                //mainline was already disabled
            }
          }
    }
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


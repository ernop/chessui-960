import logging, os, subprocess, time, re, json, atexit
import pgn
from pychess.Utils.lutils import LBoard, lmove
log = logging.getLogger(__name__)
testpgn = 'pgn/hairui_vs_snowroads_2013_08_29.pgn'

DEBUG_ENGINE = False
engine = None
GLOBAL_LAST = 5
GLOBAL_LAST = None

from util import *

def get_board(gamepgn, movenum):
    #make a pyboard at that spot.
    moves_to_here = gamepgn.moves[:movenum]
    board = LBoard.LBoard(variant=3)
    board.applyFen(gamepgn.fen)
    for move in moves_to_here :
        longmove = lmove.parseSAN(board, move)
        board.applyMove(longmove)
    return board

def read_move(infoline, board, gamepgn, movenum):
    board = board.clone()
    #'info multipv 3 depth 4 seldepth 24 score cp 7 time 4995 nodes 4342 nps 0 tbhits 0 hashfull 0 pv c2c4 c7c5 f2f4 f7f5 e1f2',
    res = {}
    if ' pv ' not in infoline:
        return False
    if 'cp ' in infoline:
        value = ((-1) ** movenum) * int(re.compile(r'cp ([\-\d]+)').findall(infoline)[0])
    else:
        value = ''
    if 'mate' in infoline:
        mate = re.compile(r' mate ([\-\d]+)').findall(infoline)[0]
    else:
        mate = ''
    pv = re.compile(r' pv (.*)').findall(infoline)[0]
    ANmove = pv.split(' ')[0]
    LANmove = lmove.toLAN (board, lmove.parseAN(board, ANmove))
    LANmove = ''.join([c for c in LANmove.replace('x', '-') if c.lower()==c])
    res = {'nodes': re.compile(r'nodes ([\d]+)').findall(infoline)[0],
           'value': value,
           'mate': mate,
           'pv': pv,
           'move': LANmove,
           }
    res['pv'] = [adddash(n) for n in res['pv'].split()]
    #print infoline
    return res

def calculate_blunders(pgnpath):
    global engine
    FIRST = 0
    assert os.path.exists(pgnpath)
    pgntext = open(pgnpath, 'r').read()
    gamepgn= pgn.loads(pgntext)[0]
    #test gameresult.
    log.info('got game %s', gamepgn)
    LAST = GLOBAL_LAST or len(gamepgn.moves)
    states = {}
    for n in range(FIRST, LAST):
        try:
            move = gamepgn.moves[n]
            if move in ['1-0', '0-1', '1/2-1/2']:
                break
            states[n] = engine.evalposition(gamepgn, movenum=n)
        except Exception, e:
            import ipdb;ipdb.set_trace()
            try:
                states[n] = engine.evalposition(gamepgn, movenum=n)
            except Exception, ee:
                pass
            break
        try:
            display_results(states, gamepgn, FIRST, LAST)
        except Exception, e:
            import ipdb;ipdb.set_trace()
            try:
                display_results(states, gamepgn, FIRST, LAST)
            except:
                pass
            continue
    #states = add_missing_played_moves(states, gamepgn)
    blunder_result = {'result': gamepgn.result,'states': states, 'version': '1.0', 'pgnpath': pgnpath, 'startfen': gamepgn.fen, 'pgn': pgntext, 'moves': gamepgn.moves,}
    return blunder_result

def add_missing_played_moves(states, gamepgn):
    for movenum, state in states.items():
        found = False
        for move in state['moves']:
            if move['playedmove']:
                found = True
                break
        if found:
            continue
        if movenum + 1 in states:
            nextstate = states[movenum+1]
            nextstate_bestmove = None
            if 'moves' in nextstate:
                for s in nextstate['moves']:
                    if 'bestmove' in s and s['bestmove']:
                        nextstate_bestmove = s
                        break
            if not nextstate_bestmove:
                continue
            if nextstate_bestmove['value'] is not None:
                nextstate_val = nextstate_bestmove['value']
            else:
                nextstate_val = ''  #this is a failure.
                import ipdb;ipdb.set_trace()
            #we should
            nextpv = nextstate_bestmove['pv']
            nextpv.insert(0, state['thismove'])
            playedmove = {'bestmove': False,
                'mate': nextstate_bestmove['mate'] and str(-1*int(nextstate_bestmove['mate'])) or '',
                'move': state['thismove'],
                'playedmove': True,
                'pv': nextpv,  #we fake up the pv of the actually played move by looking ahead in the tree.
                'nodes': 0,
                'value': nextstate_val,
                }
            state['moves'].append(playedmove)
    return states

def do_game(pgnpath):
    assert os.path.isdir("js/pregen")
    assert os.path.exists(pgnpath)
    jsfn = os.path.split(pgnpath)[-1].replace('.pgn', '.js')
    jsfp = 'js/pregen/' + jsfn
    if os.path.exists(jsfp):
        print 'overwriting unless you cancel: %s' % jsfp
    else:
        print 'will create %s' % jsfp
    blunder_result = calculate_blunders(pgnpath)
    open(jsfp, 'w').write('testjson='+json.dumps(blunder_result))
    htmlfp = jsfn.replace('.js', '.html')
    if os.path.exists(htmlfp):
        print 'overwriting %s' % htmlfp
    htmltext = open('replayer_template.html', 'r').read()
    newtext = htmltext.replace('{{pregen_js_name}}', jsfn)
    open(htmlfp, 'w').write(newtext)
    print 'created js: %s, html %s' % (jsfp, htmlfp)

if __name__ == "__main__":
    engine = setup_engine()
    setup_logging()
    do_game(testpgn)
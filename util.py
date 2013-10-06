import atexit, subprocess, logging, pprint

from pychess.Utils.lutils import LBoard, lmove

def setup_killer(engine):
    killer = Killer(engine)
    atexit.register(killer.dell)

class Killer(object):
    def __init__(self, killee):
        self.killee = killee

    def dell(self):
        self.killee.end()

def print_fen(fen):
    fen = fen.split(' ')[0]
    for n in range(9):fen = fen.replace(str(n), '-'*n)
    fensp = fen.split('/')
    #fensp.reverse()
    for p in fensp:print p

def setup_engine():
    from engine import Engine
    engine = Engine()
    engine.setup()
    setup_killer(engine)
    return engine

def adddash(x):
    if 'x' in x:
        return x
    try:
        return x[:2] + '-' + x[2:]
    except Exception, e:
        import ipdb;ipdb.set_trace()
        return ''

def removedash(x):
    return x.replace("-", '')

def start_houdini():
    engine = subprocess.Popen(
        'D:/chessengine/houdini3/Houdini_3.exe',
        universal_newlines=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    return engine

def setup_logging():
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)

def movelist2san(board, pv):
    #import ipdb;ipdb.set_trace()
    res = []
    moved = 0
    stfen = board.asFen()
    for mv in pv:
        nummove = lmove.parseAN(board, mv)
        san = lmove.toSAN(board, nummove)
        res.append(san)
        board.applyMove(nummove)
        moved += 1
    for n in range(moved):
        board.popMove()
    assert board.asFen() == stfen
    return res

def display_results(states, gamepgn, FIRST, LAST, current):
    from precalc import get_board
    for mm in range(FIRST, LAST):
        nn = mm - 1
        if nn < 0:
            continue
        if nn + 1 not in states:
            continue
        board = get_board(gamepgn, nn)
        if nn % 2 == 1:color = 'Black'
        else:color = 'White'

        if mm == current:
            print '\n%s to move' % color, nn
            print '\n\n'
            print '=' * 50
            print_fen(board.asFen())
        if nn not in states:
            continue
        res = states[nn]
        if nn < LAST and nn + 1 in states:
            hasnext = True
            nextres = states[nn+1]
        else:
            hasnext = False
            nextres = None

        #print pprint.pprint(states[nn])

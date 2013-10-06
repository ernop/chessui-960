import logging, os, subprocess, time, re, json, atexit
import pgn
from pychess.Utils.lutils import LBoard, lmove
log = logging.getLogger(__name__)

FIRSTMOVE_THINK_TIME = 15
#for every firstmove think this long.
THINK_TIME = 5
#per move from multipv
FOR_BEST_TIME = 10
#for the single best search on the raw board, to make sure we find it at least!
OVERRIDE_TIME = 5
#the first (bad) possible move will be searched to this depth.
MOVE_GENERATION_MULTIPV = 50

FAST = False
FAST = True

if FAST:
    FIRSTMOVE_THINK_TIME = 1
    #for every firstmove think this long.
    THINK_TIME = 1
    #per move from multipv
    FOR_BEST_TIME = 1
    #for the single best search on the raw board, to make sure we find it at least!
    OVERRIDE_TIME = 1
    #the first (bad) possible move will be searched to this depth.
    MOVE_GENERATION_MULTIPV = 4



setup_cmds = ['xboard',
              'uci',
              'setoption name Hash value 256',
              'setoption name Threads value 2',
              'setoption name UCI_Chess960 value true',
              'isready',
              ]  #'setoption name MultiPV value %d' % MULTIPV]

tb = 'setoption name GaviotaTbPath value e:\dl\Gaviota'

engine = None

from util import *
from precalc import *
time.clock()

class Engine(object):

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.end()

    def __init__(self):
        self.engine = start_houdini()
        self.debug = DEBUG_ENGINE
        if self.debug:
            print 'DEBUGGING ENGINE'
        self.active_pv = None

    def put(self, command):
        if self.debug:print '%0.5f you:\t%s' % (time.clock(), command)
        self.engine.stdin.write(command+'\n')

    def get(self):
        self.engine.stdin.write('isready\n')
        if self.debug:print '%0.5f  engine:' % time.clock()
        alltext = []
        while True:
            text = self.engine.stdout.readline().strip()
            alltext.append(text)
            if self.debug:
                if text !='':
                    print '%0.5f\t%s' % (time.clock(), text)
            if text == 'readyok':
                break

        '''info time 87008 nodes 8047489 nps 92000 tbhits 0 hashfull 1000 cpuload 565 idle 80793M
        info multipv 1 depth 17 seldepth 38 score cp 32 time 106952 nodes 8158605 nps 76000 tbhits 0 hashfull 1000 pv c2c4 c7c5 a1c2 f7f6 b2b3 a8c7 f2f3 d7d5 c4d5 d8d5 e2e4 d5d8 d2d4 c5d4 c2d4 e7e5 d4f5 d8d1 e1d1 c7e6 c1d3 c8d6
        bestmove c2c4 ponder c7c5'''
        return alltext

    def setup(self):
        for cmd in setup_cmds:
            self.put(cmd)
            self.get()

    def get_to_end(self):
        alltext = []
        ct = 0
        res2 = None
        while 1:
            ct += 1
            if ct > 10:
                import ipdb;ipdb.set_trace()
            if res2:
                this = res2
                res2 = None
            else:
                this = self.get()
            if not this:
                break
            if this == ['readyok']:
                continue
            alltext.extend(this)
            if this[-1] == 'readyok':
                res2 = self.get()
                if res2 == ['readyok']:
                    break
                else:
                    continue
            time.sleep(0.1)
        return alltext

    def end(self):
        self.put('quit')

    def set_multipv(self, n):
        cmd = 'setoption name MultiPV value %d'%n
        if self.debug:print '%0.5f me:%s' % (time.clock(), cmd)
        self.put(cmd)
        self.get()

    def get_possible_moves(self, movenum, gamepgn, board, including):
        if not including:
            including = []
        self.put('ucinewgame')
        self.get()
        board = get_board(gamepgn, movenum)
        #the move he's going to play in this position.
        nowfen = board.asFen()
        use_multipv = max(MOVE_GENERATION_MULTIPV-movenum/2, 4)
        print 'using multipv %d' % use_multipv
        self.set_multipv(use_multipv)
        self.put('position fen %s' % (nowfen))
        self.get()
        self.put('go movetime 3000')
        self.get()
        self.put('stop')
        res = self.get_to_end()
        self.set_multipv(0)
        possibles = []
        for line in res:
            move = read_move(line, board, gamepgn, movenum)
            if not move:
                continue
            #print 'using line', line
            #print 'got TEST move',
            #pprint.pprint(move)
            possibles.append(move)
        #check whether we evaluated including in the top moves.

        best = self.eval_for_best(board, gamepgn, movenum)
        possibles.append(best)
        possibles.sort(key=lambda x:x['value']*((-1)**movenum))
        possibles = list(set([pos['lanmove'] for pos in possibles]))
        if including in possibles:  #stick the force move on the end for final evaluation.
            possibles.remove(including)
        possibles.append(including)
        print 'got %d possibles: %s' % (len(possibles), possibles)
        return [removedash(x) for x in possibles]

    def eval_for_best(self, board, gamepgn, movenum, override_time=None):
        return self.eval_one_move(board, gamepgn, movenum, override_time=FOR_BEST_TIME)

    def eval_one_move(self, board, gamepgn, movenum, override_time=None, possible=None):
        use_think_time = override_time or THINK_TIME
        self.put('position fen %s' % (board.asFen()))
        self.get()
        if possible:
            self.put('go movetime %d searchmoves %s'%(use_think_time*1000, possible))
        else:
            self.put('go movetime %d'%(use_think_time*1000))
        self.get()
        time.sleep(use_think_time)
        self.put('stop')
        res = self.get_to_end()
        from precalc import DEBUG_ENGINE
        lines = res[-4:]
        for line in lines:
            move = read_move(line, board, gamepgn, movenum)
            if not move:
                continue
            #if int(move['nodes']) < 10000 and not move['mate']:
                #import ipdb;ipdb.set_trace()
            #import ipdb;ipdb.set_trace()
            if move['value'] != '':
                val = '%04d' % int(move['value'])
            else:
                val = 'mate in %s' % move['mate']
            print 'evalled move in time %s.     %s nodes = %09d %s' % (use_think_time, move['move'], int(move['nodes']), val)

            return move

    def evalposition(self, gamepgn, movenum):
        self.put('ucinewgame')
        self.get()
        board = get_board(gamepgn, movenum)
        LANmove = lmove.toLAN (board, lmove.parseSAN(board, gamepgn.moves[movenum]))
        SANmove = lmove.toSAN (board, lmove.parseSAN(board, gamepgn.moves[movenum]))
        LANmove = ''.join([c for c in LANmove.replace('x', '-') if c.lower()==c])

        possibles = self.get_possible_moves(movenum, gamepgn, board, including=LANmove)
        nowfen = board.asFen()
        moves = []

        for ii, possible in enumerate(possibles):
            override_time = None  #first possible you consider, think longer.
            if ii == 0:
                override_time = OVERRIDE_TIME
            if movenum == 0:
                override_time = FIRSTMOVE_THINK_TIME
            move = self.eval_one_move(board, gamepgn, movenum, override_time=override_time, possible=possible)
            if not move:
                continue
            #need to decide which is the best now.
            if move['lanmove'] == LANmove:
                move['playedmove'] = True
                foundmove = True
            else:
                move['playedmove'] = False
            moves.append(move)
        bestval = None
        bestmove = None
        for move in moves:
            moveval = ((-1) ** (movenum) ) * move['value']
            if not bestval or moveval> bestval:
                bestval = moveval
                bestmove = move
        bestmove['bestmove'] = True
        res = {
               'fen': nowfen,
               'moves': moves,
               'thislanmove': LANmove,
               'thismove': SANmove,
               'nowfen': nowfen,
               }
        return res
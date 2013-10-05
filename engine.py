import logging, os, subprocess, time, re, json, atexit
import pgn
from pychess.Utils.lutils import LBoard, lmove
log = logging.getLogger(__name__)

EARLY_MULTIPV = 5
MULTIPV = 3
setup_cmds = ['setoption name Threads value 3','setoption name Hash value 450', 'setoption name UCI_Chess960 value true', 'isready', 'setoption name MultiPV value %d' % MULTIPV]
              #'setoption name MultiPV value 10'
              #]
tb = 'setoption name GaviotaTbPath value e:\dl\Gaviota'

DEBUG_ENGINE = False
THINK_TIME = 20
engine = None

from util import *
from precalc import *

class Engine(object):
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.end()
    def __init__(self):
        self.engine = start_houdini()
        self.debug = DEBUG_ENGINE
        self.active_pv = None

    def put(self, command):
        if self.debug:print '\nyou:\t'+command,
        self.engine.stdin.write(command+'\n')
    def get(self):
        self.engine.stdin.write('isready\n')
        if self.debug:print '\nengine:',
        alltext = []
        while True:
            text = self.engine.stdout.readline().strip()
            alltext.append(text)
            if text == 'readyok':
                break
            if self.debug:
                if text !='':
                    print('\t'+text)
        '''info time 87008 nodes 8047489 nps 92000 tbhits 0 hashfull 1000 cpuload 565 idle 80793M
        info multipv 1 depth 17 seldepth 38 score cp 32 time 106952 nodes 8158605 nps 76000 tbhits 0 hashfull 1000 pv c2c4 c7c5 a1c2 f7f6 b2b3 a8c7 f2f3 d7d5 c4d5 d8d5 e2e4 d5d8 d2d4 c5d4 c2d4 e7e5 d4f5 d8d1 e1d1 c7e6 c1d3 c8d6
        bestmove c2c4 ponder c7c5'''
        return alltext
    def setup(self):
        for cmd in setup_cmds:
            self.put(cmd)
        print self.get()
    def eval_hypothetical_move():
        pass
    def get_to_end(self):
        alltext = []
        ct = 0
        while 1:
            ct += 1
            this = self.get()
            if not this:
                break

            if this == ['readyok']:
                continue
            alltext.extend(this)
            if this[-1] == 'readyok':
                break
            time.sleep(0.1)
            if ct > 10:
                import ipdb;ipdb.set_trace()
        return alltext
    def end(self):
        self.put('quit')

    def set_multipv(self, n):
        if n >= 1 and n < 99:
            cmd = 'setoption name MultiPV value %d'%n
            print cmd
            self.put(cmd)
            self.get()

    def evalposition(self, gamepgn, movenum):
        self.put('ucinewgame')
        #need to convert the SAN moves to LAN moves.
        board = get_board(gamepgn, movenum)
        #the move he's going to play in this position.
        nowfen = board.asFen()
        use_think_time = THINK_TIME
        if movenum < 10:
            use_think_time *= 3
            self.set_multipv(EARLY_MULTIPV)
            self.active_pv = EARLY_MULTIPV
        else:
            self.set_multipv(MULTIPV)
            self.active_pv = MULTIPV
        print 'pv', self.active_pv, 'time', use_think_time
        self.put('position fen %s' % (nowfen))
        self.put('go infinite')
        #import ipdb;ipdb.set_trace()

        time.sleep(use_think_time)
        self.put('stop')
        res = self.get_to_end()

        lines = res[-1*(2+self.active_pv):-1]
        moves = []
        LANmove = lmove.toLAN (board, lmove.parseSAN(board, gamepgn.moves[movenum]))
        LANmove = ''.join([c for c in LANmove.replace('x', '-') if c.lower()==c])
        foundmove = False
        for ii, pvline in enumerate(lines):
            print pvline
            if ii == 0 and 'multipv 1 ' not in pvline :
                continue
            #get the otherones.
            move = read_move(pvline, board, gamepgn, movenum)
            if not move:
                continue
            move['bestmove'] = ii == 0 or False
            if move['move'] == LANmove:
                move['playedmove'] = True
                foundmove = True
            else:
                move['playedmove'] = False
            moves.append(move)
        if not foundmove:
            #add it in manually later after generating the full game.
            pass
        #infoline = res[-1*(self.active_pv)+-2]
        res = {
               'fen': board.asFen(),
               'moves': moves,
               'thismove': LANmove,
               'nowfen': nowfen,
               }
        return res
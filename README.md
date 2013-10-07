chessui-960
===========

a javascript chess game replayer with integrated display of pregenerated engine analysis

example at:

http://fuseki.net/home/chess960-941.html


Howto
----------------

- install a UCI chess engine

- get the code

- fix the path in the code so that python can call the engine

- mess around with the time settings, engine settings, etc.

EARLY_MULTIPV = 50 (how many variations to force the engine to generate in the first 10 half moves

MULTIPV = 3 (for the rest of the game, how many pvs?)

THINK_TIME = 20 (first 10 half moves it'll think 3x this long)

What you get
---------------------------------

an html file which calls the display thingie and loads the pregenerated analysis so you can navigate around / put it on your webpages etc.

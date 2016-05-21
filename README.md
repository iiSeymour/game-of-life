Game Of Life
============

A python implementation of [Conway's Game of Life](http://en.wikipedia.org/wiki/Conway's_Game_of_Life) using the curses module with a small evolutionary twist.


Installation
============

With pip:

```
$ sudo pip install gol
```

From github:

```shell
$ git clone https://github.com/iiSeymour/game-of-life
$ cd game-of-life
$ sudo python setup.py install
```

Running
=======

```shell
$ gol
```

For terminal screensaver mode.

```shell
$ gol -faxl
```

Options
-------

```
$ gol --help
usage: gol.py [-h] [-a] [-l] [-f] [-n initial_points] [-r refresh_rate] [-t] [-x] [-v]

optional arguments:
  -h, --help         show this help message and exit
  -a, --autostart    skip the splash screen
  -l, --loop         immediately restart game
  -f, --fullscreen   display fullscreen grid
  -n initial_points  set the number of initial points
  -r refresh_rate    set the refresh rate
  -t, --traditional  traditional mode
  -x, --no-hud       don't display HUD
  -v, --version      show program's version number and exit
```

Screenshot
==========

<p align="center">
<img src="https://raw.github.com/iiSeymour/game-of-life/master/conway/gol.png"" alt="Game Of Life"/>
</p>

Game Of Life
============

A python implementation of [Conway's Game of Life](http://en.wikipedia.org/wiki/Conway's_Game_of_Life) using the curses module with a small evolutionary twist.

```shell
$ gol --help
  usage: gol [-h] [-f] [-x] [-t] [-r refresh_rate] [-n initial_points]

    optional arguments:
    -h, --help         show this help message and exit
    -f, --fullscreen   display fullscreen grid
    -x, --no_hud       don't display HUD
    -t, --traditional  traditional mode
    -r refresh_rate    set the refresh rate
    -n initial_points  set the number of initial points
```

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

Screenshot
==========

<p align="center">
<img src="https://raw.github.com/iiSeymour/game-of-life/master/conway/gol.png"" alt="Game Of Life"/>
</p>

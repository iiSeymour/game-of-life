#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Curses implementation of Conway's Game Of Life with an evolutionary twist.

Any live cell with fewer than two live neighbours dies.
Any live cell with two or three live neighbours lives on.
Any live cell with more than three live neighbours dies.
Any dead cell with exactly three live neighbours becomes a live cell.
"""

import os
import sys
import copy
import curses
import random
import argparse
from time import sleep
from itertools import chain, product

__version_info__ = (1, 0, 0)
__version__ = ".".join(map(str, __version_info__))


class gol(object):

    def __init__(self, args):
        self.test = args.test
        self.screen = curses.initscr()
        self.screen.keypad(1)
        self.initCurses()
        self.grid = {}
        self.active = []
        max_h, max_w = self.screen.getmaxyx()
        if args.fullscreen:
            self.height = max_h
            self.width = max_w
        else:
            self.height = min(24, max_h)
            self.width = min(80, max_w)
        if args.no_hud:
            self.y_pad = 0
            self.x_pad = 0
            self.hud_pad = 0
            self.hud = False
        else:
            self.y_pad = 1
            self.x_pad = 1
            self.hud_pad = 3
            self.hud = True
        self.traditional = args.traditional
        self.y_grid = self.height - self.y_pad - self.hud_pad
        self.x_grid = self.width - self.x_pad - 1
        self.char = ['-', '+', 'o', '%', '8', '0']
        if args.n:
            self.initsize = args.n
        else:
            self.initsize = int(self.x_grid * self.y_grid * 0.15)
        self.rate = args.r
        self.current_gen = 0
        self.change_gen = [1, 2, 3]
        self.color_max = len(self.char)
        self.win = curses.newwin(self.height, self.width, 0, 0)
        self.win.nodelay(1)
        self.patchCurses()
        self.splash()
        if self.hud:
            self.drawHUD()
        if not self.test:
            self.state = 'waiting'
        else:
            self.start

    def __del__(self):
        self.win.clear()
        self.win.refresh()
        curses.echo()
        curses.endwin()

    def initCurses(self):
        """
        Set up screen properties
        """
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_MAGENTA, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_GREEN, -1)
        curses.init_pair(6, curses.COLOR_BLUE, -1)
        curses.init_pair(7, curses.COLOR_RED, -1)

    def patchCurses(self):
        """
        Fix curses addch function for python 3.4.0
        """
        if (sys.version_info)[:3] == (3, 4, 0):
            self.addchar = lambda y, x, *args: self.win.addch(x, y, *args)
        else:
            self.addchar = self.win.addch

    def addstr(self, y, x, text, color=0):
        self.win.addstr(self.height-y, x, str(text), curses.color_pair(color))

    def splash(self):
        """
        Draw splash screen
        """
        dirname = os.path.split(os.path.abspath(__file__))[0]
        try:
            splash = open(os.path.join(dirname, "splash"), "r").readlines()
        except IOError:
            return

        width = len(max(splash, key=len))
        y = int(self.y_grid / 2) - len(splash)
        x = int(self.x_grid / 2) - int(width / 2)

        if self.x_grid > width:
            for i, line in enumerate(splash):
                self.win.addstr(y + i, x, line, curses.color_pair(5))

    def drawHUD(self):
        """
        Draw information on population size and current generation
        """
        self.win.move(self.height - 2, self.x_pad)
        self.win.clrtoeol()
        self.win.box()
        self.addstr(2, self.x_pad + 1, "Population: %i" % len(self.grid))
        self.addstr(3, self.x_pad + 1, "Generation: %s" % self.current_gen)
        self.addstr(3, self.x_grid - 21, "s: start    p: pause")
        self.addstr(2, self.x_grid - 21, "r: restart  q: quit")

    def drawGrid(self):
        """
        Redraw the grid with the new generation
        """
        self.active = list(self.grid.keys())
        for cell in self.active:
            y, x = cell
            y += self.y_pad
            x += self.x_pad

            if self.traditional:
                sprite = '.'
                color = curses.color_pair(4)
            else:
                sprite = self.char[self.grid[cell] - 1]
                color = curses.color_pair(self.grid[cell])

            self.addchar(y, x, sprite, color)

        self.win.refresh()

    def nextGen(self):
        """
        Decide the fate of the cells
        """
        self.current_gen += 1
        self.change_gen[self.current_gen % 3] = copy.copy(self.grid)
        grid_cp = copy.copy(self.grid)
        self.active = list(self.grid.keys())

        for cell in self.active:
            y, x = cell
            y1 = (y - 1) % self.y_grid
            y2 = (y + 1) % self.y_grid
            x1 = (x - 1) % self.x_grid
            x2 = (x + 1) % self.x_grid
            n = self.countNeighbours(cell)

            if n < 2 or n > 3:
                del grid_cp[cell]
                self.addchar(y + self.y_pad, x + self.x_pad, ' ')
            else:
                grid_cp[cell] = min(self.grid[cell] + 1, self.color_max)

            for neighbour in product([y1, y, y2], [x1, x, x2]):
                if not self.grid.get(neighbour):
                    if self.countNeighbours(neighbour) == 3:
                        y, x = neighbour
                        y = y % self.y_grid
                        x = x % self.x_grid
                        neighbour = y, x
                        grid_cp[neighbour] = 1

        self.grid = grid_cp

    def countNeighbours(self, cell):
        """
        Return the number active neighbours within one positions away from cell
        """
        count = 0
        y, x = cell
        y = y % self.y_grid
        x = x % self.x_grid
        y1 = (y - 1) % self.y_grid
        y2 = (y + 1) % self.y_grid
        x1 = (x - 1) % self.x_grid
        x2 = (x + 1) % self.x_grid
        cell = y, x

        for neighbour in product([y1, y, y2], [x1, x, x2]):
            if neighbour != cell and self.grid.get(neighbour):
                count += 1
        return count

    def initGrid(self):
        """
        Initialise the game grid
        """
        blinker = [(4, 4), (4, 5), (4, 6)]
        toad = [(9, 5), (9, 6), (9, 7), (10, 4), (10, 5), (10, 6)]
        glider = [(4, 11), (5, 12), (6, 10), (6, 11), (6, 12)]
        r_pentomino = [(10, 60), (9, 61), (10, 61), (11, 61), (9, 62)]

        self.grid = {}
        self.active = []

        if self.test:
            for cell in chain(blinker, toad, glider, r_pentomino):
                self.grid[cell] = 1
        else:
            for _ in range(self.initsize):
                ry = random.randint(self.y_pad, self.y_grid - 1)
                rx = random.randint(self.x_pad, self.x_grid - 1)
                self.grid[(ry, rx)] = 1

    @property
    def start(self):
        """
        Game logic
        """
        self.initGrid()
        self.win.clear()
        self.state = 'running'

        while self.state == 'running':
            if self.hud:
                self.drawHUD()
            self.drawGrid()
            self.nextGen()
            sleep(self.rate)
            # Has life evolved over 2 generations
            # Better stopping condition needed
            if self.change_gen[0] == self.change_gen[2]:
                self.state = 'stopped'
                break
            key = self.win.getch()
            if key == ord('q'):
                exit()
            if key == ord('r'):
                self.restart
            if key in [ord('p'), ord('s')]:
                self.state = 'paused'
                while self.state == 'paused':
                    key = self.win.getch()
                    if key == ord('q'):
                        exit()
                    if key == ord('r'):
                        self.state = 'running'
                        self.restart
                    if key in [ord('s'), ord('p')]:
                        self.state = 'running'
        self.end()

    @property
    def waiting(self):
        """
        Returns true when waiting for user input
        """
        return self.state == 'waiting'

    @property
    def restart(self):
        """
        Restart the game from a new generation 0
        """
        self.initGrid()
        self.win.clear()
        self.current_gen = 1
        self.start

    @property
    def end(self):
        """
        Game Finished - Restart or Quit
        """
        self.addstr(2, self.x_grid / 2 - 4, "GAMEOVER", 7)

        if self.hud:
            self.addstr(2, self.x_pad + 13, len(self.grid), 5)
            self.addstr(3, self.x_pad + 13, self.current_gen, 5)

        if self.test:
            exit()
        while self.state == 'stopped':
            key = self.win.getch()
            if key == ord('q'):
                exit()
            if key in [ord('s'), ord('r')]:
                self.restart


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fullscreen", action="store_true",
                        default=False, help="display fullscreen grid")
    parser.add_argument("-n", type=int, metavar="initial_points",
                        help="set the number of initial points")
    parser.add_argument("-r", default=0.05, type=float, metavar="refresh_rate",
                        help="set the refresh rate")
    parser.add_argument("-t", "--traditional", action="store_true",
                        default=False, help="traditional mode")
    parser.add_argument("-x", "--no-hud", action="store_true", default=False,
                        help="don't display HUD")
    parser.add_argument('--test', action="store_true", default=False,
                        help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)

    game = gol(parser.parse_args())

    while game.waiting:
        key = game.win.getch()
        if key in [ord('s'), ord('r')]:
            game.start
        elif key == ord('q'):
            exit()


if __name__ == "__main__":
    main()

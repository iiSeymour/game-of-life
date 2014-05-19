#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Python curses implementation of Conway's Game Of Life with an evolutionary twist.

Any live cell with fewer than two live neighbours dies, as if caused by under-population.
Any live cell with two or three live neighbours lives on to the next generation.
Any live cell with more than three live neighbours dies, as if by overcrowding.
Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
"""

import os
import copy
import curses
import random
import argparse
from time import sleep
from itertools import chain, product


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
            self.HUD = False
        else:
            self.y_pad = 1
            self.x_pad = 1
            self.hud_pad = 3
            self.HUD = True
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
        self.state = 'initial'
        self.win = curses.newwin(self.height, self.width, 0, 0)
        self.win.nodelay(1)
        self.Splash()
        if self.HUD: self.DrawHUD()


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


    def Splash(self):
        """
        Draw splash screen
        """
        dirname = os.path.split(os.path.abspath(__file__))[0]
        try:
            splash = open(os.path.join(dirname, "splash"), "r").readlines()
        except IOError:
            return

        l_splash = len(max(splash, key=len))
        y_splash = int(self.y_grid/2) - len(splash)
        x_splash = int(self.x_grid/2) - int(l_splash/2)

        if self.x_grid > l_splash:
            for i, line in enumerate(splash):
                self.win.addstr(y_splash + i, x_splash, line, curses.color_pair(5))


    def DrawHUD(self):
        """
        Draw information on population size and current generation
        """
        self.win.move(self.height - 2, self.x_pad)
        self.win.clrtoeol()
        self.win.box()
        self.win.addstr(self.height - 2, self.x_pad + 1, "Population: %i" % len(self.grid))
        self.win.addstr(self.height - 3, self.x_pad + 1, "Generation: %s" % self.current_gen)
        self.win.addstr(self.height - 3, self.x_grid - 21, "s: start    p: pause")
        self.win.addstr(self.height - 2, self.x_grid - 21, "r: restart  q: quit")


    def DrawGrid(self):
        """
        Redraw the grid with the new generation
        """
        for cell in self.grid.keys():
            y, x = cell
            y += self.y_pad
            x += self.x_pad

            if self.traditional:
                self.win.addch(y, x, '.', curses.color_pair(4))
            else:
                self.win.addch(y, x, self.char[self.grid[cell] - 1], curses.color_pair(self.grid[cell]))
        self.win.refresh()


    def NextGen(self):
        """
        Decide the fate of the cells
        """
        self.current_gen += 1
        self.change_gen[self.current_gen % 3] = copy.copy(self.grid)
        grid_cp = copy.copy(self.grid)
        self.active = self.grid.keys()

        for cell in self.active:
            y, x = cell
            y1 = (y - 1) % self.y_grid
            y2 = (y + 1) % self.y_grid
            x1 = (x - 1) % self.x_grid
            x2 = (x + 1) % self.x_grid
            n = self.CountNeighbours(cell)

            if n < 2 or n > 3:
                del grid_cp[cell]
                self.win.addch(y + self.y_pad, x + self.x_pad, ' ')
            else:
                grid_cp[cell] = min(self.grid[cell] + 1, self.color_max)

            for neighbour in product([y1, y, y2], [x1, x, x2]):
                if neighbour not in self.active:
                    if self.CountNeighbours(neighbour) == 3:
                        y, x = neighbour
                        y = y % self.y_grid
                        x = x % self.x_grid
                        neighbour = y, x
                        grid_cp[neighbour] = 1

        self.grid = grid_cp


    def CountNeighbours(self, cell):
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
            if neighbour in self.active and neighbour != cell:
                count += 1
        return count

    def InitRandom(self):
        """
        Initialise the game with n random points
        """
        self.grid = {}
        self.active = []

        for _ in xrange(self.initsize):
            ry = random.randint(self.y_pad, self.y_grid - 1)
            rx = random.randint(self.x_pad, self.x_grid - 1)
            self.grid[(ry, rx)] = 1


    def InitTest(self):
        """
        Initialise the game with a predefined set up where the behaviour is deterministic
        """
        self.grid = {}
        self.active = []

        blinker = [(4, 4), (4, 5), (4, 6)]
        toad = [(9, 5), (9, 6), (9, 7), (10, 4), (10, 5), (10, 6)]
        glider = [(4, 11), (5, 12), (6, 10), (6, 11), (6, 12)]
        r_pentomino = [(10, 60), (9, 61), (10, 61), (11, 61), (9, 62)]

        for cell in chain(blinker, toad, glider, r_pentomino):
            self.grid[cell] = 1


    def Start(self):
        """
        Game logic
        """
        if self.test: self.InitTest()
        else: self.InitRandom()
        self.win.clear()

        while self.state == 'run':
            if self.HUD: self.DrawHUD()
            self.DrawGrid()
            self.NextGen()
            sleep(self.rate)
            # Has life evolved over 2 generations
            # Better stopping condition needed
            if self.change_gen[0] == self.change_gen[2]:
                self.state = 'stop'
                break
            key = self.win.getch()
            if key == ord('q'):
                return
            if key == ord('r'):
                self.Restart()
            if key in [ord('p'), ord('s')]:
                self.state = 'pause'
                while self.state == 'pause':
                    key = self.win.getch()
                    if key == ord('q'): return
                    if key == ord('r'):
                        self.state = 'run'
                        self.Restart()
                    if key in [ord('s'), ord('p')]:
                        self.state = 'run'
        self.End()


    def Restart(self):
        """
        Restart the game from a new generation 0
        """
        if self.test: self.InitTest()
        else: self.InitRandom()
        self.win.clear()
        self.current_gen = 1

        if self.state == 'stop':
            self.state = 'run'
            self.Start()


    def End(self):
        """
        Game Finished - Restart or Quit
        """
        self.win.addstr(self.height - 2, self.x_grid/2 - 4, "GAMEOVER", curses.color_pair(7))
        if self.HUD:
            self.win.addstr(self.height - 2, self.x_pad + 13, str(len(self.grid)), curses.color_pair(5))
            self.win.addstr(self.height - 3, self.x_pad + 13, str(self.current_gen), curses.color_pair(5))
        while self.state == 'stop':
            key = self.win.getch()
            if key == ord('q'): return
            if key in [ord('s'), ord('r')]:
                self.Restart()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fullscreen", action="store_true", default=False, help="display fullscreen grid")
    parser.add_argument("-n", type=int, metavar="initial_points", help="set the number of initial points")
    parser.add_argument("-r", default=0.02, type=float, metavar="refresh_rate", help="set the refresh rate")
    parser.add_argument("-t", "--traditional", action="store_true", default=False, help="traditional mode")
    parser.add_argument("-x", "--no_hud", action="store_true", default=False, help="don't display HUD")
    parser.add_argument('--test', action="store_true", default=False, help=argparse.SUPPRESS)

    game = gol(parser.parse_args())

    while game.state == 'initial':
        key = game.win.getch()
        if key in [ord('s'), ord('r')]:
            game.state = 'run'
        if key == ord('q'):
            return

    game.Start()


if __name__ == "__main__":
    main()

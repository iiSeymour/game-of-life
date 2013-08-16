"""
Any live cell with fewer than two live neighbours dies, as if caused by under-population.

Any live cell with two or three live neighbours lives on to the next generation.

Any live cell with more than three live neighbours dies, as if by overcrowding.

Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
"""

__TESTING__ = True

import os
import copy
import curses
import random
from time import sleep
from itertools import chain, product

class gol(object):

    def __init__(self, args):
        self.screen = curses.initscr()
        self.screen.keypad(1)
        self.initCurses()
        self.grid = {}
        self.active = []
        max_h, max_w = self.screen.getmaxyx()
        if args.f:
            self.height = max_h
            self.width = max_w
        else:
            self.height = min(24, max_h)
            self.width = min(80, max_w)
        if args.x:
            self.y_pad = 0
            self.x_pad = 0
            self.hud_pad = 0
            self.HUD = False
        else:
            self.y_pad = 1
            self.x_pad = 1
            self.hud_pad = 2
            self.HUD = True

        self.y_grid = self.height - self.y_pad - self.hud_pad - 1
        self.x_grid = self.width - self.x_pad - 1
        self.char = ['.', '-', '*', '#']
        if args.n:
            self.initsize = args.n
        else:
            self.initsize = int(self.x_grid * self.y_grid * 0.15)
        self.rate = args.r
        self.current_gen = 0
        self.color_max = 4
        self.state = 'initial'
        self.win = curses.newwin(self.height, self.width, 0, 0)
        self.win.nodelay(1)
        self.Splash()
        self.DrawHUD()

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
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        return

    def Splash(self):
        """
        Draw splash screen
        """
        dirname = os.path.split(os.path.abspath(__file__))[0]
        splash = open(os.path.join(dirname,"splash"), "r").readlines()

        l_splash = len(max(splash, key=len))
        y_splash = int(self.y_grid/2) - len(splash)
        x_splash = int(self.x_grid/2) - int(l_splash/2)

        if self.x_grid > l_splash:
            for i, line in enumerate(splash):
                self.win.addstr(y_splash + i, x_splash, line)

        return

    def DrawHUD(self):
        """
        Draw information on population size and current generation
        """
        if not self.HUD:
            return
        self.win.move(self.height - 2, self.x_pad)
        self.win.clrtoeol()
        self.win.box()
        self.win.addstr(self.height - 2, self.x_pad, "Population: %i" % len(self.grid))
        self.win.addstr(self.height - 3, self.x_pad, "Generation: %s" % self.current_gen)
        self.win.addstr(self.height - 3, self.x_grid - 19, "s: start   p: pause")
        self.win.addstr(self.height - 2, self.x_grid - 19, "r: restart q: quit")
        return

    def DrawGrid(self):
        """
        Redraw the grid with the new generation
        """
        for cell in self.grid.keys():
            y, x = cell
            self.win.addch(y, x, self.char[self.grid[cell] - 1], curses.color_pair(self.grid[cell]))

        self.win.refresh()
        return

    def inGrid(self, cell):
        """
        Are we within the grid boundary
        """
        y, x = cell

        if (x < self.x_grid and x >= self.x_pad and y <= self.y_grid and y >= self.y_pad):
            return True
        return False

    def NextGen(self):
        """
        Decide the fate of the cells
        """
        self.current_gen += 1
        grid_cp = copy.copy(self.grid)
        self.active = self.grid.keys()

        for cell in self.active:
            y, x = cell
            n = self.CountNeighbours(cell)

            if n < 2 or n > 3:
                del grid_cp[cell]
                self.win.addch(y, x, ' ')
            else:
                grid_cp[cell] = min(self.grid[cell] + 1, self.color_max)

            for neighbour in product([y - 1, y, y + 1], [x - 1, x, x + 1]):
                if neighbour not in self.active and self.inGrid(neighbour):
                    if self.CountNeighbours(neighbour) == 3:
                        grid_cp[neighbour] = 1

        self.grid = grid_cp
        return

    def CountNeighbours(self, cell):
        """
        Return the number active neighbours within one positions away from cell
        """
        count = 0
        y, x = cell

        for neighbour in product([y - 1, y, y + 1], [x - 1, x, x + 1]):
            if neighbour in self.active and neighbour != cell:
                count += 1
        return count

    def InitRandom(self):
        """
        Initialise the game with n random points
        """
        self.grid = {}
        self.active = {}

        for _ in xrange(self.initsize):
            ry = random.randint(self.y_pad, self.y_grid - 1)
            rx = random.randint(self.x_pad, self.x_grid)
            self.grid[(ry, rx)] = 1
        return

    def InitTest(self):
        """
        Initialise the game with a predefined set up where the behaviour is deterministic
        """
        blinker = [(4, 4), (4, 5), (4, 6)]
        toad = [(9, 5), (9, 6), (9, 7), (10, 4), (10, 5), (10, 6)]
        glider = [(4, 11), (5, 12), (6, 10), (6, 11), (6, 12)]
        r_pentomino = [(10, 60), (9, 61), (10, 61), (11, 61), (9, 62)]

        self.grid = {}
        self.active = {}

        for cell in chain(blinker, toad, glider, r_pentomino):
            self.grid[cell] = 1
        return

    def Start(self):
        """
        Game logic
        """
        if __TESTING__:
            self.InitTest()
        else:
            self.InitRandom()
        self.win.clear()

        while self.state == 'run':
            if __TESTING__ and self.current_gen == 100:
                return
            self.DrawHUD()
            self.DrawGrid()
            sleep(self.rate)
            self.NextGen()
            key = self.win.getch()
            if key == ord('q'):
                return
            if key == ord('r'):
                self.Restart()
            if key in [ord('p'), ord('s')]:
                self.state = 'pause'
                while self.state == 'pause':
                    key = self.win.getch()
                    if key == ord('q'):
                        return
                    if key == ord('r'):
                        self.state = 'run'
                        self.Restart()
                    if key in [ord('s'),ord('p')]:
                        self.state = 'run'

        # drop here when population stable over 2 generations
        self.state = 'stop'
        self.End()
        return

    def Restart(self):
        """
        Restart the game from a new generation 0
        """
        if __TESTING__:
            self.InitTest()
        else:
            self.InitRandom()
        self.win.clear()
        self.current_gen = 0
        return

    def End(self):
        """
        Game Finished - Restart or Quit?
        """
        while self.state == 'stop':
            key = self.win.getch()
            if key == ord('q'):
                return
            if key in [ord('s'),ord('r')]:
                self.state = 'run'
                self.Start()
        return

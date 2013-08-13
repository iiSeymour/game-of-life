"""
Any live cell with fewer than two live neighbours dies, as if caused by under-population.

Any live cell with two or three live neighbours lives on to the next generation.

Any live cell with more than three live neighbours dies, as if by overcrowding.

Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
"""

import copy
import curses
import random
import argparse
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
        self.y_pad = 2
        self.x_pad = 2
        self.y_grid = self.height - self.y_pad - 2
        self.x_grid = self.width - self.x_pad - 1
        self.char = ['.', '-', '*', '#']
        self.initsize = args.n
        self.rate = args.r
        self.max_gen = args.g
        self.current_gen = 0
        self.color_max = 4
        self.win = curses.newwin(self.height, self.width, 0, 0)
        self.g = curses.newwin(self.y_grid, self.x_grid, 1, 1)
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

        splash = r"""
          _____                         ____   __   _      _  __
         / ____|                       / __ \ / _| | |    (_)/ _|
        | |  __  __ _ _ __ ___   ___  | |  | | |_  | |     _| |_ ___
        | | |_ |/ _` | '_ ` _ \ / _ \ | |  | |  _| | |    | |  _/ _ \
        | |__| | (_| | | | | | |  __/ | |__| | |   | |____| | ||  __/
         \_____|\__,_|_| |_| |_|\___|  \____/|_|   |______|_|_| \___|
        """


        self.win.addstr(self.height/2 - 8, self.width/2, splash)

        return

    def DrawHUD(self):
        """
        Draw information on population size and current generation
        """
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
            x, y = cell
            self.win.addch(x, y, self.char[self.grid[cell] - 1], curses.color_pair(self.grid[cell]))

        self.win.refresh()
        return

    def inGrid(self, cell):
        """
        Are we within the grid boundary
        """
        y, x = cell

        if (x < self.x_grid and x > self.x_pad and y < self.y_grid and y > self.y_pad):
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
            x, y = cell
            n = self.CountNeighbours(cell)

            if n < 2 or n > 3:
                del grid_cp[cell]
                self.win.addch(x, y, ' ')
            else:
                grid_cp[cell] = min(self.grid[cell] + 1, self.color_max)

            for neighbour in product([x - 1, x, x + 1], [y - 1, y, y + 1]):
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
        x, y = cell

        for neighbour in product([x-1, x, x+1], [y-1, y, y+1]):
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
            ry = random.randint(self.y_pad, self.y_grid)
            rx = random.randint(self.x_pad, self.x_grid)
            self.grid[(ry, rx)] = 1
        return

    def TestStart(self):
        """
        Initialise the game with a predefined set up where the behaviour is deterministic
        """
        blinker = [(4, 4), (4, 5), (4, 6)]
        toad = [(9, 5), (9, 6), (9, 7), (10, 4), (10, 5), (10, 6)]
        glider = [(4, 11), (5, 12), (6, 10), (6, 11), (6, 12)]
        r_pentomino = [(5, 40), (4, 41), (5, 41), (6, 41), (4, 42)]

        for cell in chain(blinker, toad, glider, r_pentomino):
            self.grid[cell] = 1
        return

    def Start(self):
        """
        Game logic
        """

        # Initial screen
        self.InitRandom()
        self.win.clear()

        while True:
            self.DrawHUD()
            self.DrawGrid()
            sleep(self.rate)
            self.NextGen()
            key = self.win.getch()
            if key == ord('q'):
                return
            if key == ord('r'):
                self.Restart()
            if key == ord('p'):
                PAUSE = True
                while PAUSE:
                    key = self.win.getch()
                    if key == ord('q'):
                        return
                    if key == ord('r'):
                        self.Restart()
                        PAUSE = False
                    if key in [ord('s'),ord('p')]:
                        PAUSE = False
        self.End()
        return

    def Restart(self):
        """
        Restart the game from a new generation 0
        """
        self.InitRandom()
        self.win.clear()
        self.current_gen = 0
        return

    def End(self):
        """
        Game Finished - Restart or Quit?
        """
        while True:
            key = self.win.getch()
            if key == ord('q'):
                return
            if key in [ord('s'),ord('r')]:
                self.Start()
        return


def main(args):
    game = gol(args)
    while True:
        key = game.win.getch()
        if key in [ord('s'),ord('r')]:
            break
        if key == ord('q'):
            return
    game.Start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", action="store_true",
                        default=False, help="Display fullscreen grid")
    parser.add_argument(
        "-g", default=50, type=int, help="Set maximum number of generations")
    parser.add_argument(
        "-r", default=0.02, type=float, help="Set the refresh rate")
    parser.add_argument(
        "-n", default=300, type=int, help="Set the number of initial points")
    main(parser.parse_args())

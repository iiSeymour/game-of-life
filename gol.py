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
        self.screen.nodelay(1)
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
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
        self.rate = args.r
        self.generations = args.g
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.color_max = 4
        self.win = curses.newwin(self.height, self.width, 0, 0)

    def __del__(self):
        self.win.clear()
        self.win.refresh()
        curses.echo()
        curses.endwin()

    def DrawHUD(self, n):
        """
        Draw information on population size and current generation
        """
        self.win.addstr(1, 2, "Game of Life")
        self.win.move(self.height - 2, self.x_pad)
        self.win.clrtoeol()
        self.win.box()
        self.win.addstr(self.height - 2, self.x_pad, "Population: %i" % len(self.grid))
        self.win.addstr(self.height - 3, self.x_pad, "Generation: %s" % n)
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

    def Breed(self):
        """
        main loop iterating through generations, population should be
        initialised before calling Breed using RandomStart or TestStart
        """
        for i in xrange(self.generations + 1):
            self.DrawHUD(i)
            self.DrawGrid()
            sleep(self.rate)
            self.NextGen()
            if self.screen.getch() == ord('q'):
                break
        return

    def RandomStart(self, n):
        """
        Initialise the game with n random points
        """
        for _ in xrange(n):
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


def main(args):
    game = gol(args)
    game.RandomStart(args.n)
    game.Breed()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", action="store_true",
                        default=False, help="Display fullscreen grid")
    parser.add_argument(
        "-g", default=50, type=int, help="The number of generations")
    parser.add_argument(
        "-r", default=0.02, type=float, help="The refresh rate")
    parser.add_argument(
        "-n", default=300, type=int, help="The number of initial points")
    main(parser.parse_args())

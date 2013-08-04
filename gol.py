"""
Any live cell with fewer than two live neighbours dies,
as if caused by under-population.

Any live cell with two or three live neighbours lives
on to the next generation.

Any live cell with more than three live neighbours dies,
as if by overcrowding.

Any dead cell with exactly three live neighbours becomes a live cell,
as if by reproduction.
"""

import copy
import curses
import random
import argparse
from time import sleep


class gol(object):

    def __init__(self, args):
        self.screen = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.grid = {}
        self.x, self.y = (0, 0)
        self.height, self.width = self.screen.getmaxyx()
        self.y_pad = 3
        self.x_pad = 2
        self.char = "*"
        self.generations = args.g
        self.rate = args.r
        self.win = curses.newwin(self.height, self.width, self.y, self.x)
        self.win.box()
        self.win.addstr(1, 2, "Game of Life")

    def __del__(self):
        self.win.clear()
        self.win.refresh()
        curses.echo()
        curses.endwin()

    def DrawHUD(self, n=0):
        """
        Draw information on population size and current generation
        """
        self.win.addstr(self.height - self.y_pad, self.x_pad, "Population: %i   " % len(self.grid))
        self.win.addstr(self.height - self.x_pad, self.x_pad, "Generation: %s" % n)
        return

    def DrawGrid(self):
        """
        Redraw the grid with the new generation
        """
        cGrid = copy.deepcopy(self.grid)

        for i in range(self.y_pad, self.height - self.y_pad):
            for j in range(self.x_pad, self.width - self.x_pad):
                cell = (i, j)
                n = self.CountNeighbours(cell)
                if cell in self.grid.keys():
                    self.win.addch(i, j, self.char)
                    if n < 2 or n > 3:
                        del cGrid[cell]
                else:
                    self.win.addch(i, j, ' ')
                    if n == 3:
                        cGrid[cell] = 1

        self.grid = copy.deepcopy(cGrid)

        self.win.refresh()
        return

    def CountNeighbours(self, cell):
        """
        Return the number active neighbours
        within one positions away from cell
        """
        count = 0
        x, y = cell
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if (i, j) in self.grid.keys() and (i, j) != cell:
                    count += 1
        return count

    def Breed(self):
        for i in range(1, self.generations + 1):
            self.DrawHUD(i)
            self.DrawGrid()
            sleep(self.rate)
        return

    def RandomStart(self, n):
        """
        Initialise the game with n random points
        """
        for _ in range(0, n):
            ry = random.randint(self.y_pad, self.height - self.y_pad)
            rx = random.randint(self.x_pad, self.width - self.x_pad)
            self.grid[(ry, rx)] = 1

        self.DrawHUD()
        self.DrawGrid()
        sleep(self.rate)
        return

    def TestStart(self):
        """
        Initialise the game with a predefined set
        up where the behaviour is deterministic
        """

        # Blinker
        self.grid[(4, 4)] = 1
        self.grid[(4, 5)] = 1
        self.grid[(4, 6)] = 1

        # Toad
        self.grid[(9, 5)] = 1
        self.grid[(9, 6)] = 1
        self.grid[(9, 7)] = 1
        self.grid[(10, 4)] = 1
        self.grid[(10, 5)] = 1
        self.grid[(10, 6)] = 1

        # Glider
        self.grid[(4, 11)] = 1
        self.grid[(5, 12)] = 1
        self.grid[(6, 10)] = 1
        self.grid[(6, 11)] = 1
        self.grid[(6, 12)] = 1

        self.DrawHUD()
        self.DrawGrid()
        sleep(self.rate)
        return


def main(args):
    game = gol(args)
    game.RandomStart(args.n)
    game.Breed()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", default=50, type=int, help="The number of generations")
    parser.add_argument("-r", default=0.02, type=float, help="The refresh rate")
    parser.add_argument("-n", default=300, type=int, help="The number of initial points")
    main(parser.parse_args())

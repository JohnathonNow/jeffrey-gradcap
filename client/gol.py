#!/usr/bin/env python2
#    This file is a game of life implementation for the client for the software on my graduation cap, Jeffrey-Gradcap.
#    Copyright (C) 2018 John Westhoff

#    This file is part of Jeffrey-Gradcap.
#
#    Jeffrey-Gradcap is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Jeffrey-Gradcap is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Jeffrey-Gradcap.  If not, see <http://www.gnu.org/licenses/>.

import random

class Ecosystem:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.board = [0 for i in range(0, w*h)]

    def __getitem__(self, i):
        x = i[0] % self.w
        y = i[1] % self.h
        return self.board[x + self.h*y]

    def live(self, i):
        x = i[0] % self.w
        y = i[1] % self.h
        return 1 if self.board[x + self.h*y] else 0

    def __setitem__(self, i, val):
        x = i[0] % self.w
        y = i[1] % self.h
        self.board[x + self.w*y] = val

    def __iter__(self):
        return EcoIterator(self)

    def tick(self):
        newboard = self.board[:]
        for x in range(0, self.w):
            for y in range(0, self.h):
                n = self.live((x+1,y))   \
                  + self.live((x-1,y))   \
                  + self.live((x,y+1))   \
                  + self.live((x,y-1))   \
                  + self.live((x+1,y+1)) \
                  + self.live((x+1,y-1)) \
                  + self.live((x-1,y-1)) \
                  + self.live((x-1,y+1))  
                if self[(x,y)]:
                    if n < 2:
                        newboard[x+y*self.w] = 0
                    elif n >= 2 and n <= 3:
                        newboard[x+y*self.w] += 1
                    elif n > 3:
                        newboard[x+y*self.w] = 0
                elif n == 3:
                    newboard[x+y*self.w] = 1
        self.board = newboard

    def color(self, x, y):
        a = self[(x,y)]
        colors = [(0, 0, 0),
                  (255, 255, 255),
                  (255, 255, 128),
                  (255, 255, 0),
                  (255, 170, 0),
                  (255, 60, 0),
                  (255, 0, 0),
                  (255, 0, 60),
                  (120, 0, 120),
                  (0, 0, 255)]
        if a < len(colors) and a >= 0:
            return colors[a]
        else:
            return (0, 0, 255)

    def seed(self):
        for i in self:
            if random.randint(0, 10) == 1:
                self[i] = 1

class EcoIterator:
    def __init__(self, ecosystem):
        self.ecosystem = ecosystem
        self.x = 0
        self.y = 0

    def __iter___(self):
        return self

    def next(self):
        if self.y >= self.ecosystem.h:
            raise StopIteration()
        else:
            x = self.x
            y = self.y
            self.x += 1
            if self.x >= self.ecosystem.w:
                self.x = 0
                self.y += 1
            return (x,y)


if __name__ == '__main__':
    e = Ecosystem(32, 32)
    e.seed()
    e.tick()
    for i in e:
        print(e.color(*i))

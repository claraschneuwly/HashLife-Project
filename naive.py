#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 18:23:43 2021

@author: claraschneuwly
"""

class Universe:
    def round(self):
        """Compute (in place) the next generation of the universe"""
        raise NotImplementedError

    def get(self, i, j):
        """Returns the state of the cell at coordinates (ij[0], ij[1])"""
        raise NotImplementedError

    def rounds(self, n):
        """Compute (in place) the n-th next generation of the universe"""
        for _i in range(n):
            self.round()
            
class Cell:
    """Encodes a live point in the Game of Life.
    Data attributes:
    x -- x-coordinate
    y -- y-coordinate
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    

class NaiveUniverse(Universe):
    def __init__(self, n, m, cells):
        # Do something here
        self.matrix = [[_ for _ in range(m)] for i in range(n)]
        self.cells = cells
    def round(self):
        # Do something here
        raise NotImplementedError()

    def get(self, i, j):
        # Do something here
        raise NotImplementedError()
        
    def get_neighbors(self, c):    
        l = []
        for x in range(self.c.x-1, self.c.x+2):
            for y in range(self.y-1, self.y+2):
                s.add(Point(x,y))       
        s.discard(self)
        return s
        
        
        
        
        
        
        
        
        
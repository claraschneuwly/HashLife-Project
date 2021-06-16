#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 18:23:43 2021

@author: claraschneuwly
"""
import math
import weakref

HC = weakref.WeakValueDictionary()

def hc(s):
    return HC.setdefault(s, s)

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

# (3, 3, [[False, True, False], [False, True, False], [False, True, False]])

class NaiveUniverse(Universe):
    def __init__(self, n, m, cells):
        self.x_size = n
        self.y_size = m 
        self.board = cells
    
    def alive_neighbors(self,i,j):
        """Compute the number of alive neighbors of the point at coordinates (i,j)"""
        min_i = max(0,i-1)
        max_i = min(self.x_size-1,i+1)
        min_j = max(0, j-1)
        max_j = min(self.y_size-1,j+1)
        
        res = 0
        
        for k in range(min_i,max_i+1):
            for l in range(min_j,max_j+1):
                if self.board[k][l]:
                    res += 1
        if self.board[i][j]:
            res -= 1
        return res            

    def round(self):
        """Compute (in place) the next generation of the universe"""
        l = []
        for i in range(self.x_size):
            l_ = []
            for j in range(self.y_size):
                l_ += [self.alive_neighbors(i,j)]
            l += [l_]
       # print(l)
        for i in range(self.x_size):
            for j in range(self.y_size):
                #print(i,j)
                if not self.board[i][j] and l[i][j] == 3:
                    self.board[i][j] = True
                if self.board[i][j] and l[i][j] != 3 and l[i][j] != 2:
                    self.board[i][j] = False

    def get(self, i, j):
        """Returns the state of the cell at coordinates (ij[0], ij[1])"""
        return self.board[i][j]
            
    
class AbstractNode:
    BIG = True 
    def __init__(self, cache=None):
        self._cache = cache
        self._hash = None
       
    
    def __hash__(self):
        if self._hash is None:
            self._hash = (
                self.population,
                self.level     ,
                self.nw        ,
                self.ne        ,
                self.sw        ,
                self.se        ,
            )
            self._hash = hash(self._hash)
        return self._hash
        
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, AbstractNode):
            return False
        return \
            self.level      == other.level      and \
            self.population == other.population and \
            self.nw         is other.nw         and \
            self.ne         is other.ne         and \
            self.sw         is other.sw         and \
            self.se         is other.se
    
    @staticmethod
    def canon(node):
        return hc(node)
        
    @staticmethod
    def cell(alive):
        return hc(CellNode(alive))
    
    @staticmethod
    def node(nw, ne, sw, se):
        return hc(Node(nw, ne, sw, se))
     
    @property
    def level(self):
        """Level of this node"""
        raise NotImplementedError()

    @property
    def population(self):
        """Total population of the area"""
        raise NotImplementedError()

    nw = property(lambda self : None)
    ne = property(lambda self : None)
    sw = property(lambda self : None)
    se = property(lambda self : None)
 
    # def zero(self, k):
    #     """returns a node of level k whose population is empty"""
    #     return None
    
    @staticmethod
    def zero(k):
        """returns a node of level k whose population is empty"""
        if k == 0:
            return AbstractNode.cell(0)
    
        a = AbstractNode.cell(0)
        
        for i in range(k):
            a = AbstractNode.node(a,a,a,a)
        return a
    
    
    # (a,b,c) = 1,2,3
    # for i in range(2):
    #     print(a,b,c)
    #     (a,b,c) = a+b, a+c, b+c
    
    def extend(self):
        """returns a node whose level is one higher than the one of self 
        and s.t. its central area is equal to self"""
        if self.level == 0:
            return AbstractNode.node(AbstractNode.cell(0),self,AbstractNode.cell(0),AbstractNode.cell(0))
        else:
            z = self.zero(self._nw.level)
            
            nw = AbstractNode.node(z,z,z,self._nw)
            ne = AbstractNode.node(z,z,self._ne,z) 
            sw = AbstractNode.node(z,self._sw,z,z) 
            se = AbstractNode.node(self._se,z,z,z) 
            
            return AbstractNode.node(nw,ne,sw,se)
        
        
    def round2(self,a,b,c,d,e,f,g,h,i):
        res = 0
        for node in (a, b, c, d, f, g, h, i):
            if node._alive:
                res += 1
        if (e._alive and res == 2) or res == 3:
            return self.cell(True)
        else:
            return self.cell(False)
        
    def create_mask(self):
        i = 16
        l = 0
        a = [self.nw.nw,self.nw.ne,self.ne.nw,self.ne.ne,self.nw.sw,self.nw.se,self.ne.sw,self.ne.se,self.sw.nw,self.sw.ne,self.se.nw,self.se.ne,self.sw.sw,self.sw.se,self.se.sw,self.se.se]
        for node in a:
            i -= 1
            if node.alive:
                 l += 2**i
        return l 
                
    def forward(self, l=None):
        if l == None or l > self._level-2:
            l = self._level -2
        if self._cache and l in self._cache.keys() :
            return self._cache[l]
        if self._level == 0:
            return self._nw
        if self._population == 0:
            return AbstractNode.zero(self.level-1)
        if self._level < 2:
            return None
        elif self._level == 2:
        
            # nw = self.round2(self._nw._nw,self._nw._ne,self._ne._nw,self._nw._sw,self._nw._se, self._ne._sw, self._sw._nw, self._sw._ne, self._se._nw)
            # ne = self.round2(self._nw._ne,self._ne._nw,self._ne._ne,self._nw._se,self._ne._sw, self._ne._se, self._sw._ne, self._se._nw, self._se._ne)
            # sw = self.round2(self._nw._sw,self._nw._se,self._ne._sw,self._sw._nw,self._sw._ne, self._se._nw, self._sw._sw, self._sw._se, self._se._sw)
            # se = self.round2(self._nw._se,self._ne._sw,self._ne._se,self._sw._ne,self._se._nw, self._se._ne, self._sw._se, self._se._sw, self._se._se)
            #return self.node(nw,ne,sw,se)
      
            mask = self.create_mask()
            return self.level2_bitmask(mask)
        # else:
        #     rNW = self.node(self._nw._nw, self._nw._ne, self._nw._sw, self._nw._se).forward(l)
        #     rTC = self.node(self._nw._ne, self._ne._nw, self._nw._se, self._ne._sw).forward(l)
        #     rNE = self.node(self._ne._nw, self._ne._ne, self._ne._sw, self._ne._se).forward(l)
        #     rCL = self.node(self._nw._sw, self._nw._se, self._sw._nw, self._sw._ne).forward(l)        
        #     rCC = self.node(self._nw._se, self._ne._sw, self._sw._ne, self._se._nw).forward(l)
        #     rCR = self.node(self._ne._sw, self._ne._se, self._se._nw, self._se._ne).forward(l)
        #     rSW = self.node(self._sw._nw, self._sw._ne, self._sw._sw, self._sw._se).forward(l)
        #     rBC = self.node(self._sw._ne, self._se._nw, self._sw._se, self._se._sw).forward(l)
        #     rSE = self.node(self._se._nw, self._se._ne, self._se._sw, self._se._se).forward(l)
        #     if l == self.level-2:
        #          res = self.node(self.node(rNW._se,rTC._sw,rCL._ne,rCC.nw), self.node(rTC._se,rNE._sw,rCC._ne,rCR.nw), self.node(rCL._se,rCC._sw,rSW._ne,rBC.nw), self.node(rCC._se,rCR._sw,rBC._ne,rSE.nw))
        #     else:
        #          res = self.node(self.node(rNW,rTC,rCL,rCC).forward(l),self.node(rTC,rNE,rCC,rCR).forward(l),self.node(rCL,rCC,rSW,rBC).forward(l),self.node(rCC,rCR,rBC,rSE).forward(l))
        #elif l > 0 and l < self._level-2:
        else:
            rNW = self.node(self._nw._nw, self._nw._ne, self._nw._sw, self._nw._se).forward(l)
            rTC = self.node(self._nw._ne, self._ne._nw, self._nw._se, self._ne._sw).forward(l)
            rNE = self.node(self._ne._nw, self._ne._ne, self._ne._sw, self._ne._se).forward(l)
            rCL = self.node(self._nw._sw, self._nw._se, self._sw._nw, self._sw._ne).forward(l)        
            rCC = self.node(self._nw._se, self._ne._sw, self._sw._ne, self._se._nw).forward(l)
            rCR = self.node(self._ne._sw, self._ne._se, self._se._nw, self._se._ne).forward(l)
            rSW = self.node(self._sw._nw, self._sw._ne, self._sw._sw, self._sw._se).forward(l)
            rBC = self.node(self._sw._ne, self._se._nw, self._sw._se, self._se._sw).forward(l)
            rSE = self.node(self._se._nw, self._se._ne, self._se._sw, self._se._se).forward(l)
            if l == self.level-2:
                res = self.node(self.node(rNW,rTC,rCL,rCC).forward(l),self.node(rTC,rNE,rCC,rCR).forward(l),self.node(rCL,rCC,rSW,rBC).forward(l),self.node(rCC,rCR,rBC,rSE).forward(l))
            else:
                res = self.node(self.node(rNW._se,rTC._sw,rCL._ne,rCC.nw), self.node(rTC._se,rNE._sw,rCC._ne,rCR.nw), self.node(rCL._se,rCC._sw,rSW._ne,rBC.nw), self.node(rCC._se,rCR._sw,rBC._ne,rSE.nw))
                
            #print(l)
            if self._cache is None: 
                self._cache = {l:res} 
            else:
                self._cache[l] = res
            return res   
        # else:
        #     # first compute the state of C in 2^k−3 generations
        #     rNW = self.node(self._nw._nw, self._nw._ne, self._nw._sw, self._nw._se).forward()
        #     rTC = self.node(self._nw._ne, self._ne._nw, self._nw._se, self._ne._sw).forward()
        #     rNE = self.node(self._ne._nw, self._ne._ne, self._ne._sw, self._ne._se).forward()
        #     rCL = self.node(self._nw._sw, self._nw._se, self._sw._nw, self._sw._ne).forward()        
        #     rCC = self.node(self._nw._se, self._ne._sw, self._sw._ne, self._se._nw).forward()
        #     rCR = self.node(self._ne._sw, self._ne._se, self._se._nw, self._se._ne).forward()
        #     rSW = self.node(self._sw._nw, self._sw._ne, self._sw._sw, self._sw._se).forward()
        #     rBC = self.node(self._sw._ne, self._se._nw, self._sw._se, self._se._sw).forward()
        #     rSE = self.node(self._se._nw, self._se._ne, self._se._sw, self._se._se).forward()
            
        #     #new time jump of 2k−3 generations
        #     res = self.node(self.node(rNW, rTC, rCL, rCC).forward(), self.node(rTC, rNE, rCC, rCR).forward(), self.node(rCL, rCC, rSW, rBC).forward(), self.node(rCC, rCR, rBC, rSE).forward())   
        #     if self._cache is None: 
        #         self._cache = {l:res} 
        #     else:
        #         self._cache[l] = res
        #     return res
            
class CellNode(AbstractNode):
    def __init__(self, alive):
        super().__init__()

        self._alive = bool(alive)

    level      = property(lambda self : 0)
    population = property(lambda self : int(self._alive))
    alive      = property(lambda self : self._alive)


class Node(AbstractNode):
    def __init__(self, nw, ne, sw, se):
        super().__init__()

        self._level      = 1 + nw.level
        self._population =  \
            nw.population + \
            ne.population + \
            sw.population + \
            se.population
        self._nw = nw
        self._ne = ne
        self._sw = sw
        self._se = se

    level      = property(lambda self : self._level)
    population = property(lambda self : self._population)

    nw = property(lambda self : self._nw)
    ne = property(lambda self : self._ne)
    sw = property(lambda self : self._sw)
    se = property(lambda self : self._se)
    
    @staticmethod
    def level2_bitmask(mask):
        b5 = 0b0000011101010111
        m5 = mask & b5
       # print(m5)
        n5 = 0
        while m5 != 0:
           m5 = m5 & (m5-1)
           n5+=1
        print(n5)
        if (mask & 0b0000000000100000 != 0 and n5 == 2) or n5 == 3:
            cell_5 = AbstractNode.cell(True)
        else:
            cell_5 = AbstractNode.cell(False)
       
        
        b6 = 0b0000111010101110
        m6 = mask & b6
        #print(m6)
        n6 = 0
        while m6 != 0:
            m6 = m6 & (m6-1)
            n6+=1
        print(n6)
        if (mask & 0b0000000001000000 != 0 and n6 == 2) or n6 == 3:
            cell_6 = AbstractNode.cell(True)
        else:
            cell_6 = AbstractNode.cell(False)
            
        b9 = 0b0111010101110000
        m9 = mask & b9
      #  print(m9)
        n9 = 0
        while m9 != 0:
            m9 = m9 & (m9-1)
            n9+=1  
        print(n9)
        if (mask & 0b0000001000000000 != 0 and n9 == 2) or n9 == 3:
            cell_9 = AbstractNode.cell(True)
        else:
            cell_9 = AbstractNode.cell(False)
            
        b10 = 0b1110101011100000
        m10 = mask & b10
       # print(m10)
        n10 = 0
        while m10 != 0:
            m10 = m10 & (m10-1)
            n10+=1  
        print(n10)
        if (mask & 0b0000010000000000 != 0 and n10 == 2) or n10 == 3:
            cell_10 = AbstractNode.cell(True)
        else:
            cell_10 = AbstractNode.cell(False)
        
        return AbstractNode.node(cell_10, cell_9, cell_6, cell_5)

class HashLifeUniverse(Universe):
    def __init__(self, *args):
        if len(args) == 1:
            self._root = args[0]
        else:
            self._root = HashLifeUniverse.load(*args)

        self._generation = 0

    @staticmethod
    def load(n, m, cells):
        level = math.ceil(math.log(max(1, n, m), 2))

        mkcell = getattr(AbstractNode, 'cell', CellNode)
        mknode = getattr(AbstractNode, 'node', Node    )

        def get(i, j):
            i, j = i + n // 2, j + m // 2
            return \
                i in range(n) and \
                j in range(m) and \
                cells[i][j]
                
        def create(i, j, level):
            if level == 0:
                return mkcell(get (i, j))

            noffset = 1 if level < 2 else 1 << (level - 2)
            poffset = 0 if level < 2 else 1 << (level - 2)

            nw = create(i-noffset, j+poffset, level - 1)
            sw = create(i-noffset, j-noffset, level - 1)
            ne = create(i+poffset, j+poffset, level - 1)
            se = create(i+poffset, j-noffset, level - 1)

            return mknode(nw=nw, ne=ne, sw=sw, se=se)
                
        return create(0, 0, level)

    def get(self, i, j):
        """Returns the state of the cell at coordinates (ij[0], ij[1])"""
    #     if i > self._root._level or j > self._root._level:
    #         return False
        
    #     return 
    
   
    #return self.get()

   

    def round(self):
        """Compute (in place) the next generation of the universe"""
        return self.rounds(1)
    
    def peripheral_band(self):
        return [self.root._nw._nw, self.root._nw._ne, self.root._ne._nw, self.root._nw._ne, self.root._ne._se, self.root._se._ne, self.root._se._se, self.root._se._sw, self.root._sw._se, self.root._sw._sw, self.root._sw._nw, self.root._nw._sw]
    
    def check_empty(self, p):
        t = True
        for i in p:
            if i.population != 0:
                t = False 
        return t
    
    def extend(self, k):
        # if self.level == 0:
        #     AbsractNode.extend(self)
            
        
        while self._root.level < max(k,2) or not self.check_empty(self.peripheral_band()):
            self._root = self._root.extend()
            #p = self.peripheral_band()
            
    def rounds(self, n):
        """Compute (in place) the n next generations of the universe"""
        n_ = bin(n)
        l = []
        for i in range(2,len(n_)):
            l = [int(n_[i])] + l
        #self.extend(len(l))
        for i in range(len(l)):
            if l[i] == 1:
                if self.root.level < 2:
                    self._root = self.root.extend()
                #if 
                self.extend(i+2)
                self._root = self.root.forward(i)
        self._generation += n


    @property
    def root(self):
        return self._root
        
    @property
    def generation(self):
        return self._generation
        
        
        
        
        
        
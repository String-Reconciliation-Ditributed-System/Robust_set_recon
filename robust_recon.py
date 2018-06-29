from iblt import IBLT
from pyemd import emd, emd_samples
from pyqtree import Index as qt # quadtree
from itertools import permutations
import numpy as np
from collections import Counter

# this is implemented for a 1-D integer situation
# Bowen Song
# Jun, 2018
class data:
    
    def randomshift(self, range, eps=None):
        if (self.len != 0):
            '''this is for 1-d'''
            if(eps is None):
                eps = np.random.choice(self.content,1)
            self.content = np.remainder(self.content+eps,range)
            print self.content
            return eps
        else:
            raise ValueError('The array is empty for randomshift')

    def revrandomshift(self,range, eps):
        if (self.len==0):
            raise ValueError('The array is empty for randomshift')
        if (eps is None):
            raise ValueError('eps is required')
        self.content = np.remainder(self.content-eps,range)
        print self.content

    @staticmethod
    def commonrange(Alice, Bob):
        '''Input Data format'''
        return max(Alice.content) if max(Alice.content) > max(Bob.content) else max(Bob.content)

    def __init__(self,array):
        self.content = array
        self.len = len(self.content) # can later become range of 0 - a number since randomshift uses mod
        self.L = np.log2(self.len)

class quadtree:
    # create a 1-D quadtree based on 1-D array
    # an array of dictionary , dictionary is a level, array from level 0 (leaf)
    # to L (root); built from bottom up
    def __init__(self,array,range):
        # all items of a set are in an array
        self.array = array
        self.range = range
        # qt range has to be multiples of 4
        self.qtrange = int(4**np.ceil(np.log(range)/np.log(4)))
        # number of levels for this quad tree
        self.levels = int(np.log(self.qtrange)/np.log(4) + 1)  # 4 coz quad, +1 coz level 0
        # item with their count in dict
        self.set = Counter(self.array)
        # qt array
        self.qtree = []
        self.build()
        # return number of levels

    def build(self):
        # build from bottom up
        self.qtree.append(dict(self.set))  # leaf level
        for i in list(reversed(range(1, self.levels))):  # iterate through each level, start at second level
            # print self.qtrange/4**i
            # tolerance has to be int
            self.qtree.append(self.insertlevel(int(self.qtrange/4**i)))

        self.qtree.append(self.insertlevel(int(self.qtrange)))  # root node

    def insertlevel(self,tolerance):
        '''returns a dict of {(lower range, upper range): occurrence}
        assume integer'''
        leveldict = {}
        for item in self.array:
            levelrange = (int(item - item % tolerance),
                          int(item+(-item) % tolerance - 1))
            if levelrange in leveldict.keys():
                leveldict[levelrange] = leveldict[levelrange] + self.set[item]
            else:
                leveldict[levelrange] = self.set[item]
        return leveldict

    def printqt(self):
        print("Quadtree: ")
        for level in self.qtree:
            print(level)


class emd1d:
    def padlength(self):
        if(len(self.alice)!=len(self.bob)):
            self.len = max(len(self.alice),len(self.bob))
            if ( len(self.alice) > len(self.bob) ):
                self.bob = [self.bob ,np.zeros(self.len - len(self.bob))]
            else:
                self.alice = [self.alice ,np.zeros(self.len - len(self.alice))]
                pass

        else:
            self.len = len(self.alice)

    # def minpair(self):
    # 	# padd with zeros if not the same length

    def __init__(self,alice,bob):
        '''input alice set and bob set as array'''
        if(len(alice)!=0 and len(bob)!=0):
            self.alice = alice
            self.bob = bob
            self.padlength()
            self.alicepermu = np.matrix(permutations(alice))
            self.bobpermu = np.matrix(permutations(bob))

            return
        else:
            raise ValueError("Either Alice or Bob is empty")

if __name__ == "__main__":
    
    # Toy Example
    Alice = data(np.array([1,2,9,12,33],dtype=float))
    Bob = data(np.array([1,2,9,10,12,28],dtype=float))
    # random shift
    rag = data.commonrange(Alice,Bob)
    print rag
    EPS = Alice.randomshift(rag)
    print(EPS)
    Bob.randomshift(rag,EPS)

    # Building Quadtree
    Aliceqt = quadtree(Alice.content,rag)
    Bobqt = quadtree(Bob.content,rag)
    Aliceqt.printqt()
    Bobqt.printqt()

    # reverse Random shift
    Bob.revrandomshift(rag,EPS)


    #alicetree = quadtree(Alice.content,Alice.L)
    #tb = IBLT(m,k,keysize,valsize,hashsize,hashfunc)




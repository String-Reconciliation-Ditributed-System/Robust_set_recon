from iblt import IBLT
from pyemd import emd, emd_samples
from pyqtree import Index as qt # quadtree
from ast import literal_eval
from itertools import permutations
import numpy as np
from collections import Counter

# this is implemented for a 1-D integer situation
# version is not handeled by the protocol (every level needs version control)
# Affecting current two-way scheme adding any extra elements

# Bowen Song
# Jun, 2018

def dictInsert(key, value, Dict):
    # type: (str, int, dict)->dict
    '''
    insert a key value pair into a dict
    :param key: range or int number in str and later parse with ast
    :param value: number of occurrences
    :param Dict: carrier dict
    :return: revised dict
    '''
    if key in Dict.keys():
        Dict[key] = Dict[key] + value
    else:
        Dict[key] = value
    return Dict


class data:
    
    def randomshift(self, range, eps=None):
        if (self.len != 0):
            '''this is for 1-d'''
            if(eps is None):
                eps = np.random.choice(self.content, 1)
            self.content = np.remainder(self.content+eps, range)
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
        '''Input Data format, if not +1 max item mixed with 0'''
        return max(Alice.content)+1 if max(Alice.content) > max(Bob.content) else max(Bob.content)+1

    def __init__(self,array):
        self.content = array
        self.len = len(self.content) # can later become range of 0 - a number since randomshift uses mod
        self.L = np.log2(self.len)

    def padding(self,num, occr):
        # type: (int, int)->[]
        '''
        create an array with respect to its occurrence
        :param num: the number item
        :param occr: its occurrences int >0
        :return: array of this item with its occurrences.
        '''
        if occr < 1:
            return []
        return np.pad(num, (0, occr-1), 'mean')

    def diffadd(self, adding, isleaf):
        # type: (dict,bool)->[]
        '''
        What needs to be added by the dict provided
        :param adding: dict of need to add elements
        :param isleaf: if it is leaf add the item, if its range, add the mean
        :return: array of items needs tobe added
        '''
        addition = []
        if isleaf:
            for item in adding.keys():
                addition.append(self.padding(item, adding[item][0]).tolist())
        else:
            for item in adding.keys():
                addition.append(self.padding(np.average(item), adding[item][0]).tolist())
        self.content = np.concatenate((self.content, np.array(addition)))
        return self.content

    def diffdel(self, deleting, isleaf):
        # type: (dict,bool)->[]
        '''
        What needs to be added by the dict provided
        :param adding: dict of need to add elements
        :param isleaf: if it is leaf add the item, if its range, add the mean
        :return: array of items needs tobe added
        '''
        deletion = []
        if isleaf:
            for item in deleting.keys():
                self.content = np.delete(self.content, np.argwhere(self.content==item))
        else:
            for item in deleting.keys():
                self.content = np.delete(self.content, np.argwhere(self.content in range(item[1], item[0])))
        return self.content

class quadtree:
    # create a 1-D quadtree based on 1-D array
    # an array of dictionary , dictionary is a level, array from level 0 (leaf)
    # to L (root); built from bottom up
    def __init__(self, array, range):
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
            leveldict = dictInsert(levelrange, self.set[item], leveldict)
            # if levelrange in leveldict.keys():
            #     leveldict[levelrange] = leveldict[levelrange] + self.set[item]
            # else:
            #     leveldict[levelrange] = self.set[item]
        return leveldict

    def printqt(self):
        print("Quadtree: ")
        for level in self.qtree:
            print(level)


class ibltC:
    # IBLT compression
    def __init__(self,k):
        '''
        Init an IBLT with specified size
        :param k: size of IBLT
        '''
        # fins a way to specify size of IBLT based on k
        self.IBLTsize = (10, 10, 50, 50)
        self.ibltTree = []
        self.treeHeight = 0

    def encode(self,qtree):
        '''
        Encoding the entire tree into IBLT's
        :param qtree: a quad tree, Array of dictionaries
        :return: a quad tree, Array of IBLTs
        '''
        for item in qtree:
            self.ibltTree.append(self.insertlevel(item))
            self.treeHeight+=1
        return self.ibltTree

    def insertlevel(self,level):
        # type: (dict)->IBLT
        '''
        insert a level of quad tree into a IBLT table
        :param level: dict of a level of quadtree
        :return: a IBLT table for a level
        '''
        _iblt = IBLT(*self.IBLTsize)
        for item in level.keys():
            _iblt.insert("{"+str(item)+":"+str(level[item])+"}", "")
        # print _iblt.list_entries()
        return _iblt

    def deletelevel(self,level, _iblt):
        # type: (dict)->IBLT
        '''
        insert a level of quad tree into a IBLT table
        :param level: dict of a level of quadtree
        :return: a IBLT table for a level
        '''
        for item in level.keys():
            _iblt.delete("{"+str(item)+":"+str(level[item])+"}", "")
        print _iblt.list_entries()
        return _iblt

    def issuccess(self,level):
        # type: ([])->bool
        if level[0] is "complete":
            return True
        return False

    def iblt2tree(self,iblt):
        # type: (IBLT)->dict
        '''
        converting IBLT to array
        :param iblt: iblts
        :return: symmetric diff tree
        '''
        Bobdif = iblt[1]
        Alicedif = iblt[2]
        bobdifdic = {}
        alicedifdic = {}
        for item in Bobdif:
            pitem = literal_eval(item[0])
            # if it is a range or int
            if type(pitem.keys()[0]) in [tuple, float]:
                bobdifdic = dictInsert(pitem.keys()[0], pitem.values(), bobdifdic)
            else:
                raise ValueError("decoded item is not in range or number")
        for item in Alicedif:
            pitem = literal_eval(item[0])
            # if it is a range or int
            if type(pitem.keys()[0]) in [tuple, float]:
                alicedifdic = dictInsert(pitem.keys()[0], pitem.values(), alicedifdic)
            else:
                raise ValueError("decoded item is not in range or number")
        return bobdifdic, alicedifdic, not self.islevelrange(bobdifdic)

    def islevelrange(self, dicttree):
        '''
        input a tree level see if it is leaf
        :param dicttree: level in dict
        :return: bool
        '''
        if len(dicttree.keys())>0 and type(dicttree.keys()[0]) is tuple:
            return True
        return False

    def decode(self, qtree):
        '''
        Decode a quad tree of IBLT's
        :param qttree: Local quad tree
        :param qtIBLT: Recieved IBLT tree
        :return: 2 dicts of Symmetric difference
        '''
        print "symmetric difference"
        for i in range(self.treeHeight):
            self.deletelevel(qtree[i], self.ibltTree[i])
            ibltLvLst = self.ibltTree[i].list_entries()
            if self.issuccess(ibltLvLst):
                return self.iblt2tree(ibltLvLst)
                # if isoneway:
                #     # one way, we correct Bob entirely based on Alice
                #     if self.islevelrange(bobadd):
                #         # we add points at the center of the range
                #         # and deletes random points from a range
                #     else:
                #         # we elaborately add all and send what alice is missing
                #     return
                # else:
                #     # else two-way, we correct both Bob and Alice
                #     return
        # out of for loop with out any successful levels
        raise ValueError("No IBLT can be decoded")

class emd1d:
    def padlength(self):
        if(len(self.alice)!=len(self.bob)):
            self.len = max(len(self.alice),len(self.bob))
            if ( len(self.alice) > len(self.bob) ):
                self.bob = [self.bob, np.zeros(self.len - len(self.bob))]
            else:
                self.alice = [self.alice, np.zeros(self.len - len(self.alice))]
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
    Bob = data(np.array([1,2,9,10,12,28,30,31],dtype=float))
    # random shift
    rag = data.commonrange(Alice,Bob)
    print "Range: " + str(rag)
    EPS = Alice.randomshift(rag)
    print "Epsilon: " + str(EPS)
    Bob.randomshift(rag,EPS)

    # Building Quadtree
    Aliceqt = quadtree(Alice.content,rag)
    Bobqt = quadtree(Bob.content,rag)
    Aliceqt.printqt()
    Bobqt.printqt()

    # Insert Every level into IBLT of K size
    kmsgsize = 5
    aliceiblt = ibltC(kmsgsize)
    aliceiblt.encode(Aliceqt.qtree)

    # send aliceiblt over here we evaluate the msg size ------ not done

    # find symmetrical diff and adjust on Host Bob
    bobadd, aliceadd, isleaf = aliceiblt.decode(Bobqt.qtree)

    oneway = False  # using one-way or two-way scheme
    if oneway:
        # one-way add what Bob is missing, delete what Alice does not have
        Bob.diffadd(bobadd,isleaf)
        Bob.diffdel(aliceadd,isleaf)
        # reverse Random shift
        print("Reconciled Alice Set")
        Alice.revrandomshift(rag,EPS)
        print("Reconciled Bob Set")
        Bob.revrandomshift(rag, EPS)
    else:
        # two-way add what Bob is missing, send to alice what she should have
        Bob.diffadd(bobadd,isleaf)
        Alice.diffadd(aliceadd,isleaf)
        # reverse Random shift
        print("Reconciled Alice Set")
        Alice.revrandomshift(rag,EPS)
        print("Reconciled Bob Set")
        Bob.revrandomshift(rag, EPS)

    # EMD distance




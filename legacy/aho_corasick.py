import Queue

class Node:
    def __init__ (self, depth, index):
        self.depth = depth
        self.index = index
        self.child = [None]*26
        self.c = []
        self.isEnd = False
        self.fall = None
        self.parent = None
    def addWord (self, s):
        if self.depth == len(s):
            self.isEnd = True
            return
        curr = s[self.depth]
        index = ord(curr) - ord('a')
        if self.child[index] == None:
            self.child[index] = Node(self.depth + 1, index)
            self.child[index].parent = self
            self.c += [index]
        self.child[index].addWord(s)

root = Node(0, 0)
root.parent = root;

def computeFall ():
    q = Queue.Queue()
    root.fall = root
    q.put(root)
    while not q.empty():
        curr = q.get()
        for i in curr.c:
            q.put(curr.child[i])
        if curr.fall != None:
            continue
        fall = curr.parent.fall
        while fall.child[curr.index] == None and fall != root:
            fall = fall.fall
        curr.fall = fall.child[curr.index]
        if curr.fall == None or curr.fall == curr:
            curr.fall = root
            
def printWord (n):
    if n != root:
        return printWord(n.parent) + chr(n.index + ord('a'))
    return ""
def search (s):
    currState = root
    for i in range(len(s)):
        curr = s[i]
        index = ord(curr) - ord('a') 
        while currState.child[index] == None and currState != root:
            currState = currState.fall
        if currState == root:
            if currState.child[index] != None:
                currState = currState.child[index]
        else:
            currState = currState.child[index]
        
        other = currState
        while other != root:
            if other.isEnd:
                print str(printWord(other)) + " at " + str(i)
            other = other.fall
root.addWord("apple")
root.addWord("banana")
computeFall()
search("askfjasjfklasjfasfjpabananasfjawofjoawjfopjapapple")
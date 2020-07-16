import pyTSF as tsf
import random
from math import sqrt
from math import log as ln
from time import time
# Needs alternating expansion, policy calls.

MCRTrials = 20
MCRActs = 100

FRAME_CHUNK_SIZE=10

UCBCParam = .1

# Library of possible player commands
comm0 = tsf.PlayerCommand()
comm1 = tsf.PlayerCommand()
comm2 = tsf.PlayerCommand()
comm3 = tsf.PlayerCommand()
comm4 = tsf.PlayerCommand()
directions=[tsf.NO_TURN,tsf.TURN_LEFT,tsf.TURN_RIGHT]
thrust=[True,False]
fire=[False,True]
comm0.turn=directions[0]
comm0.thrust=thrust[0]
comm0.fire=fire[0]
comm1.turn=directions[1]
comm1.thrust=thrust[0]
comm1.fire=fire[0]
comm2.turn=directions[2]
comm2.thrust=thrust[0]
comm2.fire=fire[0]
comm3.turn=directions[0]
comm3.thrust=thrust[1]
comm3.fire=fire[0]
comm4.turn=directions[0]
comm4.thrust=thrust[0]
comm4.fire=fire[1]


player_actions = [comm0,comm1,comm2,comm3,comm4]

# Library of fortress commands
fortress_actions = list()
for i in range(0,2):
    for j in range(0,2):
        fcomm = tsf.FortressCommand()
        fcomm.targetID=i
        fcomm.fireProb=j
        fortress_actions.append(fcomm)

builder = tsf.JsonGameBuilder("configs/sf_config_tick_clock.json")
tempGame = builder.build()

class StateNode():
    def __init__(self,state,tree,parent=None,clock=None):
        self.tree=tree
        self.parent = parent
        self.state = state
        self.children=dict()
        self.value=0
        self.trials=0
    def MCRollout(self):
        rootState=self.state
        p0 = tempGame.getPlayerByID(0)
        p1 = tempGame.getPlayerByID(1)
        self.value = 0
        for _ in range(MCRTrials):
            tempGame.setState(rootState)
            for _ in range(MCRActs):
                p0.command(random.choice(player_actions))
                p1.command(random.choice(player_actions))
                tempGame.gameClock.tick()
                self.value += tempGame.getState().score
        self.trials+=MCRTrials
        node = self
        while node.parent != None:
            node.parent.trials+=MCRTrials
            node.parent.value+=node.value
            node = node.parent
    def expand(self,frontier):
        frontier.remove(self)
        tempGame.setState(self.state)
        clock = tempGame.gameClock
        human = tempGame.getPlayerByID(0)
        agent = tempGame.getPlayerByID(1)
        fortress = tempGame.getFortressByID(0)
        # @Dana, how can I call the policy here
        for i in range(len(player_actions)):
            for j in range(len(player_actions)):
                for k in range(len(fortress_actions)):
                    tempGame.setState(self.state)
                    human.command(player_actions[i])
                    agent.command(player_actions[j])
                    fortress.command(fortress_actions[k])
                    [clock.tick() for _ in range(FRAME_CHUNK_SIZE)]
                    newNode=StateNode(tempGame.getState(),self.tree,parent=self)
                    newNode.MCRollout()
                    self.children[(i,j,k)] = newNode
                    frontier.add(newNode)

class GameTree():
    def __init__(self):
        self.builder = tsf.JsonGameBuilder("configs/sf_config_tick_clock.json")
        self.game = builder.build()
        self.clock = self.game.gameClock
        self.human = self.game.getPlayerByID(0)
        self.agent = self.game.getPlayerByID(1)
        self.fortress = self.game.getFortressByID(0)
        self.clock.tick()
        # Mark root node and adjacency sets
        self.root = self.getState()
        self.frontier = set([self.root])
        self.root.expand(self.frontier)
        # Implement expansion selection
    def tick(self):
        self.clock.tick()
    def walkback(self,newState):
        self.game.setState(newState.state)
    def getState(self):
        return StateNode(self.game.getState(),self)
    def processMove(self,moves=None):
        if moves==None:
            currNode=max(self.frontier, key=lambda x: x.value)
            while currNode.parent!=self.root: currNode=currNode.parent
            self.root=currNode
        else:
            self.root=self.root.children[moves]
        newFront=set()
        for fn in frontier:
            n = fn
            while n!=None:
                if n==self.root:
                    newFront.add(fn)
                n=n.parent
        del self.frontier
        self.frontier=newFront
    def selectAndExpand(self):
        def UCBEq(node):
            w=node.value
            s=node.trials
            return w/(s+1)+UCBCParam*sqrt(ln(node.parent.trials)/s)
        max(self.frontier,key=UCBEq).expand(self.frontier)

if __name__=="__main__":
    gt=GameTree()
    print("Running 5 expansions")
    for i in range(5):
        z=-time()
        gt.selectAndExpand()
        z+=time()
        print("    Expansion {}: {}".format(i,z)
    #Move forward a frame
    gt.processMove()
    #Print leaf values
    for n in gt.frontier: print(n.value/n.trials)

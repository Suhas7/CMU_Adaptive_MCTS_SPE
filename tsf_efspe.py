import pyTSF as tsf
import random

MCRTrials = 20
MCRActs = 100

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
comm0.turn=directions[0], comm0.thrust=thrust[0], comm0.fire=fire[0]
comm1.turn=directions[1], comm1.thrust=thrust[0], comm1.fire=fire[0]
comm2.turn=directions[2], comm2.thrust=thrust[0], comm2.fire=fire[0]
comm3.turn=directions[0], comm3.thrust=thrust[1], comm3.fire=fire[0]
comm4.turn=directions[0], comm4.thrust=thrust[0], comm4.fire=fire[1]

player_actions = set([comm0,comm1,comm2,comm3,comm4])

self.builder = tsf.JsonGameBuilder("configs/sf_config_tick_clock.json")
tempGame = builder.build()

class StateNode():
	def __init__(self,state,parent=None,clock=None):
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
				clock.tick()
				self.value += tempGame.getState().score
		self.trials+=MCRTrials
		node = self
		while node.parent != None:
			node.parent.trials+=MCRTrials
			node.parent.value+=node.value
			node=node.parent

	def expand(self,frontier):
		frontier.remove(self)
		tempGame.setState(self.state)
		clock = tempGame.gameClock
		human = tempGame.getPlayerByID(0)
		agent = tempGame.getPlayerByID(1)
		# self.fortress = game.getPlayerByID(3)
		# @Dana, how can I call the policy here
		for i in range(len(player_actions)):
			for j in range(len(player_actions)):
				tempGame.setState(self.state)
				human.command(player_actions[i])
				agent.command(player_actions[j])
				clock.tick()
				newNode=StateNode(tempGame.getState(),parent=self.state)
				newNode.MCRollout()
				self.children[(i,j)] = newNode
				frontier.add(newNode)

class GameTree():
	def __init__(self):
		self.builder = tsf.JsonGameBuilder("configs/sf_config_tick_clock.json")
		self.game = builder.build()
		self.clock = game.gameClock
		self.human = game.getPlayerByID(0)
		self.agent = game.getPlayerByID(1)
		# self.fortress = game.getPlayerByID(3)
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
		return StateNode(self.game.getState(),self,None)
	def processMove(moves):
		self.root=self.root.children[moves]
	def selectAndExpand(self):
		def UCBEq(node):
			w=node.value
			s=node.trials
			return w/(s+1)+UCBCParam*sqrt(ln(node.parent.trials)/s)
		max(self.frontier,key=UCBEq).expand(self.frontier)


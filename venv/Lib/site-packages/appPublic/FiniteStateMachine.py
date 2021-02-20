# FiniteStateMachine.py
## a virtual State object of FSM
# 
class BaseFSM(object):
	def enterState(self, obj):
		raise NotImplementedError()
 
	def execState(self, obj):
		raise NotImplementedError()
 
	def exitState(self, obj):
		raise NotImplementedError()

## a FMS Manager
#  only need one Manager for a FSM
class FSMManager(object):
	def __init__(self):
		self._fsms = {}

	def addState(self,state,fsm):
		self._fsms[state] = fsm
	
	def delState(self,state):
		del self._fsms[state]      
	
	def getFSM(self, state):
		return self._fsms[state]
      
	def frame(self, objs, state):
		for obj in objs:
			if state == obj.curr_state:
				obj.keepState()
			else:
				obj.changeState(state, self._fsms[state])

## the object with has a Finite State Machine
# 
class FSMObject(object):
	def attachFSM(self,state,fsm):
		self.fsm_state_object = fsm
		self.fsm_cur_state = state
		
	def changeState(self,new_state,newfsm):
		self.fsm_cur_state = new_state
		self.fsm_state_object.exitState(self)
		self.fsm_state_object = new_fsm
		self.fsm_state_object.enterState(self)
		self.fsm_state_object.execState(self)
		
	def keepState(self):
		self.fsm_state_object.execState(self)
		
	
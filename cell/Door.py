# -*- coding: gb18030 -*-

"""
门
"""


from NPCObject import NPCObject


class Door( NPCObject ):
	"""
	Door
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		NPCObject.__init__( self )

	def onCorpseDelayTimer( self, controllerID, userData ):
		"""
		MONSTER_CORPSE_DELAY_TIMER_CBID的callback函数；
		"""
		self.destroy()
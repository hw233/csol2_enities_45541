# -*- coding: gb18030 -*-

"""
��
"""


from NPCObject import NPCObject


class Door( NPCObject ):
	"""
	Door
	"""
	def __init__(self):
		"""
		���캯����
		"""
		NPCObject.__init__( self )

	def onCorpseDelayTimer( self, controllerID, userData ):
		"""
		MONSTER_CORPSE_DELAY_TIMER_CBID��callback������
		"""
		self.destroy()
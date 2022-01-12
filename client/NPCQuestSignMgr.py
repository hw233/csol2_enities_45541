# -*- coding: gb18030 -*-
#

import Language
from config import NPCQuestSign


class NPCQuestSignMgr:
	__inst = None
	

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = NPCQuestSignMgr()
		return SELF.__inst


	def __init__( self ):
		"""
		"""
		self._npcQuestSignData = NPCQuestSign.Datas
	
	def getSignBySignID( self, signID ):
		"""
		@type		signID: int32
		"""
		try:
			return self._npcQuestSignData[signID]['sign']
		except:
			return ""
	
	def getStateBySignID( self, signID ):
		"""
		@type		signID: int32
		"""
		try:
			return self._npcQuestSignData[signID]['state']
		except:
			return 0

npcQSignMgr = NPCQuestSignMgr.instance()
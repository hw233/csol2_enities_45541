# -*- coding: gb18030 -*-
#
#$Id:$

import BigWorld
import csdefine
from bwdebug import *

class FuncCancelHoldFamilyNPC:
	"""
	ȡ��ռ��ĳ������NPC
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass
		
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.endGossip( talkEntity )
		player.client.family_askForCancelFamilyNPC()
		
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if player.family_grade == csdefine.FAMILY_GRADE_SHAIKH:
			key = "flyNPC." + talkEntity.className
			if BigWorld.globalData.has_key( key ):		
				dbid, name = BigWorld.globalData[ key ]
				if player.family_dbID == dbid:
					return True
		return False



#$Log:$
#
# 
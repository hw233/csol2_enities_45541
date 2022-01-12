# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst
from ActivityRecordMgr import g_activityRecordMgr
from ObjectScripts.GameObjectFactory import g_objFactory

class FuncYiJieZhanChang( Function ):
	"""
	�������ս������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.spaceName = section.readString( "param1" ) # �����ͼclassName

	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_DESERTER_BUFF_ID ):
			player.statusMessage( csstatus.YI_JIE_ZHAN_CHANG_DESERTER_ABANDON )
			return
		
		objScript = g_objFactory.getObject( self.spaceName )
		pos, direction = objScript.getRandomEnterPos()
		player.gotoSpace( self.spaceName, pos, direction )

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
		return True


# -*- coding: gb18030 -*-

"""
"""
from Function import Function
import csdefine
import csstatus
import Language
import time
import BigWorld
from bwdebug import *

class FuncTouch( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
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
		player.endGossip( talkEntity )


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
		if talkEntity.isReal():
			talkEntity.getScript().touch( talkEntity )
		else:
			talkEntity.remoteScriptCall( "touch", () )
		return False


class FuncOpenDoor( Function ):
	"""
	�Ի�������
	"""
	def __init__( self, section ):
		"""
		"""
		# param1: �ţ�������ʲô������Ҫ����param2������
		# param2: �ŵ�����(�ַ���)����ѡֵ��self.doorType��
		# �ŵ����;�������ε���openDoor���� -_-!
		
		# ��ô����Ĵ�����Բ����ұ��⣬������openDoor���ַ�����Ȼ���ǽӿڵ�һ���֣�
		# ��˲�ͬ�ĸ����в�ͬ�ĵ��÷�ʽ���еĴ��������dict,�е����ַ������е���className
		# �������"openDoorDict","openDoorStr","openDoorClassName"��Щ����Ĺؼ��֣����Ǿ�
		# ������������һ���ŵ����͡�
		
		self.acceptDoorType = [ "monsterType", "dict" ] # �����Ҫ�����������������
		
		self.doorType = section.readString( "param2" ) # �ŵ�����
		
		# Ϊ�˺���ǰ�����ñ��ּ��ݣ����doorType�����ôĬ��ΪmonsterType
		if self.doorType == "": self.doorType = "monsterType"
		
		DEBUG_MSG( "doorType = %s"%self.doorType )
		
		assert self.doorType in self.acceptDoorType,"Invalid door type!"
		
		# ����doorType��ʼ��door
		if self.doorType == "monsterType":
			self.door = section.readInt( "param1" )
		elif self.doorType == "dict":
			self.door = section.readString( "param1" )
		#elif more doorType:
		#	some init work
		else:
			assert False,"Code path should never reach here!"
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		
		spaceBase = player.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "Can't find space base!" )
			return
		
		# �����ŵ�����ѡ��ͬ�ĵ��÷�ʽ
		if self.doorType == "monsterType":
			player.getCurrentSpaceBase().openDoor( self.door )
		elif self.doorType == "dict":
			player.getCurrentSpaceBase().openDoor( { "entityName": self.door } )
		else:
			ERROR_MSG( "Code path should never reach here!" )

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

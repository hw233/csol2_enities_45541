# -*- coding:gb18030 -*-

from Function import Function
import csconst
import csdefine

class FuncCityWarGetTongActionVal( Function ):
	"""
	���ռ�������ȡ�ж����Ի�����
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.actionValDict = {}
		level = 1
		for actionValString in section.readString( "param1" ).split( ";" ):
			self.actionValDict[level] = int( actionValString )
			level += 1
			
	def do( self, player, talkEntity = None ):
		"""
		"""
		if talkEntity is None:
			return
		if not player.isTongChief():
			return
		if player.tong_holdCity != player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ):
			return
		playerTongEntity = player.tong_getSelfTongEntity()
		if not playerTongEntity:
			return
		#playerTongEntity.addDailyCityWarActionVal( self.actionValDict[player.tong_level] )
		
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
		return player.tong_holdCity == player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) and player.isTongChief()

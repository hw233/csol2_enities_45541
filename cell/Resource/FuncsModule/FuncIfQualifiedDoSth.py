# -*- coding: gb18030 -*-


import csstatus
import cschannel_msgs
import BigWorld
import csdefine
import items
from Function import Function
from bwdebug import *
g_items = items.instance()



class FuncSpellTargetIfQualified( Function ):
	"""
	���û����Ӧ����Ʒ����ô������ͷ�һ������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )		# ��Ҫ������Ʒ itemId1|itemId2|itemId3 ������
		self._skillID = section.readInt( "param2" )		# �����ļ���ID(��Ϊ��������һ��buff)
		self._describe = section.readString( "param3" )	# ������Ʒʱ������
		if len( self._p1 ):
			self._requireItems = self._p1.split( "|" )		# ��Ҫ������ƷID���� type:str
		else:
			self._requireItems = []


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
		for itemID in self._requireItems:
			item = player.findItemFromNKCK_( int( itemID ) )
			if item:
				talkEntity.say( self._describe )
				return

		talkEntity.spellTarget( self._skillID, player.id )

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



class FuncGiveItemIfQualified( Function ):
	"""
	���û����Ӧ����Ʒ����ô���������Ӧ����Ʒ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )					# ��Ҫ������Ʒ itemId1|itemId2|itemId3 ������
		self._p2 = section.readString( "param2" )					# ��������Ʒ itemId1|itemId2|itemId3 ������
		self._describe = section.readString( "param3" )				# ������Ʒʱ������
		if len( self._p1 ):
			self._requireItems = self._p1.split( "|" )					# ��Ҫ������ƷID���� type:str
		else:
			self._requireItems = []
		if len( self._p2 ):
			self._rewardItems = self._p2.split( "|" )					# ��������ƷID���� type:str
		else:
			self._rewardItems = []
		

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
		for itemID in self._requireItems:
			item = player.findItemFromNKCK_( int( itemID ) )
			if item:
				talkEntity.say( self._describe )
				return

		self.rewardPlayer( player )


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

	def rewardPlayer( self, player ):
		"""
		�������
		"""
		items = []
		for itemID in self._rewardItems:
			item = g_items.createDynamicItem( int( itemID ) )
			items.append( item )
			if item is None:
				ERROR_MSG( "item %s not exist." % itemID )
				return
				
		kitbagState = player.checkItemsPlaceIntoNK_( items )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			# �����ռ䲻��װ
			player.statusMessage( csstatus.CIB_MSG_ITEMBAG_SPACE_NOT_ENOUGH )
		else:
			for item in items:
				player.addItem( item, csdefine.ADD_ITEM_BY_TALK )


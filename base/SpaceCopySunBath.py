# -*- coding: gb18030 -*-
# ����SpaceMultiLine�������չ�ԡ������Ϊ�˶�ʱ��ˢ�³��������

import Love3
import BigWorld
import Const
import random
from bwdebug import *
from interface.GameObject import GameObject
from SpaceMultiLine import SpaceMultiLine
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objFactory = GameObjectFactory.instance()

SUERARG_START_TIME = 10001	# ˢ�±���Timer���


class SpaceCopySunBath( SpaceMultiLine ):
	"""
	����SpaceMultiLine�������չ�ԡ������Ϊ�˶�ʱ��ˢ�³��������
	"""
	def __init__(self):
		"""
		���캯����
		"""
		super( SpaceCopySunBath, self ).__init__()
		self.__currSpawnID	= 0								# ��ʱ����	:	���ڳ�����ʼ��ʱ��¼��ǰ���ص�spawnPoint����
		self._sunBathSpellIDList = []						# ���չ�ԡ���������б��ǵ�ID�б�
		self.registerLoadEntityType( "QuestShellBox" )
		self.registerLoadEntityType( "BCNPC" )
		self.spellNum = self.getScript()._spellNum

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		if entityType == "QuestShellBox": # ���Ϊ�������ͣ������ID������
			self._sunBathSpellIDList.append( baseEntity.id )

	def initLoadEntityParams( self, params ):
		"""
		virtual method.
		��ʼ��Ҫ������entity�Ĳ���
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	params			: �ײ��Ѿ�������Ĭ�ϴ�������
		@type 	params			: dict		
		"""
		super( SpaceCopySunBath, self ).initLoadEntityParams( params )
		params[ "lineNumber" ] = self.lineNumber
		return params

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceMultiLine.onSpawnPointLoadedOver( self, retCode )
		if retCode == Const.SPACE_LOADSPAWN_RET_OVER:
			self.addRefreshSpellTimer()	# �չ�ԡ�������������Ϻ�addTimerˢ�±���

	def addRefreshSpellTimer( self ):
		"""
		���Ӽ�ʱ����ˢ�±���
		"""
		#self.getScript().refreshSpell()	# ����֮���չ�ԡ�������������Ϻ���ˢһ�Σ�
		#������ʱ��ˢ�±��ǣ�WARNING: ServerEntityMailBox::sendStream() :Cell entity channel not established, buffering message for entity 2350�����Կ��Ǽ�һ��Timer
		spellRefreshTime = self.getScript()._spellRefreshTime
		assert spellRefreshTime > 0	# ���ʱ��������0
		self.addTimer( spellRefreshTime, spellRefreshTime, SUERARG_START_TIME )
		
	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceMultiLine.onTimer( self, id, userArg )
		if userArg == SUERARG_START_TIME:	# ˢ��һ�α���
			self.refreshSpell()
			return
			
	def refreshSpell( self ):
		"""
		ˢ��һ�α���
		"""
		tempIDList = []
		
		# ���tempIDListû�е�����ˢ������
		while len( tempIDList ) < min( self.spellNum, len( self._sunBathSpellIDList ) ):
			tempID = random.choice( self._sunBathSpellIDList )	# ��_sunBathSpellIDList�����ѡȡһ��id
			if not tempID in tempIDList:	# һ��IDֻ��ѡȡһ��
				tempIDList.append( tempID )
				BigWorld.entities[tempID].spawnShell()	# ˢ��ĳ������

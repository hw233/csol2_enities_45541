# -*- coding: gb18030 -*-
# 重载SpaceMultiLine，创建日光浴场景，为了定时间刷新场景中物件

import Love3
import BigWorld
import Const
import random
from bwdebug import *
from interface.GameObject import GameObject
from SpaceMultiLine import SpaceMultiLine
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objFactory = GameObjectFactory.instance()

SUERARG_START_TIME = 10001	# 刷新贝壳Timer标记


class SpaceCopySunBath( SpaceMultiLine ):
	"""
	重载SpaceMultiLine，创建日光浴场景，为了定时间刷新场景中物件
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		super( SpaceCopySunBath, self ).__init__()
		self.__currSpawnID	= 0								# 临时变量	:	用于场景初始化时记录当前加载的spawnPoint索引
		self._sunBathSpellIDList = []						# 存日光浴场景中所有贝壳的ID列表
		self.registerLoadEntityType( "QuestShellBox" )
		self.registerLoadEntityType( "BCNPC" )
		self.spellNum = self.getScript()._spellNum

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		if entityType == "QuestShellBox": # 如果为贝壳类型，则把它ID存起来
			self._sunBathSpellIDList.append( baseEntity.id )

	def initLoadEntityParams( self, params ):
		"""
		virtual method.
		初始化要创建的entity的参数
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	params			: 底层已经给出的默认创建参数
		@type 	params			: dict		
		"""
		super( SpaceCopySunBath, self ).initLoadEntityParams( params )
		params[ "lineNumber" ] = self.lineNumber
		return params

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceMultiLine.onSpawnPointLoadedOver( self, retCode )
		if retCode == Const.SPACE_LOADSPAWN_RET_OVER:
			self.addRefreshSpellTimer()	# 日光浴场景物件加载完毕后，addTimer刷新贝壳

	def addRefreshSpellTimer( self ):
		"""
		增加计时器，刷新贝壳
		"""
		#self.getScript().refreshSpell()	# 启动之后日光浴场景物件加载完毕后，先刷一次，
		#如果这个时候刷新贝壳：WARNING: ServerEntityMailBox::sendStream() :Cell entity channel not established, buffering message for entity 2350，可以考虑加一个Timer
		spellRefreshTime = self.getScript()._spellRefreshTime
		assert spellRefreshTime > 0	# 间隔时间必须大于0
		self.addTimer( spellRefreshTime, spellRefreshTime, SUERARG_START_TIME )
		
	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceMultiLine.onTimer( self, id, userArg )
		if userArg == SUERARG_START_TIME:	# 刷新一次贝壳
			self.refreshSpell()
			return
			
	def refreshSpell( self ):
		"""
		刷新一次贝壳
		"""
		tempIDList = []
		
		# 如果tempIDList没有到贝壳刷新数量
		while len( tempIDList ) < min( self.spellNum, len( self._sunBathSpellIDList ) ):
			tempID = random.choice( self._sunBathSpellIDList )	# 从_sunBathSpellIDList中随机选取一个id
			if not tempID in tempIDList:	# 一个ID只能选取一次
				tempIDList.append( tempID )
				BigWorld.entities[tempID].spawnShell()	# 刷新某个贝壳

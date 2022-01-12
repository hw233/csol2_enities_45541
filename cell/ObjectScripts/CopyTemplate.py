# -*- coding: gb18030 -*-

# ------------------------------------------------
# from python
import copy
# ------------------------------------------------
# from common
from bwdebug import *
import Language
import csdefine
# ------------------------------------------------
# from cell
import Const
import Resource.CopyStage.CopyStageBase as CopyStageBase
from interface.CopyStageInterface import CopyStageInterface
# ------------------------------------------------
# from current directory
from SpaceCopy import SpaceCopy
# ------------------------------------------------

class CopyTemplate( SpaceCopy, CopyStageInterface ) :
	"""
	副本模板
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		CopyStageInterface.__init__( self )
		self._stageFile = ""					# 副本的关卡配置文件
		self._stageSection = None

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopy.load( self, section )

		self._spaceConfigInfo["extended_shown"] =\
			[int(i) for i in section.readString("extended_shown").split()]

		if section.has_key( "CopyStageFile" ) :
			self.loadStages(section.readString("CopyStageFile"))

	def loadStages(self, stage_file_path):
		"""
		加载阶段内容配置
		@type	stage_file_path:	string
		@param	stage_file_path:	file path
		"""
		self._stageFile = stage_file_path
		assert self._stageFile != "", "the CopyStageFile is NULL."

		self._stageSection = Language.openConfigSection( self._stageFile )
		assert self._stageSection is not None, "open %s false." % self._stageFile

		for childSect in self._stageSection.values() :
			copyStage = CopyStageBase.CopyStageBase()
			copyStage.init( childSect )
			self.addStage( copyStage )
			copyStage.setIndexInCopy( len( self._stages ) - 1 )

		# 清除缓冲
		Language.purgeConfig( self._stageFile )

	def getCopyStageFile( self ) :
		"""
		获取关卡配置文件
		"""
		return self._stageFile

	def getCopyStageSection( self ) :
		"""
		"""
		return self._stageSection

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )

		params["baseMailbox"] = baseMailbox
		currentStage = self.getCurrentStage( selfEntity )
		if not selfEntity.queryTemp("firstPlayer", False ) :
			selfEntity.setTemp('firstPlayer', True )
			currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_FIRST_ENTER_COPY, params )

		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_ENTER_COPY, params )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		params["baseMailbox"] = baseMailbox
		currentStage = self.getCurrentStage( selfEntity )
		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_LEAVE_COPY, params )
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def onConditionChange( self, selfEntity, params ) :
		"""
		副本事件变化通知
		"""
		pass

	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		"""
		SpaceCopy.onTeleportReady( self, selfEntity, baseMailbox )
		baseMailbox.client.onOpenCopySpaceInterface( self.shownDetails() )

		params = {}
		params["baseMailbox"] = baseMailbox
		self.getCurrentStage( selfEntity ).doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_TELEPORT_READY, params )

	def copyTemplate_onMonsterDie( self, spaceBase, monsterID, monsterClassName, killerID ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡。
		此处并没有像玩家死亡事件那样，统一添加了怪物死亡的通知，原因有下：
		# 1.怪物死亡需通知副本的情况较多
		# 2.怪物死亡传入参数比较统一，做在这里方便后续继承使用。
		缺点就是一些副本的怪物死亡无需通知，不过如果后续继承于此的副本不希望做这些无用通知的话可以重载此接口。
		"""
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity and spaceEntity.isReal() :
			spaceEntity.getScript().copyTemplate_onMonsterDieRemote( spaceEntity, monsterID, monsterClassName, killerID )
		else :
			spaceBase.cell.remoteScriptCall( "copyTemplate_onMonsterDieRemote", ( monsterID, monsterClassName, killerID ) )

	def copyTemplate_onMonsterDieRemote( self, selfEntity, monsterID, monsterClassName, killerID ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""
		params = {}
		params["monsterID"] = monsterID
		params["monsterClassName"] = monsterClassName
		params["killerID"] = killerID
		self.getCurrentStage( selfEntity ).doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_MONSTER_DIE, params )

	def onRoleDie( self, role, killer ):
		"""
		<virtual method>

		#某role在该副本中死亡

		"""
		SpaceCopy.onRoleDie( self, role, killer )

		"""
		params = {}

		if not killer :
			params[ "killer" ] = None
		else :
			killerType = killer.getEntityType()
			if killer.isEntityType( csdefine.ENTITY_TYPE_PET ) :
				killer = killer.getOwner().entity

			params[ "killerType" ]	= killer.getEntityType()
			if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
				params[ "killerBase" ]			= killer.base
				params[ "playerName" ]			= killer.playerName
				params[ "killerCamp" ]			= killer.getCamp()
				params[ "killer_dbID" ]			= killer.databaseID
				params[ "killer_tong_dbID" ]	= killer.tong_dbID
			else :
				if hasattr( killer, "uname" ) :
					params[ "uname" ]			= killer.uname

		params[ "roleBase" ]		= role.base
		params[ "roleCamp" ]		= role.getCamp()
		params[ "rolePos" ]			= role.position
		params[ "role_dbID" ]		= role.databaseID
		params[ "role_tong_dbID" ]	= role.tong_dbID
		params[ "role_teamID" ]		= 0
		if role.getTeamMailbox() :
			params[ "role_teamID" ]	= role.getTeamMailbox().id

		spaceBase = role.getCurrentSpaceBase()
		if spaceBase :
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal() :
				spaceEntity.getScript().onRoleDieRemote( spaceEntity, params )
			else :
				spaceBase.cell.remoteScriptCall( "onRoleDieRemote", ( params, ) )

		# 放弃在此处统一添加玩家死亡事件通知副本的处理，原因 ：
		# 1.少数副本才需要玩家死亡通知
		# 2.不同的死亡通知传入参数差别较大，可能还有特殊参数，这里统一也不利于后续拓展。
		# 故这里仅提供一个添加玩家死亡事件的处理方式，供后续继承于此的副本参考。
		def onRoleDieRemote( selfEntity, params ) :
			self.getCurrentStage( selfEntity ).doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_ROLE_DIE, params )
		"""

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
		]
		"""
		# 默认显示的三项，其余有显示的需要，需要在另外定义shownDetails
		details = [ 0, 1, 3 ]
		# 加上配置定义的其他显示项
		details.extend(self.extendedShownDetails())
		return details

	#-------------------------------------------------------------
	# 下面的方法是在新的 addUserTimer 添加的回调方法。
	# 做此支持是为了支持 action 的延迟调用可配置。
	#-------------------------------------------------------------

	def onTimer( self, selfEntity, timerID, userArg, params ) :
		"""
		"""
		if userArg == Const.SPACE_TIMER_ARG_CLOSE_SPACE :		# 值为 -1，此处的timer并不想让配置人员配置，具体可去Const.py里去看说明。
			self.closeCopy( selfEntity )
		elif userArg > Const.SPACE_TIMER_USER_ARG_MAX :
			self.doCopyStageAction( selfEntity, params )
		else :
			self.getCurrentStage( selfEntity ).doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_TIMER, params )

	def doCopyStageAction( self, selfEntity, params ) :
		"""
		处理一个副本行为
		"""
		eventType		= params.get( "eventType" )
		eventInStage	= params.get( "eventInStage" )
		actionInEvent	= params.get( "actionInEvent" )
		stageInCopy		= params.get( "stageInCopy" )

		copyStage	= self._stages[ stageInCopy ]
		copyEvent	= copyStage.getEvent( eventType, eventInStage )
		copyAction	= copyEvent.getAction( actionInEvent )
		copyAction.do( selfEntity, params )

	def closeCopy( self, selfEntity, params = {} ) :
		"""
		# 副本关闭,该功能需在踢出所有玩家之后才能调用，现行做法是在踢出玩家后加一个 10 秒的timer
		# 故属于不想让配置人员知晓的timer，userArg 定义在Const.py中，为负值。
		# 该功能其实在底层 SpaceCopy 中有，但是那里使用了selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )处理,故这里重载覆盖。
		"""
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
		selfEntity.base.closeSpace( True )

	def extendedShownDetails(self):
		"""获取副本显示信息配置"""
		return self._spaceConfigInfo["extended_shown"]

	def getNonRepeatedPatrolGraphID( self, selfEntity, patrolGraphIdList, monsterClassName, monsterCell ) :
		"""
		从巡逻路径 patrolGraphIdList 中不重复获取一条，用于怪物 AIAction300
		"""
		if selfEntity.queryCopyShareTemp( SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS ) == None :
			selfEntity.setCopyShareTemp( SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS, patrolGraphIdList )
		
		originalGraphIDs = selfEntity.queryCopyShareTemp( SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS )
		key = SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS + monsterClassName
		if not selfEntity.queryCopyShareTemp( key ) :
			selfEntity.setCopyShareTemp( key, copy.deepcopy( originalGraphIDs ) )
		
		graphID = selfEntity.queryCopyShareTemp( key ).pop()
		monsterCell.remoteScriptCall( "onGetNonRepeatedPatrolGraphID", ( graphID, ) )


# ------------------------------------------------
# 副本共享数据 copyShareTempMapping key 的定义
# ------------------------------------------------

SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS							= "AIAction300_graphIDs_"				# 副本模板怪物 AIAction300 用于存储怪物共享的巡逻路径信息，为区别不同怪物，真实 key 为 "AIAction300_graphIDs_XXX"，XXX为怪物className



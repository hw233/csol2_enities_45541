# -*- coding: gb18030 -*-


from SlaveMonster import SlaveMonster
import Monster
import cschannel_msgs
import ShareTexts as ST
from FactionMgr import factionMgr
import ECBExtend
import BigWorld
import csdefine
import csconst
import csstatus
import Const
import Define
import random
from bwdebug import *
from VehicleHelper import getCurrVehicleID
from Domain_Fight import g_fightMgr


FIND_OWNER_SPEED = 5.0				#查找主人速度

STATES =   csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_FIGHT \
			  | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_TALK

class SlaveDart( SlaveMonster ):
	"""
	"""
	def __init__(self):
		"""
		"""
		INFO_MSG( "SlaveDart(%i) create! ownerName:%s!"%(self.id, self.ownerName ) )

		self.isRideOwner = False
		SlaveMonster.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_VEHICLE_DART
		self.topSpeedY = csconst.ROLE_TOP_SPEED_Y			#Y轴上的运动不作回拉处理

		# 镖车会被玩家骑上去（控制），因此必须一出生就能广播坐标信息。
		self.volatileInfo = (BigWorld.VOLATILE_ALWAYS, BigWorld.VOLATILE_ALWAYS, None, None)
		self.addTimer( 5000, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )						# 镖车5000死亡
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		BigWorld.globalData['DartManager'].buildDartRelation( self.ownerName, spaceLabel, self.base, self.getFaction() )

		if BigWorld.entities.has_key( self.ownerID ):
			INFO_MSG( "SlaveDart(%i) find owner just create!. ownerName:%s!"%(self.id, self.ownerName ) )
			player = BigWorld.entities[self.ownerID]
			player.queryDartInfo( self )
			self.setOwner( player )
		else:
			INFO_MSG( "SlaveDart(%i) can't find owner just create!. ownerName:%s!"%(self.id, self.ownerName ) )
			self.addTimer( FIND_OWNER_SPEED, 0, ECBExtend.INIT_DART_OWNER_CBID )									# 不能立刻找到主人，镖车5.0秒后，寻找主人
		self.enemyForTongDart = []			# 用来记录谁攻击过镖车
		self.addFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE )


	def onInitOwner( self, controllerID, userData ):
		"""
		回调的方式初始化镖车
		"""
		if BigWorld.entities.has_key( self.ownerID ):
			INFO_MSG( "SlaveDart(%i) spend few second to find owner success!. ownerName:%s!"%(self.id, self.ownerName ) )
			player = BigWorld.entities[self.ownerID]
			player.queryDartInfo( self )
			self.setOwner( player )

		else:
			self.addTimer( FIND_OWNER_SPEED, 0, ECBExtend.INIT_DART_OWNER_CBID )									#允许镖车不停的寻找主人
			INFO_MSG( "SlaveDart(%i) spend little second to find owner, but missed!. ownerName:%s!"%(self.id, self.ownerName ) )
			BigWorld.globalData['DartManager'].findOwnerByName( self.ownerName )

	def onReceiveDartInfo( self, dart_destNpcClassName, dart_questID, dart_eventIndex, dart_factionID, dart_level, dart_type  ):
		"""
		define method
		"""
		self.uname = factionMgr.getName( dart_factionID ) + cschannel_msgs.DART_INFO_4
		self.setTemp( "destNpcClassName", dart_destNpcClassName )			# 镖车存储到达的NPC ClassName
		self.setTemp( 'questID', dart_questID )								# 镖车存储这个任务的ID
		self.setTemp( 'eventIndex', dart_eventIndex )						# 镖车存储任务索引ID
		self.setTemp( "factionID", dart_factionID  )						# 镖车设置势力id
		self.setTemp('start_time',BigWorld.time() )							# 镖车生成时间
		self.setTemp('level', dart_level )
		self.setTemp('callMonstersTotal', 3 )								# 招怪个数
		self.setTemp('callMonstersTimeTotal', 5 )							# 招怪次数
		self.factionID = dart_factionID
		
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner is None:
			return
			
		self.position = owner.position
			
		if dart_type == 7:
			self.setTemp( "ownerTongDBID", owner.tong_dbID )
			self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_TONG_FRIEND, owner.tong_dbID )
		# owner.sendTongMemberQuest( dart_questID, self.id )	# CSOL-2118 不再发送任务邀请

	def mountEntity( self, srcEntityID, entityID, order ):
		"""
		Exposed Method
		"""
		return
		if BigWorld.entities.has_key( entityID ) and not self.isRideOwner and BigWorld.entities[entityID].isReal():
			player = BigWorld.entities[entityID]
			if player.vehicle or getCurrVehicleID( player ):
				player.client.onStatusMessage( csstatus.DART_FORBID_VEHICLE, "" )
				return
			if player.position.flatDistTo( self.position ) > 5.0:
				player.client.onStatusMessage( csstatus.DART_FORBID_TOO_FAR, "" )
				return
			if player.getState() != csdefine.ENTITY_STATE_FREE or self.getState() != csdefine.ENTITY_STATE_FREE:
				if self.getState() == csdefine.ENTITY_STATE_FIGHT:
					if len( self.enemyList ) == 0:
						self.state = 0
					needRemoveEnemyIDs = []
					for i in self.enemyList:
						entity = BigWorld.entities.get( i )
						if entity is None or entity.getState() != csdefine.ENTITY_STATE_FIGHT:
							needRemoveEnemyIDs.append( i )
					
					g_fightMgr.breakGroupEnemyRelationByIDs( self, needRemoveEnemyIDs )
					
				player.client.onStatusMessage( csstatus.DART_FORBID_CUR_THING, "" )
				return
			self.direction = player.direction
			player.position = self.position
			if not self.isMoving():
				self.planesAllClients( "setFilterYaw", ( player.direction[2], ) )
			self.controlledBy = player.base
			#上镖车时取消组队跟随
			if player.isTeamFollowing():
				player.cancelTeamFollow()
				
			player.boardVehicle( self.id )
			player.actCounterInc( STATES )					# 限制上镖车时不能进行的行为
			#player.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )
			# 通知entity上马
			self.planesAllClients( "onMountEntity", ( player.id, 0 ) )
			self.isRideOwner = True
			self.topSpeed = self.move_speed + csconst.ROLE_MOVE_SPEED_BIAS


	def disMountEntity( self, srcEntityID, playerID = 0 ):
		"""
		Exposed Method
		卸载entity
		@param entity		:	entity
		@type entity		:	mailBox
		@return None
		"""
		return
		if BigWorld.entities.has_key( srcEntityID ) and self.isRideOwner and srcEntityID == self.ownerID:
			self._disMountEntity()


	def _disMountEntity( self ):
		self.isRideOwner = False
		player = BigWorld.entities[self.ownerID]
		player.leaveDart( STATES, self.id )
		self.stopMoving()
		if player.isReal():
			player.stopMoving()
		self.controlledBy = None


	def beforeDie( self, killerID ):
		"""
		virtual method.
		"""
		if self.isRideOwner:
			self._disMountEntity()
		return True
		
	def dartMissionBrocad( self, killer, factionID ):
		"""
		运镖或劫镖成功的广播 by姜毅14:10 2009-7-31
		@param missionType : 任务类型
		@param missonnType : UINT8
		"""
		#self.family_grade
		killer.brocastMessageSlaveDart( factionID )

	def destoryDartEntity( self ):
		"""
		define method
		"""
		self.setTemp( 'dartQuestAbandoned', True )
		owner = self.getOwner()
		if owner:
			self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.getOwnerID() )
		self.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		if self.controlledBy is not None:
			self._disMountEntity()

	def closeVolatileInfo( self ):
		"""
		virtual method.
		关闭坐标信息传送功能。
		由于这个模块会被不同的entity调用，而某些entity可能会需要以不同
		的方式或时机关闭这个行为，因此这个接口允许玩家重载。
		"""
		# 主角重载此接口，但不做任何事情，等于不执行关闭坐标信息通知的行为
		# 如果关闭了，玩家（镖车）会漂移，因为玩家（被控制镖车）移动时并没有被通知要打开坐标信息通知功能。
		pass

	def openVolatileInfo( self ):
		"""
		virtual method.
		打开坐标信息传送功能
		由于这个模块会被不同的entity调用，而某些entity可能会需要以不同
		的方式或时机关闭这个行为，因此这个接口允许玩家重载。
		"""
		# 重载并覆盖此方法的功能，使镖车能正常表现。
		pass

	def onDestroy( self ):
		"""
		"""
		# 如果镖车上有玩家要先让玩家下镖车
		if self.isRideOwner:
			self._disMountEntity()
		# 如果有保镖要销毁保镖
		baoBiaoList = self.queryTemp( "DartMonsterIdList", [] )
		if len( baoBiaoList ) > 0:
			for i in baoBiaoList:
				if BigWorld.entities.has_key( i ):
					BigWorld.entities[i].destroy()
		SlaveMonster.onDestroy( self )

	def onRoleDestroy( self, entityID ):
		"""
		角色销毁前回调
		"""
		self.ownerID = 0
		self.setTemp( "ownerBaseMailBox", None )
		self.controlledBy = None
		if self.isRideOwner:
			self._disMountEntity()

	def isSlaveDart( self ):
		"""
		该骑乘是否是镖车
		"""
		return True

	def sendOwnerToSelf( self, baseMailbox ):
		"""
		传送镖车主人到镖车
		"""
		spaceName = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		baseMailbox.gotoSpace( spaceName, self.position, self.direction )

	def onCorpseDelayTimer( self, controllerID, userData ):
		"""
		MONSTER_CORPSE_DELAY_TIMER_CBID的callback函数；
		"""
		if not self.isDestroyed:
			playerName = self.ownerName
			if self.queryTemp( 'questFinish', False ) == False:
				INFO_MSG( "SlaveDart(%i) destroy on quest not finish! ownerName:%s!"%(self.id, self.ownerName ) )
				ownerID = self.getOwnerID()
				if BigWorld.entities.has_key( ownerID ):
					if not self.queryTemp('beKilled',False):
						BigWorld.entities[ownerID].statusMessage( csstatus.ROLE_QUEST_DART_TIME_OUT )
					if not self.queryTemp( 'dartQuestAbandoned', False ):
						BigWorld.entities[ownerID].handleDartFailed()
					BigWorld.entities[ownerID].selectTitle( ownerID, 0 )
				elif playerName != '':
					if not self.queryTemp('beKilled',False):
						BigWorld.globalData['DartManager'].addDartMessage( playerName, csstatus.ROLE_QUEST_DART_TIME_OUT, True )
			else:
				INFO_MSG( "SlaveDart(%i) destroy on quest finish! ownerName:%s!"%(self.id, self.ownerName ) )
			if not self.queryTemp( 'dartQuestAbandoned', False ):
				BigWorld.globalData['DartManager'].onReceiveDestoryCommand( playerName )
			self.destroy()


	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系

		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.Monster.queryRelation( self, entity )
			
		slaveOwner = BigWorld.entities.get( self.ownerID )

		if entity.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT:
			return csdefine.RELATION_NOFIGHT
			
		if entity.utype == csdefine.ENTITY_TYPE_ROLE:				# 设置帮会成员与帮会镖车为友好关系
			if self.queryTemp( "ownerTongDBID",0 ) != 0 and self.queryTemp( "ownerTongDBID" ) == entity.tong_dbID:
				return csdefine.RELATION_FRIEND

		if slaveOwner == None or not slaveOwner.isReal():
			return csdefine.RELATION_ANTAGONIZE

		return slaveOwner.queryRelation( entity )

	def updateTopSpeed( self ):
		"""
		virtual method = 0.

		更新移动速度限制(topSpeed)
		"""
		slaveOwner = BigWorld.entities.get( self.ownerID )
		if slaveOwner != None:
			if self.actionSign( csdefine.ACTION_FORBID_MOVE ) or slaveOwner.actionSign( csdefine.ACTION_FORBID_MOVE ):
				self.topSpeed = 0.001
			else:
				self.topSpeed = self.move_speed + csconst.ROLE_MOVE_SPEED_BIAS
	
	
	def updateOwnerID( self, ownerID ):
		"""
		define method
		"""
		self.ownerID = ownerID
	
	
	def updateOwnerBaseMailbox( self, ownerBaseMB ):
		"""
		define method
		角色重新上线，更新镖车对自身baseMailBox的引用
		"""
		self.setTemp( "ownerBaseMailBox", ownerBaseMB )
		self.updateOwnerID( ownerBaseMB.id )

	def setDartMember( self, entityID ):
		"""
		define method
		设置运镖成员
		"""
		dm = self.queryTemp( "dartMembers" )
		if dm is None:
			dm = {}
		dm[entityID] = 0
		self.setTemp( "dartMembers", dm )
		
	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		接受伤害。
		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能ID
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		if casterID not in self.enemyForTongDart:
			attacker = BigWorld.entities.get( casterID )
			if attacker and attacker.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				self.enemyForTongDart.append( casterID )
		Monster.Monster.receiveDamage( self, casterID, skillID, damageType, damage )
		
	def getRelationEntity( self ):
		"""
		获取关系判定的真实entity
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		else:
			return owner
		
	def queryCombatRelation( self, entity ):
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner:
			return owner.queryCombatRelation( entity )
		else:
			return csdefine.RELATION_ANTAGONIZE
		
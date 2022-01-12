# -*- coding: gb18030 -*-

import csdefine
import ECBExtend
import csconst
import Const
import csstatus
import cschannel_msgs
import time
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam

LEAVE_GATE = 10001
CLOSE_SPACE = 10002
SPACE_LAST_TIME = 60 * 30

class SpaceCopyDestinyTrans( SpaceCopyTeam ):
	"""
	天命轮回副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )
		self.bossID = ""

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。
		
		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		SpaceCopyTeam.onLoadEntityProperties_( self, section )
		
		if section["Space"].has_key( "bossID"):
			self.bossID = section[ "Space" ][ "bossID" ].readString( "className" )

	def packedDomainData( self, entity ):
		"""
		@param player:	创建者实例
		"""
		data = { "dbID" 			: entity.databaseID,
				 "type" 			: entity.query( "destityTransSpaceType", None ),
				 "spaceKey"		: entity.databaseID,
				}
		if entity.teamMailbox:
			data[ "teamID" ] = entity.teamMailbox.id
			data[ "captainDBID" ] = entity.getTeamCaptainDBID()
			data[ "membersDBID" ] = entity.getTeamMemberDBIDs()
			if csdefine.DESTINY_ENTER_GATE_TEAM == entity.query( "destityTransSpaceType", None ):
				data["spaceKey"] = entity.getTeamCaptainDBID()
		return data

	def getCaptainLevel( self, baseMailbox ):
		"""
		根据玩家MailBox获得队长等级
		"""
		entity = BigWorld.entities.get( baseMailbox.id )
		if not entity:
			return
		level = entity.level
		if entity.teamMailbox:
			if entity.isTeamCaptain():
				level = entity.level
			else:
				captain = entity.getTeamCaptain()
				if captain:
					lelve = captain.level
		
		return level

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		
		type = entity.query( "destityTransSpaceType", None )
		if type == csdefine.DESTINY_ENTER_GATE_SINGLE:
			level = entity.level
		else:
			level = self.getCaptainLevel( entity )

		packDict[ "level" ] = entity.level
		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.onEnterDestinyTransGate()
		baseMailbox.client.closeBoardInterface( 0 )		# 关闭棋盘界面
		if not selfEntity.queryTemp( "tempHaveCome", False ):				# 只设置一次
			level = params[ "level" ]
			selfEntity.base.createSpawnEntities( { "level" : level } )		# 刷出怪物
			selfEntity.setTemp( "tempHaveCome", True )
			selfEntity.setTemp( "copyStartTime", time.time() )				# 副本开始时间
			selfEntity.addTimer( SPACE_LAST_TIME, 0.0, CLOSE_SPACE )
		
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
		baseMailbox.cell.setTemp( "last_space_type",  self.getSpaceType() )
		baseMailbox.cell.onLeaveDestinyTransGate()

	def onRoleDie( self, role, killer ):
		"""
		玩家死亡
		"""
		if role.queryTemp( "livePoint", 0  ) <= 0:
			# 传出副本
			role.client.desTrans_msgs( csdefine.DESTINY_TRANS_FAILED_GATE )
			role.addTimer( 3.0, 0, ECBExtend.WAIT_ROLE_REVIVE_PRE_SPACE_CBID )
			return
		
		# 等待点击按钮复活
		autoReviveTimer= role.addTimer( 10.0, 0, ECBExtend.ROLE_UESE_LIVE_POINT_REVIE_CBID )
		role.setTemp( "autoReviveTimer", autoReviveTimer )

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""	
		if monsterClassName != self.bossID:
			selfEntity.monsterCount -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.monsterCount  )
		else:
			selfEntity.bossCount -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.bossCount )
		
		if selfEntity.bossCount <= 0 and selfEntity.monsterCount <= 0 :
			self.gatePassed( selfEntity )

	def gatePassed( self, selfEntity ):
		"""
		通关
		"""
		for e in selfEntity._players:
			e.cell.onPassedGate()

		selfEntity.addTimer( 3.0, 0.0, LEAVE_GATE )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )
		if userArg == LEAVE_GATE:
			self.roleLeaveGate( selfEntity )
		
		if userArg == CLOSE_SPACE:
			self.closeSpace( selfEntity )

	def roleLeaveGate( self, selfEntity ):
		"""
		玩家离开关卡
		"""
		for e in selfEntity._players:
			role = BigWorld.entities.get( e.id )
			if role:
				role.gotoForetime()
			else:
				e.cell.gotoForetime()

	def closeSpace( self, selfEntity ):
		"""
		关闭副本
		"""
		for e in selfEntity._players:
			if not ( selfEntity.bossCount <= 0 and selfEntity.monsterCount <= 0 ):
				e.cell.onFailedGate()
			
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()
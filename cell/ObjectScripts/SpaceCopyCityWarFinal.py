# -*- coding: gb18030 -*-

import re
import csdefine
import Const
import csstatus
from bwdebug import *
from SpaceCopyTemplate import SpaceCopyTemplate
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess

BATTLE_PREPARE_TIME				 = 60 * 2
WAIT_BATTLE_FIELD_RESET_TIME	 = 60 * 3
KICK_PLAYER_TIME				 = 30
BATTLE_FIELD_RESET_TIME			 = 60
BASE_ON_OCCUPIED_NOTICE_TIMES	 = 3

PRE_CONTENT					 = 20140213
BATTLE_FIELD_RESET			 = 20140214
KICK_PLAYER_TIMER			 = 20140215
STATUS_MESSAGE_TIMER		 = 20140224

# 传入位置
DEFEND_TONG_ENTER_POS			= 1		# 攻方传入点
DEFEND_LEAGUES_ENTER_POS		= 2		# 攻方联盟传入点
ATTACK_TONG_ENTER_POS			= 3		# 守方传入点
ATTACK_LEFT_LEAGUES_ENTER_POS	= 4		# 守方联盟1传入点
ATTACK_RIGHT_LEAGUES_ENTER_POS	= 5		# 守方联盟2传入点

class CCPrepareProcess( CopyContent ):
	"""
	2分钟准备时间
	"""
	def __init__( self ):
		self.key = "prepareProcess"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		内容执行
		"""
		spaceEntity.addTimer( BATTLE_PREPARE_TIME, 0, NEXT_CONTENT )
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )

	def endContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.destroyLightWall( )
		CopyContent.endContent( self, spaceEntity )

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色进入
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )			# 强制所有玩家进入和平模式

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		baseMailbox.cell.setSysPKMode( 0 )

class CCCombatProcess( CopyContent ):
	"""
	战斗时间
	"""
	def __init__( self ):
		self.key = "combatProcess"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		内容执行
		"""
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_LEAGUE )

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色进入
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_LEAGUE )			# 强制所有玩家进入联盟模式

	def onConditionChange( self, spaceEntity, params ):
		"""
		一个条件发生变化，通知内容
		"""
		spaceEntity.resetTimer =  spaceEntity.addTimer( WAIT_BATTLE_FIELD_RESET_TIME, 0, BATTLE_FIELD_RESET )

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		CopyContent.onTimer( self, spaceEntity, id, userArg )
		if userArg == BATTLE_FIELD_RESET:
			spaceEntity.cancel(  spaceEntity.resetTimer )
			spaceEntity.resetTimer = 0
			self.onBattleFieldResetTimer( spaceEntity )

	def onBattleFieldResetTimer( self, spaceEntity ):
		"""
		战场重置timer
		"""
		belong = spaceEntity.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_HEROMONU ][0].values()[ 0 ]
		if belong != csdefine.CITY_WAR_FINAL_FACTION_DEFEND:
			self.endContent( spaceEntity )

class CCBattleFieldReset( CopyContent ):
	"""
	战场重置
	"""
	def __init__( self ):
		self.key = "battleFieldReset"
		self.val = 1

	def beginContent( self, spaceEntity ):
		"""
		内容开始
		添加战场重置Timer
		"""
		spaceEntity.addTimer( BATTLE_FIELD_RESET_TIME, 0, PRE_CONTENT )

	def onContent( self, spaceEntity ):
		"""
		内容执行
		通知副本战场重置
		"""
		spaceEntity.setTemp( "BATTLE_FIELD_RESET", True )	# 停止计算积分
		spaceEntity.battleFieldReset()
		spaceEntity.spawnLightWall()

	def endContent( self, spaceEntity ):
		"""
		内容结束,执行上一个内容
		"""
		spaceEntity.destroyLightWall()
		spaceEntity.removeTemp( "BATTLE_FIELD_RESET" )
		spaceEntity.getScript().doPreContent( spaceEntity )

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色进入
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_LEAGUE )			# 强制所有玩家进入联盟模式

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		CopyContent.onTimer( self, spaceEntity, id, userArg )
		if userArg == PRE_CONTENT:
			self.endContent( spaceEntity )

class SpaceCopyCityWarFinal( SpaceCopyTemplate ):
	"""
	帮会夺城战决赛
	"""
	def __init__( self ):
		SpaceCopyTemplate.__init__( self )

	def initContent( self ):
		"""
		"""
		self.contents.append( CCPrepareProcess() )
		self.contents.append( CCCombatProcess() )
		self.contents.append( CCBattleFieldReset() )
		self.contents.append( CCKickPlayersProcess() )

	def load( self, section ):
		"""
		从配置中加载数据
		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTemplate.load( self, section )
		
		spaceData = section[ "Space" ]
		
		# 守城帮会进入位置
		defend_tong_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["defend_tong_enterPos"].asString ) )
		defend_league_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["defend_league_enterPos"].asString ) )
		
		# 攻城帮会进入位置
		attack_tong_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_tong_enterPos"].asString ) )
		attack_leftLeague_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_leftLeague_enterPos"].asString ) )
		attack_rightLeague_enterPos = eval( re.sub( "\s*;\s*|\s+", ",", spaceData["attack_rightLeague_enterPos"].asString ) )
		
		self.enterPosMapping = { 1: defend_tong_enterPos,
								 2: defend_league_enterPos,
								 3: attack_tong_enterPos,
								 4: attack_leftLeague_enterPos,
								 5: attack_rightLeague_enterPos,
								}

	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		"""
		dict = {}
		dict[ "tongDBID" ] = entity.tong_dbID
		dict[ "camp" ] = entity.getCamp()
		dict[ "roleDBID" ] = entity.databaseID
		dict[ "roleName" ] = entity.getName()
		dict[ "spaceName" ] = entity.spaceType
		return dict

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "roleDBID" ] = entity.databaseID
		packDict[ "roleName" ] = entity.getName()
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		获取entity离开时，向所在的space发送离开该space消息的额外参数；
		@param entity: 想要向space entity发送离开该space消息(onLeave())的entity（通常为玩家）
		@return: dict，返回要离开的space所需要的entity数据。如，有些space可能会需要比较离开的玩家名字与当前记录的玩家的名字，这里就需要返回玩家的playerName属性
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnLeave( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "roleName" ] = entity.getName()
		packDict[ "databaseID" ] = entity.databaseID
		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		tongDBID = params[ "tongDBID" ]
		belong = selfEntity.getTongBelong( tongDBID )
		self.setRoleBelong( baseMailbox, belong )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.tong_onLeaveCityWarSpace()
		baseMailbox.cell.setSysPKMode( 0 )										# 解除默认sysPKMode

	def setRoleBelong( self, baseMailbox, belong ):
		"""
		设置玩家归属
		"""
		baseMailbox.cell.setTemp( "CITY_WAR_FINAL_BELONG", belong )

	def resetTongInfos( self, selfEntity ):
		"""
		重置参战帮会信息
		"""
		newTongInfos = {}
		newTongInfos[ "defend" ] = {}			# 守城方
		newTongInfos[ "attack"] = {}			# 攻城方
		
		for key, item in selfEntity.tongInfos.iteritems():
			# 守城方将变为攻城方
			if key == "defend":
				for tongDBID in item.keys():
					maxNum = item[ tongDBID ][ "maxNum" ]
					if tongDBID == selfEntity.attack:
						enterPos = ATTACK_TONG_ENTER_POS
					else:
						enterPos = ATTACK_LEFT_LEAGUES_ENTER_POS
					newTongInfos[ "attack"][ tongDBID ] = { "maxNum": maxNum, "enterPos":  enterPos }
			# 攻城方变成守城方
			elif key == "attack":
				for tongDBID in item.keys():
					maxNum = item[ tongDBID ][ "maxNum"]
					if tongDBID == selfEntity.defend:
						enterPos = DEFEND_TONG_ENTER_POS
					else:
						enterPos = DEFEND_LEAGUES_ENTER_POS
					newTongInfos[ "defend" ][ tongDBID ] = { "maxNum": maxNum, "enterPos": enterPos }
		selfEntity.tongInfos = newTongInfos

	def getTongBasePos( self, selfEntity, tongDBID ):
		"""
		获得帮会的大本营位置
		"""
		for key, item in selfEntity.tongInfos.iteritems():
			for dbid in item.keys():
				if dbid == tongDBID:
					enterPosNo = item[ dbid ]["enterPos"]
					break
		enterPos = self.enterPosMapping[ enterPosNo ]
		pos, dir = enterPos[ :3 ], enterPos[ 3 :]
		return pos, dir

	def teleportPlayerToBelongBase( self, selfEntity ):
		"""
		战场重置时将所有玩家传送到本方大本营
		"""
		for tongDBID, info in selfEntity.warInfos.infos.iteritems():
			belong = selfEntity.getTongBelong( tongDBID )
			pos, dir = self.getTongBasePos( selfEntity, tongDBID )
			for roleDBID, member in info.members.iteritems():
				roleMB = member.mailBox
				self.setRoleBelong( roleMB, belong )
				
				role = BigWorld.entities.get( roleMB.id )
				if role:
					role.teleportToSpace( pos, dir, selfEntity, selfEntity.spaceID )
				else:
					role.cell.teleportToSpace( pos, dir, selfEntity, selfEntity.spaceID )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.
		某role在该副本中死亡
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Role %i kill a enemy." % role.id )
		if not killer:		# 找不到杀人者，忽略
			return

		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" :
				return
			killer = owner.entity

		if killer.getEntityType() != csdefine.ENTITY_TYPE_ROLE:
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.belong, 0, role.tong_dbID, role.databaseID )
		else:
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.tong_dbID, killer.databaseID, role.tong_dbID, role.databaseID )

	def onRoleRelive( self, selfEntity, mailbox, tongDBID ):
		"""
		战场复活
		"""
		pos, dir = self.getTongBasePos( selfEntity, tongDBID )
		mailbox.cell.tong_onCityWarFinalReliveCB( pos, dir, selfEntity, selfEntity.spaceID )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		覆盖底层的onTimer()处理机制
		"""
		SpaceCopyTemplate.onTimer( self, selfEntity, id, userArg )
		if userArg == KICK_PLAYER_TIMER:
			self.doLastContent( selfEntity )
		elif userArg == STATUS_MESSAGE_TIMER:
			self.onTimerStatusMessage( selfEntity, id )

	def closeSpace( self, selfEntity ):
		"""
		关闭副本( 执行最后剔除玩家的步骤 )
		"""
		selfEntity.addTimer( KICK_PLAYER_TIME, 0, KICK_PLAYER_TIMER )
		self.statusMessageAllPlayer( selfEntity, csstatus.TONG_CITY_WAR_FINAL_KICK_PLAYER, str( ( 30, ) ) )

	def doPreContent( self, selfEntity ):
		"""
		执行上一个阶段
		"""
		index = selfEntity.queryTemp( "contentIndex", -1 )
		index -= 1
		selfEntity.setTemp( "contentIndex", index )
		if len( self.contents ) > index:
			self.contents[index].doContent( selfEntity )
			INFO_MSG( "TONG_CITY_WAR_FINAL: Space %s begin to do content %s " % ( selfEntity.className, self.contents[index].key ) )

	def doLastContent( self, selfEntity ):
		"""
		执行最后的阶段
		"""
		index = len( self.contents ) -1
		selfEntity.setTemp( "contentIndex", index  )
		self.contents[index].doContent( selfEntity )

	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		通知所有人 指定的信息( 每隔10秒提示一次，共3次 )
		"""
		isFind = False
		for msg in selfEntity.msgs:
			if msg[ "msgKey" ] == ( msgKey, args ):
				isFind = True
				msg[ "times" ] += 1
				if msg[ "times" ] > BASE_ON_OCCUPIED_NOTICE_TIMES:		# 大于已经提示的次数
					selfEntity.msgs.remove( msg ) 
					return
				msg[ "timerID" ] = selfEntity.addTimer( 10, 0, STATUS_MESSAGE_TIMER )
				break
		
		if not isFind:
			dict = {}
			dict[ "msgKey" ] = ( msgKey, args )
			dict[ "times" ] = 1
			dict[ "timerID" ] = selfEntity.addTimer( 10, 0, STATUS_MESSAGE_TIMER )
			selfEntity.msgs.append( dict )
		
		for e in selfEntity._players:
			e.client.onStatusMessage( msgKey, *args )

	def onTimerStatusMessage( self, selfEntity, id ):
		"""
		Timer通知播放提示信息
		"""
		for msg in selfEntity.msgs:
			if msg[ "timerID" ] == id:
				msgKey = msg[ "msgKey"]
				self.statusMessageAllPlayer( selfEntity, msgKey[0], *msgKey[1] ) 
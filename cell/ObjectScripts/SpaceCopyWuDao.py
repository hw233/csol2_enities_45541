# -*- coding: gb18030 -*-
#
#$Id:$

import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
from SpaceCopyTeam import SpaceCopyTeam

CLOSE_COPY				= 3	  # 标记关闭副本
CLOSE_WUDAO				= 4   # 关闭武道大会

class SpaceCopyWuDao( SpaceCopyTeam ):
	"""
	武道大会副本空间
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True

	def load( self, section ):
		"""
		从配置中加载数据

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )

		# 进入者最小级别限制
		self.enterLimitLevel = section[ "Space" ][ "enterLimitLevel" ].asInt


	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'roleDBID' : entity.databaseID, "level": entity.level, "playerName":entity.playerName }

	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		if entity.level < self.enterLimitLevel:
			return csstatus.WU_DAO_NO_WAR_LEVEL

		return csstatus.SPACE_OK

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		packDict[ "playerDBID" ] = entity.databaseID
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		# 打包玩家离开的数
		packDict = SpaceCopyTeam.packedSpaceDataOnLeave( self, entity )
		packDict[ "state" ] = entity.getState()
		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		playerDBID = params["playerDBID"]
		if playerDBID not in selfEntity.databaseIDList:
			selfEntity.databaseIDList.append( playerDBID )

		player = baseMailbox.cell
		player.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# 进入武道大会，免战

		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[ baseMailbox.id  ]
			player.setTemp( "wudao_sclass", selfEntity.className )	# 设置玩家所在副本的脚本名字，以便玩家和副本不在同一个server时可以找回副本
			player.setTemp( "lastPkMode", player.pkMode )

		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )	#设置为和平模式
		baseMailbox.cell.lockPkMode()										#锁定pk模式，不能设置

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		if not selfEntity.hasClearNoFight:		# 如果没有清除过角色的免战效果
			baseMailbox.cell.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
			return

		baseMailbox.cell.setSysPKMode( 0 )
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[ baseMailbox.id  ]
			player.unLockPkMode()		# 解锁pk模式
			player.setPkMode( baseMailbox.id, player.queryTemp( "lastPkMode" ) )	# 恢复原先pkMode
		else:
			baseMailbox.cell.unLockPkMode()		# 解锁pk模式
			baseMailbox.cell.setPkMode( baseMailbox.id, csdefine.PK_CONTROL_PROTECT_RIGHTFUL )	# 恢复到善意模式

		if not selfEntity.queryTemp( "hasCloseWuDao" ):		# 如果武道大会副本没有关闭，则是中途退出副本
			if len( selfEntity._players ) == 1: 			# 副本中另外一个人，直接获胜
				selfEntity._players[0].client.onStatusMessage( csstatus.WU_DAO_OUT, "" )
				selfEntity._players[0].onWuDaoOver( selfEntity._players[0], 1 ) # 通知武道大会管理器，获胜方
				self.closeWuDao( selfEntity ) # 关闭武道大会

		if params[ "state" ] == csdefine.ENTITY_STATE_DEAD:
			baseMailbox.cell.reviveActivity() # 空血空蓝复活

	def onPlayerDied( self, selfEntity, killer, killerDBID, beKiller, beKillerDBID ):
		"""
		玩家死亡
		"""
		for e in selfEntity._players:
			e.client.onStatusMessage( csstatus.WU_DAO_LEAVA, "" )

		self.onWuDaoOver( killer.base, killerDBID, killer.level, 1 )
		self.onWuDaoOver( beKiller.base, beKillerDBID, beKiller.level, 0 )
		selfEntity.databaseIDList.remove( beKillerDBID )
		killer.clearBuff( [csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT] )

		selfEntity.setTemp( "hasCloseWuDao", True )		# 设置已经关闭武道大会，防止玩家死亡后，先在CLOSE_WUDAO前退出副本
		selfEntity.addTimer( 10, 0, CLOSE_WUDAO )		# 10秒后调用claseWuDao

	def onWuDaoOver( self, playerBase, dbid, level, result = 0 ):
		"""
		武道大会一场比赛结束了，通知管理器
		"""
		BigWorld.globalData[ "WuDaoMgr" ].onWuDaoOverFromSpace( playerBase, dbid, level, result )	# 通知武道大会管理器，某场战斗结果

	def closeWuDao( self, selfEntity ):
		"""
		出副本，关闭武道大会
		"""
		selfEntity.setTemp( "hasCloseWuDao", True )		# 设置已经关闭武道大会

		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].challengeActivityTransmit( csconst.TRANSMIT_TYPE_WUDAO )
			else:
				e.cell.challengeActivityTransmit( csconst.TRANSMIT_TYPE_WUDAO )

		selfEntity.addTimer( 10.0, 0.0, CLOSE_COPY )

	def clearNoFight( self , selfEntity ):
		for e in  selfEntity._players:
			# 设置PK模式
			e.cell.unLockPkMode()
			e.cell.setPkMode( e.id, csdefine.PK_CONTROL_PROTECT_NONE )
			e.cell.lockPkMode()
			# 清除免战
			e.cell.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
			# 广播玩家开打
			e.client.onStatusMessage( csstatus.WU_DAO_CLEAR_NO_FIGHT, "" )

		selfEntity.hasClearNoFight = True		# 标记已经清除过角色的免战效果

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		if not killer:	# 没找到杀人者，非正常死亡不处理，直接返回
			DEBUG_MSG( "player( %s ) has been killed,can't find killer." % role.getName() )
			return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if killer.getState() == csdefine.ENTITY_STATE_DEAD:		# 如果杀人者已经死亡，则返回
			return

		role.statusMessage( csstatus.WU_DAO_LOSE )
		killer.statusMessage( csstatus.WU_DAO_WIN )

		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			spaceBase = role.getCurrentSpaceBase()
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal():
				self.onPlayerDied( spaceEntity, killer, killer.databaseID, role, role.databaseID )
			else:
				spaceBase.cell.remoteScriptCall( "onPlayerDied", ( killer, killer.databaseID, role, role.databaseID ) )

		role.client.onStatusMessage( csstatus.WU_DAO_JOIN_REWARD, "" )

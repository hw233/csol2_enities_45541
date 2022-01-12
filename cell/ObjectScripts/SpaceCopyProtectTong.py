# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPotential.py,v 1.17 2008-06-23 01:32:24 kebiao Exp $

"""
"""
import BigWorld
import ShareTexts as ST
import csstatus
import csdefine
import random
import csconst
import ECBExtend
import Love3
import time
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam
from ObjectScripts.GameObjectFactory import g_objFactory


class SpaceCopyProtectTong( SpaceCopyTeam ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )
		self._spaceType = csdefine.SPACE_TYPE_PROTECT_TONG

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTeam.load( self, section )
		self._posData = {}
		self.bossPoint = []
		self.monsterInfo = []	# like as [ [boss编号,小怪编号], ... ]
		
		self.setEntityProperty( "uname", section.readString( "spaceName" ) )					# 中文名称
		
		for item in section[ "Space" ]["monsterInfo"].values():
			self.monsterInfo.append( [ monsterID for monsterID in item.asString.split(";")] )
			
		for idx, item in enumerate( section[ "Space" ][ "monsterPoint" ].values() ):
			ls = []
			self._posData[ idx ] = ls
			for point in item.values():
				ls.append( ( eval( point["pos"].asString ), eval( point["direction"].asString ), eval( point["randomWalkRange"].asString ) ) )

		self.bossPoint = [ ( eval( point["pos"].asString ), eval( point["direction"].asString ), eval( point["randomWalkRange"].asString ) ) for point in section["Space"]["BossPoint"].values() ]
		point = section[ "Space" ][ "doorPoint" ]
		self.doorPoint = ( eval( point["pos"].asString ), point["radius"].asFloat )

		point = section[ "Space" ][ "playerEnterPoint" ]
		self.playerEnterPoint = ( eval( point[ "pos" ].asString ), eval( point[ "direction" ].asString ) )

	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'dbID' : entity.popTemp( "enterSpaceID" ) }

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.isTeamCaptain():
			tongDBID, enterPosition, enterDirection = entity.popTemp( "ProtectTongData", ( BigWorld.globalData[ "AS_ProtectTong" ][0], (0,0,0), (0, 0, 0 ) ) )
			packDict[ "playerLevel" ] = entity.level
			packDict[ "spaceName" ] = entity.popTemp( "currentSpaceName", 0 )
			packDict[ "enterPosition" ] = enterPosition
			packDict[ "enterDirection" ] = enterDirection
			packDict[ "isTongMember" ] = entity.tong_dbID == BigWorld.globalData[ "AS_ProtectTong" ][0]
			packDict[ "duizhang" ] = entity.getName()
			
		return packDict

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		SpaceCopyTeam.initEntity( self, selfEntity )
		selfEntity.setTemp( "currMonsterTotal", 0 )		# 当前还剩多少怪物在副本
		BigWorld.globalData[ "ProtectTong" ].onRegisterProtectTongSpace( selfEntity.base )
		selfEntity.params[ "tongDBID" ] = BigWorld.globalData[ "AS_ProtectTong" ][0]

		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, self.getName() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, -1 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )

	def addCastMonsterCount( self, selfEntity, count ):
		"""
		currMonsterTotal: 当前还剩多少怪物在副本
		"""
		selfEntity.setTemp( "currMonsterTotal", selfEntity.queryTemp( "currMonsterTotal" ) + count )

	def getCurrentMonsterCount( self, selfEntity ):
		return selfEntity.queryTemp( "currMonsterTotal" )

	def castAllMonster( self, selfEntity, playerLevel ):
		"""
		在每个点刷出所有的怪物
		"""

		slist = []
		for lst in self._posData.itervalues():
			slist.extend( lst )

		monsterCount = len( slist )
		isTongMember = selfEntity.queryTemp( "isTongMember" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, monsterCount )
		for x in xrange( monsterCount ):
			idx = random.randint( 0, len( slist ) - 1 )
			posData = slist.pop( idx )
			monsterID = self.monsterInfo[ random.randint( 0, len( self.monsterInfo ) - 1 ) ][ 1 ]
			monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className, "isTongMember" : isTongMember } }
			monInfo[ "spawnPos" ] = posData[0]
			monInfo[ "randomWalkRange" ] = posData[2]
			monInfo[ "level" ] = playerLevel
			selfEntity.createNPCObject( monsterID, posData[0], posData[1], monInfo )
			self.addCastMonsterCount( selfEntity, 1 )

	def castBoss( self, selfEntity, level ):
		"""
		刷出boss
		"""
		isTongMember = selfEntity.queryTemp( "isTongMember" )
		bossID = self.monsterInfo[ random.randint( 0, len( self.monsterInfo ) - 1 ) ][ 0 ]
		posData = self.bossPoint[ random.randint( 0, len( self.bossPoint ) - 1 ) ]
		monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className, "isTongMember" : isTongMember } }
		monInfo[ "spawnPos" ] = posData[0]
		monInfo[ "randomWalkRange" ] = posData[1][2]
		monInfo[ "level" ] = level
		selfEntity.createNPCObject( bossID, posData[0], posData[1], monInfo )
		self.addCastMonsterCount( selfEntity, 1 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )
		statusID = csstatus.PROTECT_TONG_BOSS
		if BigWorld.globalData[ "AS_ProtectTong" ][2] == csdefine.PROTECT_TONG_MID_AUTUMN:
			statusID = csstatus.PROTECT_TONG_AUTUMN_BOSS
		self.statusMessageAllPlayer( selfEntity, statusID )

	def onProtectTongEnd( self, selfEntity, isTimeout ):
		"""
		活动结束
		"""
		if isTimeout:
			if selfEntity.queryTemp( "OverProtectTong", -1 ) == True:
				return
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
			BigWorld.globalData[ "ProtectTong" ].protectTongOver( selfEntity.queryTemp("duizhang"), BigWorld.globalData[ "AS_ProtectTong" ][2] )
			# 开始倒计时30秒关闭副本
			selfEntity.setTemp( "leaveTimer", selfEntity.addTimer( 20, 0, 0  ) )
			self.customCreateDoor( selfEntity, selfEntity.queryTemp("spaceName"), selfEntity.queryTemp("enterPosition"), selfEntity.queryTemp("enterDirection") )
			self.statusMessageAllPlayer( selfEntity, csstatus.PROTECT_TONG_OVER )
		else:
			if selfEntity.queryTemp( "OverProtectTong", -1 ) == False:
				return

			self.allMemberLeaveSpace( selfEntity )

		selfEntity.setTemp( "OverProtectTong", isTimeout )

	def allMemberLeaveSpace( self, selfEntity ):
		"""
		所有成员都应该离开副本
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].setTemp( "enter_tong_territory_datas", { "enterOtherTong" : selfEntity.params[ "tongDBID" ] } )
				BigWorld.entities[ e.id ].gotoSpace( "fu_ben_bang_hui_ling_di", selfEntity.queryTemp( "enterPosition" ), selfEntity.queryTemp( "enterDirection" ) )

			else:
				e.cell.setTemp( "enter_tong_territory_datas", { "enterOtherTong" : selfEntity.params[ "tongDBID" ] } )
				e.cell.gotoSpace( "fu_ben_bang_hui_ling_di", selfEntity.queryTemp( "enterPosition" ), selfEntity.queryTemp( "enterDirection" ) )

		# 开始倒计时30秒关闭副本
		selfEntity.setTemp( "destroyTimer", selfEntity.addTimer( 10, 0, 0  ) )

	def onProtectTongMonsterDie( self, selfEntity, position ):
		"""
		一个怪物死亡了
		"""
		# 设置当前怪物数量
		currMonsterTotal = selfEntity.queryTemp( "currMonsterTotal" )
		selfEntity.setTemp( "currMonsterTotal", currMonsterTotal - 1 )

		if selfEntity.queryTemp( "castBossWaitTimeID" ) == None:
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, currMonsterTotal - 1 )
			if currMonsterTotal <= 1:
				selfEntity.setTemp( "castBossWaitTimeID", selfEntity.addTimer( 10, 0, 0 ) )
		else:
			if currMonsterTotal <= 1:
				self.onProtectTongEnd( selfEntity, True )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if selfEntity.queryTemp( "destroyTimer", 0 ) == id:
			selfEntity.base.closeSpace( True )
		elif selfEntity.queryTemp( "castBossWaitTimeID", 0 ) == id:
			selfEntity.cancel( selfEntity.queryTemp( "castBossWaitTimeID", 0 ) )
			selfEntity.setTemp( "castBossWaitTimeID", -100 )
			self.castBoss( selfEntity, selfEntity.queryTemp( "playerLevel", 10 ) )
		elif selfEntity.queryTemp( "leaveTimer", 0 ) == id:
			self.allMemberLeaveSpace( selfEntity )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		# 队长第一次进入则刷出所有的怪物
		if not selfEntity.queryTemp( "playerLevel" ) and params.has_key( "playerLevel" ):
			selfEntity.setTemp( "playerLevel", params[ "playerLevel" ] )
			selfEntity.setTemp( "spaceName", params[ "spaceName" ] )
			selfEntity.setTemp( "enterPosition", params[ "enterPosition" ] )
			selfEntity.setTemp( "enterDirection", params[ "enterDirection" ] )
			selfEntity.setTemp( "duizhang", params[ "duizhang" ] )
			selfEntity.setTemp( "isTongMember", params[ "isTongMember" ] )
			self.castAllMonster( selfEntity, params[ "playerLevel" ] )

		#baseMailbox.cell.setTemp( "ProtectTongData", ( selfEntity.params[ "tongDBID" ], selfEntity.queryTemp( "enterPosition" ), selfEntity.queryTemp( "enterDirection" ) ) )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		通知所有人 指定的信息
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				p = BigWorld.entities[ e.id ]
				p.statusMessage( msgKey, *args )
			else:
				ERROR_MSG( "player %i not found" % e.id )

	def createDoor( self, selfEntity ):
		"""
		创建Door
		"""
		pass

	def customCreateDoor( self, selfEntity, spaceName, destPosition, destDirection ):
		"""
		创建Door
		"""
		doordict = {"name" : "haha"}
		doordict["radius"] = self.doorPoint[1]
		doordict["destSpace"] = spaceName
		doordict["destPosition"] = destPosition
		doordict["destDirection"] = destDirection
		doordict["modelNumber"] = None
		doordict["modelScale"] = 25
		BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, self.doorPoint[0], (0, 0, 0), doordict )

	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		tongDBID, enterPosition, enterDirection = playerEntity.popTemp( "ProtectTongData", \
																( BigWorld.globalData[ "AS_ProtectTong" ][0], (0,0,0), (0, 0, 0 ) ) )

		playerEntity.setTemp( "enter_tong_territory_datas", { "enterOtherTong" : tongDBID } )

		if playerEntity.queryTemp( 'leaveSpaceTime', 0 ) == 0:
			playerEntity.leaveTeamTimer = playerEntity.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
		playerEntity.setTemp( "leaveSpaceTime", 5 )
		playerEntity.client.onLeaveTeamInSpecialSpace( 5 )

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		队员离开队伍处理
		"""
		tongDBID, enterPosition, enterDirection = playerEntity.popTemp( "ProtectTongData", \
																( BigWorld.globalData[ "AS_ProtectTong" ][0], (0,0,0), (0, 0, 0 ) ) )

		if not playerEntity.isInTeam():
			playerEntity.gotoSpace( "fu_ben_bang_hui_ling_di", enterPosition, enterDirection )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		pass

#
# $Log: not supported by cvs2svn $
#

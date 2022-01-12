# -*- coding: gb18030 -*-
#
"""
"""
import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csstatus
import csdefine
import random
import csconst
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam
from ObjectScripts.GameObjectFactory import g_objFactory
from LevelEXP import AmendExp
import ECBExtend


g_monsters = [
		"20612011", 	# 大力神兵
		"20622014", 	# 天剑神兵
		"20632009", 	# 飞火神兵
		"20642008", 	# 传法神兵
		"20652010", 	# 金甲神兵
	]
BOSS_ID = "20654003" 	# 胜战神将

class SpaceCopyExpMelee( SpaceCopyTeam ):
	"""
	经验乱斗脚本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTeam.load( self, section )
		self._posData = {}
		for idx, item in enumerate( section[ "Space" ][ "monsterPoint" ].values() ):
			ls = []
			self._posData[ idx ] = ls
			for point in item.values():
				pos = tuple( [ float(x) for x in point["pos"].asString.split() ] )
				ls.append( ( pos, eval( point["direction"].asString ), eval( point["randomWalkRange"].asString ) ) )

		point = section[ "Space" ][ "BossPoint" ]
		self.bossPoint = ( eval( point["pos"].asString ), eval( point["direction"].asString ), eval( point["randomWalkRange"].asString ) )

		point = section[ "Space" ][ "doorPoint" ]
		self.doorPoint = ( eval( point["pos"].asString ), point["radius"].asFloat )

	def packedDomainData( self, entity ):
		"""
		"""
		return { 'dbID' : entity.databaseID, "teamID" : entity.teamMailbox.id, "captainDBID" : entity.captainID, "spaceKey": entity.teamMailbox.id}

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.isTeamCaptain():
			packDict[ "isTeamCaptain" ] = True
			packDict[ "playerLevel" ] = entity.level
			packDict[ "spaceName" ] = entity.popTemp( "currentSpaceName", 0 )
			packDict[ "enterPosition" ] = entity.popTemp( "enterPosition",(0,0,0) )
			packDict[ "enterDirection" ] = entity.popTemp( "enterDirection",(0,0,0) )
			packDict[ "teamID" ] = entity.teamMailbox.id

		if entity.isInTeam():
			packDict[ "teamID" ] = entity.teamMailbox.id

		return packDict

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		SpaceCopyTeam.initEntity( self, selfEntity )
		selfEntity.setTemp( "currMonsterTotal", 0 )		# 当前还剩多少怪物在副本
		selfEntity.setTemp( "castMonsterCount", 0 )		# 刷怪的批数
		#selfEntity.setTemp( "checkTeamTimerID", selfEntity.addTimer( 3, 3, 119 ) )

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
		castMonsterCount = selfEntity.queryTemp( "castMonsterCount", 0 )
		for posData in self._posData[ castMonsterCount ]:
			monsterID = g_monsters[ random.randint( 0, len( g_monsters ) - 1 ) ]
			monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className } }
			monInfo[ "spawnPos" ] = posData[0]
			monInfo[ "randomWalkRange" ] = posData[1][2]
			monInfo[ "level" ] = playerLevel
			selfEntity.createNPCObject( monsterID, posData[0], posData[1], monInfo )
			self.addCastMonsterCount( selfEntity, 1 )

		if selfEntity.queryTemp( "castMonsterCount", 0 ) == 0:
			#副本界面使用
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.JING_YAN_LUAN_DOU_INFO_3 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, 2400 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )
			selfEntity.setTemp( "leaveBoss", 1 )

			selfEntity.createNPCObject( "10111246", (23.978,0.832,46.077), (0,90,0), {} )		# 刷出离开副本对话npc
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, str( 15 - castMonsterCount ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.queryTemp( "currMonsterTotal", 0 ) )
		selfEntity.setTemp( "castMonsterCount", castMonsterCount + 1 )

	def onOverMelee( self, selfEntity, isTimeout ):
		"""
		活动结束
		"""
		if isTimeout:
			#刷NPC		10111201	玄天武尊	npcm0208_1
			if selfEntity.queryTemp( "OverMelee", -1 ) == True:
				return

			elist = []
			for e in selfEntity._players:
				player = BigWorld.entities.get( e.id )
				if player is not None and player.spaceID == selfEntity.spaceID:
					elist.append( player.databaseID )

			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
			selfEntity.createNPCObject( "10111201", self.bossPoint[0], self.bossPoint[1], { "tempMapping" : { "playerLevel": selfEntity.queryTemp( "playerLevel", 1 ), "rewardPlayers" : elist } } )
			#self.customCreateDoor( selfEntity, selfEntity.popTemp("spaceName"), selfEntity.popTemp("enterPosition"), selfEntity.popTemp("enterDirection") )
			self.statusMessageAllPlayer( selfEntity, csstatus.POTENTIAL_MELEE_ALERT_OVER )
		else:
			if selfEntity.queryTemp( "OverMelee", -1 ) == False:
				return

			# 活动时间到了,强制所有人离开副本
			for e in selfEntity._players:
				player = BigWorld.entities.get( e.id )
				if player is not None:
					player.gotoForetime()
				else:
					e.cell.gotoForetime()

			# 开始倒计时30秒关闭副本
			selfEntity.setTemp( "destroyTimer", selfEntity.addTimer( 30, 0, 199  ) )

		selfEntity.setTemp( "OverMelee", isTimeout )

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""
		if monsterClassName in g_monsters:	# 如果小怪死亡了
			currMonsterTotal = selfEntity.queryTemp( "currMonsterTotal" )
			selfEntity.setTemp( "currMonsterTotal", currMonsterTotal - 1 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, currMonsterTotal - 1 )

			if currMonsterTotal <= 1:	# 如果一轮怪物都死掉了
				if selfEntity.queryTemp( "castMonsterCount", 0 ) < 15:	# 刷满15轮
					selfEntity.setTemp( "castMonsterWaitTimeID", selfEntity.addTimer( 15, 0, 199 ) )
				else:	# 刷出boss，麻烦啊
					BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, str( 0 ) )
					monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className } }
					monInfo[ "spawnPos" ] = self.bossPoint[0]
					monInfo[ "randomWalkRange" ] = self.bossPoint[2]
					monInfo[ "level" ] = selfEntity.queryTemp( "playerLevel", 10 )
					selfEntity.createNPCObject( BOSS_ID, self.bossPoint[0], self.bossPoint[1], monInfo )

		if monsterClassName == BOSS_ID:		# 如果boss挂了
			selfEntity.setTemp( "leaveBoss", 0 )
			self.onOverMelee( selfEntity, True )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if selfEntity.queryTemp( "destroyTimer", 0 ) == id:
			selfEntity.base.closeSpace( True )

		elif selfEntity.queryTemp( "castMonsterWaitTimeID", 0 ) == id:
			self.castAllMonster( selfEntity, selfEntity.queryTemp( "playerLevel", 10 ) )

		elif selfEntity.queryTemp( "checkTeamTimerID", 0 ) == id:
			for e in selfEntity._players:
				p = BigWorld.entities.get( e.id )
				if p is not None and p.teamMailbox == None:
					p.gotoForetime()

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		if not selfEntity.queryTemp( "tempHaveCome", False ) and params.get( "isTeamCaptain" ):	# 只设置一次
			BigWorld.globalData['ExpMelee_%i'%params['teamID'] ] = True
			selfEntity.setTemp('globalkey','ExpMelee_%i'%params['teamID'])

			selfEntity.setTemp( "playerLevel", params[ "playerLevel" ] )
			selfEntity.setTemp( "spaceName", params[ "spaceName" ] )
			selfEntity.setTemp( "enterPosition", params[ "enterPosition" ] )
			selfEntity.setTemp( "enterDirection", params[ "enterDirection" ] )
			self.castAllMonster( selfEntity, params[ "playerLevel" ] )
			selfEntity.setTemp( "tempHaveCome", True )

	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		if playerEntity.isTeamCaptain():
			return		
		SpaceCopyTeam.onLeaveTeam( self, playerEntity )
		playerEntity.getCurrentSpaceBase().cell.setLeaveTeamPlayerMB( playerEntity.base )

	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		通知所有人 指定的信息
		"""
		for e in selfEntity._players:
			p = BigWorld.entities.get( e.id )
			if p is not None:
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
		doordict["modelNumber"] = "gw7504"
		doordict["modelScale"] = 1.000000
		BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, self.doorPoint[0], (0, 0, 0), doordict )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		pass

# -*- coding: gb18030 -*-

"""
神鬼秘境副本
"""

from SpaceCopyMapsTeam import SpaceCopyMapsTeam
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import time
from GameObject import GameObject
from bwdebug import *
import csdefine
import ECBExtend
import csconst
import Const
from Resource.SpaceCopyCountLoader import SpaceCopyCountLoader

class SpaceCopyShenGuiMiJing( SpaceCopyMapsTeam ):
	"""
	神鬼秘境脚本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyMapsTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.recordKey = "shenguimijing_record"
		self.difficulty = 0
		#self._bossID = ""
		#self._curBossNum  = 0
		#self._curMonsterNum = 0
		self._curSpawnBossNeedNum = []

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyMapsTeam.load( self, section )
		self.difficulty = section[ "Space" ][ "difficulty" ].asInt
		#self._bossID = section[ "Space" ][ "bossID" ].asString
		#self._curBossNum = section[ "Space" ][ "curBossNum" ].asInt
		#self._curMonsterNum = section[ "Space" ][ "curMonsterNum" ].asInt
		if section[ "Space" ].has_key( "curSpawnBossNeedNum" ):
			tempSpawnBossNeedNumList = section[ "Space" ][ "curSpawnBossNeedNum" ].asString.split(";")
			for num in tempSpawnBossNeedNumList:
				self._curSpawnBossNeedNum.append( int( num ) )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		SpaceCopyMapsTeam.initEntity( self, selfEntity )
		#selfEntity.setTemp( "bossCount", self._curBossNum )
		#selfEntity.setTemp( "allMonsterCount", self._curMonsterNum )

	def packedDomainData( self, entity ):
		"""
		创建SpaceDomainShenGuiMiJing时，传递参数
		"""
		d = SpaceCopyMapsTeam.packedDomainData( self, entity )
		if entity.teamMailbox:
			d["mailbox"] = entity.base
			# 设置队伍平均等级、最高等级（队伍等级为队长等级，最高等级为队长等级加3）
			if entity.isTeamCaptain():
				d["teamLevel"] = entity.level
				d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				if self._isPickMembers:
					d["membersMailboxs"] = self._pickMemberData( entity )
			else:
				captain = entity.getTeamCaptain()
				if captain:
					d["teamLevel"] = captain.level
					d["teamMaxLevel"] = min( captain.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				else:
					d["teamLevel"] = entity.level
					d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )

		return d
	
	def _pickMemberData( self, entity ):
		# 打包队友数据
		teamMemberMailboxsList = entity.getTeamMemberMailboxs()
		if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
			teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
		
		return teamMemberMailboxsList

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyMapsTeam.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id

		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		进入神鬼秘境
		"""
		if baseMailbox is not None and self._spaceMapsNo == 0 and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_SHEN_GUI_MI_JING, self.recordKey )
			
		SpaceCopyMapsTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		# 进入之后，设置相应任务的任务标记teamID，与相应的队伍绑定
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]

		if not selfEntity.queryTemp( "tempHaveCome", False ):	# 只设置一次
			selfEntity.base.createSpawnEntities( { "level" : selfEntity.teamLevel } )		# 刷出怪物
			selfEntity.setTemp( "tempHaveCome", True )

		#副本界面使用
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.ACTIVITY_SHEN_GUI_MI_JING )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.createTime )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, self._spaceLife * 60 )

		baseMailbox.client.startCopyTime( self._spaceLife * 60 - int( time.time() - selfEntity.createTime ) )	# 通知客户端副本倒计时

		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )	# 检查进入副本的时候是否有队伍，防止：副本中下线再上线没在队伍中

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		"""
		SpaceCopyMapsTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.endCopyTime()

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""	
		if self._bossID and monsterClassName in self._bossID:
			# boss死亡后，boss召唤出来的小怪消失
			tempCount = selfEntity.queryTemp( "bossCount" )
			tempCount -= 1
			
			selfEntity.setTemp( "bossCount", tempCount )
			selfEntity.domainMB.killCopyBoss( selfEntity.copyKey )
			if tempCount == 0:
				self.createDoor( selfEntity, False )
				
				for id in selfEntity.queryTemp( "tempCallMonsterIDs", [] ):
					if BigWorld.entities.has_key( id ):
						entity = BigWorld.entities[id]
						entity.destroy()

		#if self._bossID and monsterClassName == self._bossID:
			#self.createDoor( selfEntity, False )
			
			#for id in selfEntity.queryTemp( "tempCallMonsterIDs", [] ):
			#	if BigWorld.entities.has_key( id ):
			#		entity = BigWorld.entities[id]
			#		entity.destroy()
			
			#tempCount = selfEntity.queryTemp( "bossCount" )
			#tempCount -= 1
			
			#selfEntity.setTemp( "bossCount", tempCount )
			#selfEntity.domainMB.killCopyBoss( selfEntity.copyKey )
		else:
			#tempCount = selfEntity.queryTemp( "allMonsterCount" )
			#tempCount -= 1
			#selfEntity.setTemp( "allMonsterCount", tempCount )
			#if tempCount == 0:
			#	for bossID in self._bossID:
			#		selfEntity.base.createSpawnEntities( { "bossID":bossID, "level" : selfEntity.teamLevel } )				# 刷出巫妖王
				#selfEntity.base.createSpawnEntities( { "bossID":self._bossID, "level" : selfEntity.teamLevel } )				# 刷出巫妖王
			tempCount = selfEntity.queryTemp( "totalMonsterCount", 0 )
			tempCount += 1
			selfEntity.setTemp( "totalMonsterCount", tempCount )
			for index,count in enumerate( self._curSpawnBossNeedNum ):
				if tempCount == count:
					if index > len( self._bossID ) - 1:
						DEBUG_MSG("SpaceCopyShenGuiMiJing:index(%s) more than the length of self._bossID(%s)."%( index, len( self._bossID ) ) )
					else:
						selfEntity.base.createSpawnEntities( { "bossID":self._bossID[ index ], "level" : selfEntity.teamLevel } )
				
			selfEntity.domainMB.killCopyMonster( selfEntity.copyKey )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		DEBUG_MSG( "Role %i is killed by a enemy." % role.id )
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		cbid = role.addTimer( 32.0, 0, ECBExtend.ROLE_REVIVE_TIMER )
		role.setTemp( "role_die_to_revive_cbid", cbid )
	
	def setCopyKillBoss( self, selfEntity, bossNum ):
		"""
		define method
		设置副本BOSS数量
		"""
		SpaceCopyMapsTeam.setCopyKillBoss( self, selfEntity, bossNum )
		if self._copyBossNum ==  bossNum:
			selfEntity.domainMB.closeCopyItem( { "teamID": selfEntity.copyKey } )
			
	def onZhainanHPChange( self, selfEntity, hp, hp_Max ):
		"""
		斋南怒气值改变（实际用的血量）
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_ZHANNAN_ANGER_PERCENT, int( hp*1.0 / hp_Max*100 ) )
		
	def onShowAnger( self, selfEntity ):
		"""
		显示怒气值界面
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_ANGER_ISSHOW, True )
		
	def onHideAnger( self, selfEntity ):
		"""
		隐藏怒气值界面
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_ANGER_ISSHOW, False )
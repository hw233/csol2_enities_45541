# -*- coding: gb18030 -*-
#
# WXMonster类 2009-10-08 SongPeifang
#

from Monster import Monster
from bwdebug import *
import csdefine
import BigWorld
import cschannel_msgs


class WXMonster( Monster ):
	"""
	千年毒蛙(ToxinFrog)、牛魔王(BovineDevil)、白蛇妖(SnakeBoss)、巨灵魔(JuLingMo)
	堕落猎人(HunterMonster)、疯狂祭师(JishiMonster)、撼地大将(HandiMonster)、啸天大将(XiaotianMonster)
	的基类脚本文件
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.bornNPC = True
		self.callMonsterID		= ""
		self.callMonsterCount = 0
		self.fightingText		= ""
		self.freeText			= ""
		self.fightOption		= ""
		self.leaveOption		= ""
		self.fightSay			= ""
		self.dieSay				= ""
		self.dieNotifyText		= ""
		self.dieDelKey			= ""


	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		# 初始化附加数据放在前头
		Monster.initEntity( self, selfEntity )
		if not self.bornNPC:
			selfEntity.callMonsters( self.callMonsterID, self.callMonsterCount )


	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		if selfEntity.state == csdefine.ENTITY_STATE_FIGHT:
				playerEntity.setGossipText( cschannel_msgs.CELL_WXMONSTER_1 )
				playerEntity.sendGossipComplete( selfEntity.id )
				return
		if dlgKey == "Talk":
			if playerEntity.getState() == csdefine.ENTITY_STATE_FIGHT:
				playerEntity.setGossipText( self.fightingText )
				playerEntity.sendGossipComplete( selfEntity.id )
				return
			if selfEntity.getState() != csdefine.ENTITY_STATE_FREE:
				playerEntity.endGossip( selfEntity )
				return
			playerEntity.setGossipText( self.freeText )
			playerEntity.addGossipOption(  "NPCStart.s1", self.fightOption )
			playerEntity.addGossipOption(  "NPCLeave.s1", self.leaveOption )
			playerEntity.sendGossipComplete( selfEntity.id )
		elif dlgKey == "NPCStart.s1":
			if selfEntity.getState() != csdefine.ENTITY_STATE_FREE:
				playerEntity.endGossip( selfEntity )
				return

			selfEntity.say( self.fightSay )
			monsLvl = playerEntity.level
			selfEntity.setTemp( 'call_monster_level', monsLvl )
			selfEntity.setAINowLevel( 1 )
			selfEntity.changeToMonster( monsLvl, playerEntity.id )
			count = 3
			if playerEntity.isInTeam():
				teamMembers = playerEntity.teamMembers
				if len( teamMembers ) >= 4:
					# 如果有4个或4个以上的人一起组队杀，就召唤14个小怪
					count = 14
				elif len( teamMembers ) >= 3:
					# 如果有3个或3个以上的人一起组队杀，就召唤9个小怪
					count = 9
				elif len( teamMembers ) >= 2:
					# 如果有2人一起组队杀，就召唤6个小怪
					count = 6
			selfEntity.callMonsters( self.callMonsterID, count )	# 召唤小怪
			playerEntity.endGossip( selfEntity )
		elif dlgKey == "NPCLeave.s1":
			playerEntity.endGossip( selfEntity )

	def dieNotify( self, selfEntity, killerID ):
		"""
		死亡通知
		"""
		Monster.dieNotify( self, selfEntity, killerID )
		if self.dieSay != "":
			selfEntity.say( self.dieSay )
		if self.dieNotifyText != "":
			bootyOwner = selfEntity.getBootyOwner()
			if BigWorld.entities.has_key( bootyOwner[0] ):
				killerID = bootyOwner[0]
			if not BigWorld.entities.has_key( killerID ):
				ERROR_MSG( "DieNotify of %s script counld not find player id: %s:" % ( selfEntity.getName(), killerID ) )
				return
			killer = BigWorld.entities[killerID]
			if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
				owner = killer.getOwner()
				if owner.etype == "MAILBOX" :
					ERROR_MSG( "%s被id为%s的Entity杀死。" % ( selfEntity.getName(), killerID ) )
					return
				killer = owner.entity
			killerName = killer.playerName
			if bootyOwner[1] != 0 and BigWorld.entities.has_key( killer.captainID ):
				killer = BigWorld.entities[ killer.captainID ]
				killerName = cschannel_msgs.CELL_WXMONSTER_2 % killer.playerName
			notifyStr = self.dieNotifyText % killerName
			selfEntity.sysBroadcast( notifyStr )
		if self.dieDelKey != "":
			BigWorld.globalData[ self.dieDelKey ] = False
			
	def getSpawnPos( self, selfEntity ):
		return selfEntity.spawnPos
		
	def getBootyOwner( self, selfEntity ):
		"""
		virtual method
		获得战利品拥有者
		"""
		bootyOwner = selfEntity.queryTemp( "ToxinFrog_bootyOwner", () )
		if bootyOwner: return bootyOwner
		return Monster.getBootyOwner( self, selfEntity )
		
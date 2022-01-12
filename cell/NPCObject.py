# -*- coding: gb18030 -*-
#
# $Id: NPCObject.py,v 1.30 2008-09-04 07:44:14 kebiao Exp $

"""
NPC基类
"""

import BigWorld
import ECBExtend
from bwdebug import *
from interface.GameObject import GameObject
import csdefine
import csconst
import cPickle
import Const
from Resource.SkillLoader import g_skills
import SkillTargetObjImpl
from Resource.BoundingBoxLoader import BoundingBoxLoader
from ObjectScripts.GameObjectFactory import g_objFactory


g_bounds = BoundingBoxLoader.instance()

import csstatus


class NPCObject(GameObject):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		GameObject.__init__( self )

		# 检查是否有任务
		script = self.getScript()
		if script and ( script.getStartCount() > 0 or script.getFinishCount() > 0 ):
			self.addFlag( csdefine.ENTITY_FLAG_QUEST_ISSUER )

		if self.lifetime > 0:
			self.addTimer( self.lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def setTitle( self, title ):
		"""
		define method.
		设置名称
		"""
		self.title = title
		self.planesAllClients( "onSetTitle", ( title, ) )

	def getTitle( self ):
		"""
		virtual method.
		@return: the title of character entity
		@rtype:  STRING
		"""
		return self.title

	def setName( self, name ):
		"""
		define method.
		设置名称
		"""
		self.uname = name
		self.planesAllClients( "onSetName", ( name, ) )

	def getName( self ):
		"""
		virtual method.
		@return: the name of character entity
		@rtype:  STRING
		"""
		return self.uname

	def onDestroy( self ):
		"""
		entity 销毁的时候由BigWorld.Entity自动调用
		"""
		# spawnMB and indexInSpace in SpawnCode.def
		DEBUG_MSG( "%i: I dies." % self.id )
		if self.getScript():
			self.getScript().onDestroy( self )

	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		删除自身
		"""
		self.getScript().onDestroySelfTimer( self )
		self.destroy()

	def searchTeamMember( self, teamMailBoxID, range ):
		"""
		获取以怪物为中心点范围为“range”的与“teamMailBoxID”同一队伍的成员

		@param teamMailBoxID: 队伍的entityID，在这里其实就是队长的entityID；
		@type  teamMailBoxID: OBJECT_ID
		@param         range: 范围(半径)
		@type          range: FLOAT
		@return:              同一范围内所有队伍成员列表，如果没有队伍则返回一个空列表
		@rtype:               ARRAY of Entity
		"""
		return [ e for e in self.entitiesInRangeExt( range, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == teamMailBoxID ]

	def isInteractionRange( self, entity ):
		"""
		判断一个entity是否在自己的交互范围内
		"""
		return self.position.flatDistTo( entity.position ) < csconst.COMMUNICATE_DISTANCE

	# ------------------------------------------------
	# npc 聊天
	# ------------------------------------------------
	def say( self, msg ) :
		"""
		define method.
		AOI范围发言
		@type			msg : STRING
		@param			msg : 说话内容
		"""
		npcName = self.getName()
		self.planesAllClients( "onSay", ( npcName, msg ) )
		
	# ------------------------------------------------
	# npc 聊天 仅聊天泡泡可见
	# ------------------------------------------------
	def sayBupple( self, msg ) :
		"""
		define method.
		AOI范围发言
		@type			msg : STRING
		@param			msg : 说话内容
		"""
		self.planesAllClients( "onSayBupple", ( msg, ) )

	def whisper( self, msg, mbReceiver ) :
		"""
		defined method
		对某个角色私聊，调用者需保证 mbReceiver 不为 None
		@type			msg		   : STRING
		@param			msg		   : 私聊内容
		@type			mbReceiver : Role MAILBOX
		@param			mbReceiver : 私聊对象的 cell mailbox
		"""
		spkName = "M\0" + self.getName()
		mbReceiver.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, self.id, spkName, msg, [] )

	def yell( self, msg ) :
		"""
		defined method
		世界发言，所有玩家接收
		@type			msg : STRING
		@param			msg : 说话内容
		"""
		spkName = "W\0" + self.getName()
		for appName, app in BigWorld.globalData.items() :							# 获得所有的 BaseappEntity 的 base mailbox
			if appName.startswith( "GBAE" ) :
				app.globalChat( csdefine.CHAT_CHANNEL_NPC_SPEAK, self.id, spkName, msg )


	# ------------------------------------------------
	# gossip and quest about
	# ------------------------------------------------
	def gossipWith( self, srcEntityID, talkID ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		INFO_MSG("Use entity gossipWith function [%s,%s]" % ( self.id, self.__class__.__name__  ) )
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# 这个应该永远都不可能到达
			return
		if not self.isInteractionRange( playerEntity ):
			WARNING_MSG( "%s(%i): target too far." % (playerEntity.playerName, playerEntity.id) )
			return	# 距离目标太远不允许交谈

		if self.isReal():
			self.getScript().gossipWith( self, playerEntity, talkID )
		else:
			playerEntity.gossipWithForward(self, talkID )


	def questStatus( self, srcEntityID ):
		"""
		Exposed method.
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# 这个应该永远都不可能到达
			return

		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_ISSUER ):
			# 只有指定的任务存在于任务列表中才允许继续
			if playerEntity.isReal():
				self.getScript().questStatus( self, playerEntity )
			else:
				playerEntity.questStatusForward( self )

	def onQuestStatus( self, state ):
		"""
		@param state: QUEST_STATE_*
		@type  state: UINT8
		@return: None
		"""
		pass

	def setPosition( self, position ):
		"""
		define method
		更改位置
		"""
		self.position = position
	

	def endGossip( self, player ) :
		player.clientEntity( self.id ).onEndGossip()


	def onRequestCell( self, cellMailbox, baseMailbox ):
		"""
		创建副本空间 entity的cell返回
		"""
		self.getScript().onRequestCell( self , cellMailbox, baseMailbox )

	# =======================================
	# 邮件相关接口
	# =======================================
	def mail_send( self, receiverName, mailType, title, content, money, item = [] ):
		"""
		（用于NPC）发送邮件

		参数：
		@param receiverName: 收信人名字
		@type  receiverName: string
		@param     mailType: 邮件类型（快件还是普通件）
		@type      mailType: int8
		@param        title: 邮件的标题
		@type         title: string
		@param      content: 邮件的内容
		@type       content: string
		@param        money: 邮件包含的金钱
		@type         money: unit32
		@param         item: 邮件包含的物品
		@type          item: ITEM
		"""
		itemDatas = []
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )

		# 把信件发给邮件管理器
		BigWorld.globalData["MailMgr"].send(None, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, money, itemDatas)

	def mail_sendWithMailbox( self, receiverBase, receiverName, mailType, title, content, money, item = [] ):
		"""
		（用于NPC）有收件人的base mailbox的邮件发送

		参数：
		@param receiverName: 收信人名字
		@type  receiverName: string
		@param     mailType: 邮件类型（快件还是普通件）
		@type      mailType: int8
		@param        title: 邮件的标题
		@type         title: string
		@param      content: 邮件的内容
		@type       content: string
		@param        money: 邮件包含的金钱
		@type         money: unit32
		@param         item: 邮件包含的物品
		@type          item: ITEM
		"""
		itemDatas = []
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		if len(title) > csconst.MAIL_TITLE_LENGTH_MAX:		# 标题长度小于20个字检测
			return False
		if len(content) > csconst.MAIL_CONTENT_LENGTH_MAX:	# 标题长度小于400个字检测
			return False
		# 把信件发给邮件管理器
		BigWorld.globalData["MailMgr"].sendWithMailbox(None, receiverBase, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, money, itemDatas)

	def getBoundingBox( self ):
		"""
		virtual method.
		返回代表自身的bounding box的长、高、宽的Vector3实例；
		如果自身的模型有被缩放过，需要提供缩放后的值。

		@return: Vector3
		"""
		if len( self.modelNumber ) > 0:
			return g_bounds.get( self.modelNumber ) * self.modelScale
		return GameObject.getBoundingBox( self )

	def setModelNumber( self, modelNumber ):
		"""
		define method.
		设置模型编号
		"""
		self.modelNumber = modelNumber

	def setModelScale( self, modelScale ):
		"""
		define method.
		设置模型尺寸
		"""
		self.modelScale = modelScale

	def setQuestWorkingFlag( self, lastTime ):
		"""
		define method
		设置任务表现
		"""
		self.addTimer( lastTime, 0, ECBExtend.ADD_QUEST_FLAG_TIMER_CBID )
		self.addFlag( csdefine.ENTITY_FLAG_QUEST_WORKING )
	
	def onQuestFlagCBID( self, timerID, cbID ):
		"""
		设置任务表现回调，把任务表现位清除
		"""
		self.removeFlag( csdefine.ENTITY_FLAG_QUEST_WORKING )


	def setVisibleByRole( self, role, visible, lasted ):
		"""
		向某角色客户端设置NPC可见性
		@ role 玩家角色 player entity
		@ visible 是否可见 BOOL
		@ lasted 持续时间 float
		"""
		if visible:
			self.removeFlag( csdefine.ENTITY_FLAG_UNVISIBLE )		# 移除不可见标签
		else:
			self.addFlag( csdefine.ENTITY_FLAG_UNVISIBLE )		# 添加不可见标签
		if lasted > 0:
			self.addTimer( lasted, 0, ECBExtend.NPC_VISIBLE_CHANGE )
		
		self.planesAllClients( "setVisible", ( visible, ) )
		
	def onTimerNPCVisibleChange( self, timerID, cbID ):
		"""
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
			self.removeFlag( csdefine.ENTITY_FLAG_UNVISIBLE )
		else:
			self.addFlag( csdefine.ENTITY_FLAG_UNVISIBLE )
		self.planesAllClients( "setVisible", ( False, ) )
		DEBUG_MSG( "onTimerNPCVisibleChange" )

	def onSpaceGone( self ):
		"""
		space delete
		"""
		GameObject.onSpaceGone( self )
		currSpaceObj = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		currSpaceObj.onEntitySpaceGone( self )
	
	def onWitnessed( self, isWitnessed ):
		"""
		see also Python Cell API::Entity::onWitnessed()
		@param isWitnessed: A boolean indicating whether or not the entity is now witnessed;
		@type  isWitnessed: bool
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_MODEL_COLLIDE ):
			try:
				spell = g_skills[Const.ENTITY_CREATE_TRIGGER_SKILL_ID]
			except KeyError:
				ERROR_MSG( "%i: skill %i not exist." % ( self.id, skillID ) )
				return 
			spell.cast( self, SkillTargetObjImpl.createTargetObjEntity( self ) )
			
	def onEnterTrapExt( self, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		# 当有entity 进入怪物的陷阱范围之内，此函数就会被调用
		self.getScript().onEnterTrapExt( self, entity, range, controllerID )
		
	def onLeaveTrapExt( self, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity leaves a proximity trap of this entity.

		@param entity:		The entity that has left.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		self.getScript().onLeaveTrapExt( self, entity, range, userData )
# NPCObject.py

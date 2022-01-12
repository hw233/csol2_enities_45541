# -*- coding: gb18030 -*-
#
# $Id: NPCObject.py,v 1.30 2008-09-04 07:44:14 kebiao Exp $

"""
NPC����
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
	NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		GameObject.__init__( self )

		# ����Ƿ�������
		script = self.getScript()
		if script and ( script.getStartCount() > 0 or script.getFinishCount() > 0 ):
			self.addFlag( csdefine.ENTITY_FLAG_QUEST_ISSUER )

		if self.lifetime > 0:
			self.addTimer( self.lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def setTitle( self, title ):
		"""
		define method.
		��������
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
		��������
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
		entity ���ٵ�ʱ����BigWorld.Entity�Զ�����
		"""
		# spawnMB and indexInSpace in SpawnCode.def
		DEBUG_MSG( "%i: I dies." % self.id )
		if self.getScript():
			self.getScript().onDestroy( self )

	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		ɾ������
		"""
		self.getScript().onDestroySelfTimer( self )
		self.destroy()

	def searchTeamMember( self, teamMailBoxID, range ):
		"""
		��ȡ�Թ���Ϊ���ĵ㷶ΧΪ��range�����롰teamMailBoxID��ͬһ����ĳ�Ա

		@param teamMailBoxID: �����entityID����������ʵ���Ƕӳ���entityID��
		@type  teamMailBoxID: OBJECT_ID
		@param         range: ��Χ(�뾶)
		@type          range: FLOAT
		@return:              ͬһ��Χ�����ж����Ա�б����û�ж����򷵻�һ�����б�
		@rtype:               ARRAY of Entity
		"""
		return [ e for e in self.entitiesInRangeExt( range, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == teamMailBoxID ]

	def isInteractionRange( self, entity ):
		"""
		�ж�һ��entity�Ƿ����Լ��Ľ�����Χ��
		"""
		return self.position.flatDistTo( entity.position ) < csconst.COMMUNICATE_DISTANCE

	# ------------------------------------------------
	# npc ����
	# ------------------------------------------------
	def say( self, msg ) :
		"""
		define method.
		AOI��Χ����
		@type			msg : STRING
		@param			msg : ˵������
		"""
		npcName = self.getName()
		self.planesAllClients( "onSay", ( npcName, msg ) )
		
	# ------------------------------------------------
	# npc ���� ���������ݿɼ�
	# ------------------------------------------------
	def sayBupple( self, msg ) :
		"""
		define method.
		AOI��Χ����
		@type			msg : STRING
		@param			msg : ˵������
		"""
		self.planesAllClients( "onSayBupple", ( msg, ) )

	def whisper( self, msg, mbReceiver ) :
		"""
		defined method
		��ĳ����ɫ˽�ģ��������豣֤ mbReceiver ��Ϊ None
		@type			msg		   : STRING
		@param			msg		   : ˽������
		@type			mbReceiver : Role MAILBOX
		@param			mbReceiver : ˽�Ķ���� cell mailbox
		"""
		spkName = "M\0" + self.getName()
		mbReceiver.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, self.id, spkName, msg, [] )

	def yell( self, msg ) :
		"""
		defined method
		���緢�ԣ�������ҽ���
		@type			msg : STRING
		@param			msg : ˵������
		"""
		spkName = "W\0" + self.getName()
		for appName, app in BigWorld.globalData.items() :							# ������е� BaseappEntity �� base mailbox
			if appName.startswith( "GBAE" ) :
				app.globalChat( csdefine.CHAT_CHANNEL_NPC_SPEAK, self.id, spkName, msg )


	# ------------------------------------------------
	# gossip and quest about
	# ------------------------------------------------
	def gossipWith( self, srcEntityID, talkID ):
		"""
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param playerEntity: ˵�������
		@type  playerEntity: Entity
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: str
		@return: ��
		"""
		INFO_MSG("Use entity gossipWith function [%s,%s]" % ( self.id, self.__class__.__name__  ) )
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# ���Ӧ����Զ�������ܵ���
			return
		if not self.isInteractionRange( playerEntity ):
			WARNING_MSG( "%s(%i): target too far." % (playerEntity.playerName, playerEntity.id) )
			return	# ����Ŀ��̫Զ������̸

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
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# ���Ӧ����Զ�������ܵ���
			return

		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_ISSUER ):
			# ֻ��ָ������������������б��в��������
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
		����λ��
		"""
		self.position = position
	

	def endGossip( self, player ) :
		player.clientEntity( self.id ).onEndGossip()


	def onRequestCell( self, cellMailbox, baseMailbox ):
		"""
		���������ռ� entity��cell����
		"""
		self.getScript().onRequestCell( self , cellMailbox, baseMailbox )

	# =======================================
	# �ʼ���ؽӿ�
	# =======================================
	def mail_send( self, receiverName, mailType, title, content, money, item = [] ):
		"""
		������NPC�������ʼ�

		������
		@param receiverName: ����������
		@type  receiverName: string
		@param     mailType: �ʼ����ͣ����������ͨ����
		@type      mailType: int8
		@param        title: �ʼ��ı���
		@type         title: string
		@param      content: �ʼ�������
		@type       content: string
		@param        money: �ʼ������Ľ�Ǯ
		@type         money: unit32
		@param         item: �ʼ���������Ʒ
		@type          item: ITEM
		"""
		itemDatas = []
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )

		# ���ż������ʼ�������
		BigWorld.globalData["MailMgr"].send(None, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, money, itemDatas)

	def mail_sendWithMailbox( self, receiverBase, receiverName, mailType, title, content, money, item = [] ):
		"""
		������NPC�����ռ��˵�base mailbox���ʼ�����

		������
		@param receiverName: ����������
		@type  receiverName: string
		@param     mailType: �ʼ����ͣ����������ͨ����
		@type      mailType: int8
		@param        title: �ʼ��ı���
		@type         title: string
		@param      content: �ʼ�������
		@type       content: string
		@param        money: �ʼ������Ľ�Ǯ
		@type         money: unit32
		@param         item: �ʼ���������Ʒ
		@type          item: ITEM
		"""
		itemDatas = []
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		if len(title) > csconst.MAIL_TITLE_LENGTH_MAX:		# ���ⳤ��С��20���ּ��
			return False
		if len(content) > csconst.MAIL_CONTENT_LENGTH_MAX:	# ���ⳤ��С��400���ּ��
			return False
		# ���ż������ʼ�������
		BigWorld.globalData["MailMgr"].sendWithMailbox(None, receiverBase, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, money, itemDatas)

	def getBoundingBox( self ):
		"""
		virtual method.
		���ش��������bounding box�ĳ����ߡ����Vector3ʵ����
		��������ģ���б����Ź�����Ҫ�ṩ���ź��ֵ��

		@return: Vector3
		"""
		if len( self.modelNumber ) > 0:
			return g_bounds.get( self.modelNumber ) * self.modelScale
		return GameObject.getBoundingBox( self )

	def setModelNumber( self, modelNumber ):
		"""
		define method.
		����ģ�ͱ��
		"""
		self.modelNumber = modelNumber

	def setModelScale( self, modelScale ):
		"""
		define method.
		����ģ�ͳߴ�
		"""
		self.modelScale = modelScale

	def setQuestWorkingFlag( self, lastTime ):
		"""
		define method
		�����������
		"""
		self.addTimer( lastTime, 0, ECBExtend.ADD_QUEST_FLAG_TIMER_CBID )
		self.addFlag( csdefine.ENTITY_FLAG_QUEST_WORKING )
	
	def onQuestFlagCBID( self, timerID, cbID ):
		"""
		����������ֻص������������λ���
		"""
		self.removeFlag( csdefine.ENTITY_FLAG_QUEST_WORKING )


	def setVisibleByRole( self, role, visible, lasted ):
		"""
		��ĳ��ɫ�ͻ�������NPC�ɼ���
		@ role ��ҽ�ɫ player entity
		@ visible �Ƿ�ɼ� BOOL
		@ lasted ����ʱ�� float
		"""
		if visible:
			self.removeFlag( csdefine.ENTITY_FLAG_UNVISIBLE )		# �Ƴ����ɼ���ǩ
		else:
			self.addFlag( csdefine.ENTITY_FLAG_UNVISIBLE )		# ��Ӳ��ɼ���ǩ
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
		# ����entity �����������巶Χ֮�ڣ��˺����ͻᱻ����
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

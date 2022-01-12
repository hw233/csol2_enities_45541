# -*- coding: gb18030 -*-
#
# $Id: NPCObject.py,v 1.41 2008-08-29 02:38:42 huangyongwei Exp $

"""
"""

import random
import BigWorld
import GUI
import Math
import Language
import csdefine
import csconst
import Define
import GUIFacade
import event.EventCenter as ECenter
import EntityCache
from bwdebug import *
from interface.GameObject import GameObject
from gbref import rds
from NPCQuestSignMgr import npcQSignMgr
from config.NPCBoundingBox import Datas as g_boundData
from ChatFacade import chatFacade
from Function import Functor
import Const

g_entityCache = EntityCache.EntityCache.instance()

class NPCObject( GameObject ):
	"""
	NPC����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		GameObject.__init__( self )
		self.setSelectable( True )
		self.selectable = True
		self.questStates = 0			# hyw
		self.questState = False
		self.uname = ""
		self.title = ""
		self.attrDistance = 10.0
		self.own_familyName = ""
		self.voiceBan = False
		self.voiceTimerID = 0
		self.scaleTime = -1
		self.collideModel = None
		self.isCollide =  False
		self.preCompleteEffect = None
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_FLAG, csdefine.VISIBLE_RULE_BY_FLASH ]
		
	# ----------------------------------------------------------------
	# called by engine
	# ----------------------------------------------------------------
	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		prerep = []
		path = rds.npcModel.getModelSources( self.modelNumber )
		prerep.extend( path )
		hairPath = rds.npcModel.getHairPath( self.modelNumber )
		prerep.extend( [hairPath] )
		return prerep

	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.DumbFilter()

	def enterWorld( self ) :
		"""
		it will be called, when character enter world
		"""
		#  ��ʼ��ģ�����
		self.createModel( Define.MODEL_LOAD_ENTER_WORLD )
		self.setVisibility( False )
		GameObject.enterWorld( self )

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if not self.inWorld:
			return

		# ������������������״̬
		BigWorld.callback( 3.0, self.refurbishQuestStatus )
		GameObject.onCacheCompleted( self )
		#self.setVisibility( not self.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ) )
		self.updateVisibility()
		self.fadeInModel()
#		ECenter.fireEvent( "EVT_ON_QUEST_ENTITY_ENTER_WORLD", self.className, self.id )
	
	def leaveWorld( self ) :
		"""
		it will be called, when character leave world
		"""
		ECenter.fireEvent( "EVT_ON_QUEST_ENTITY_LEAVE_WORLD", self.className, self.id )
		GameObject.leaveWorld( self )

	# -------------------------------------------------
	def onSetAttrDistance( self, distance ):
		"""
		define method.
		����npc��������
		"""
		self.attrDistance = distance

	def onSetName( self, uname ):
		"""
		define method.
		��������
		"""
		self.uname = uname
		ECenter.fireEvent( "EVT_ON_ENTITY_NAME_CHANGED", self.id, uname )

	def getName( self ):
		"""
		ȡ��entity����
		"""
		return self.uname

	def onSetTitle( self, title ):
		"""
		define method.
		���óƺ�
		"""
		self.title = title

	def getTitle( self ):
		"""
		virtual method.
		��ȡͷ��
		@return: string
		"""
		return self.title

	def getHeadTexture( self ) :
		"""
		get npc's header
		"""
		return rds.npcModel.getHeadTexture( self.modelNumber )

	def getRoleAndNpcSpeakDistance( self ):
		"""
		NPC����ҶԻ��ľ���
		"""
		return csconst.COMMUNICATE_DISTANCE

	def onSetOwnFamilyName( self, familyName ):
		"""
		define method.
		����������������
		"""
		self.own_familyName = familyName
		ECenter.fireEvent( "EVT_ON_NPC_FAMILY_NAME_CHANGE", self.id, familyName )

	# -------------------------------------------------
	def isInteractionRange( self, entity ):
		"""
		�ж�һ��entity�Ƿ����Լ��Ľ�����Χ��
		"""
		return self.position.flatDistTo( entity.position ) < self.getRoleAndNpcSpeakDistance()

	# ----------------------------------------------------------------
	# about gossip and quest
	# ----------------------------------------------------------------
	"""
	def onSetGossipText( self, gossipText ):
		������������

		@type gossipText: string
		GUIFacade.onSetGossipText( gossipText )
	"""

	"""
	def onAddGossipOption( self, talkID, title ):
		��������ѡ��

		@type talkID: string
		@type  title: string
		GUIFacade.onAddGossipOption( talkID, title )
	"""

	"""
	def onAddGossipQuest( self, questID, title ):
		��������ѡ��

		@type questID: int32
		@type   title: string
		GUIFacade.onAddGossipQuest( questID, title )
	"""

#	def onGossipComplete( self, targetID ):
#		������Ϣ�������
#		GUIFacade.onGossipComplete( targetID )

#	def onEndGossip( self ) :
#		GUIFacade.onEndGossip( self )

	def onQuestStatus( self, id ):
		"""
		define
		����״̬�ı�ͨ��

		@param state: ֵΪQUEST_STATE_*��ֵ�����ƶ�λ�������ϣ��� state & (1<<QUEST_STATE_NOT_HAVE) ��Ϊ0���ʾ�пɽ�������������
		"""
		"""
		start = bool( state & ( 1 << csdefine.QUEST_STATE_NOT_HAVE ) )
		incomplete = bool( state & ( 1 << csdefine.QUEST_STATE_NOT_FINISH ) )
		finish = bool( state & ( 1 << csdefine.QUEST_STATE_FINISH ) )
		directFinish = bool( state & ( 1 << csdefine.QUEST_STATE_DIRECT_FINISH ) )
		self.questStates = start, incomplete, finish, directFinish ,isFixLoop
		ECenter.fireEvent( "EVT_ON_NPC_QUEST_STATE_CHANGED", self, start, incomplete, finish, directFinish , isFixLoop)
		"""
		self.questStates = id
		#print 'questStates:', id
		ECenter.fireEvent( "EVT_ON_NPC_QUEST_STATE_CHANGED", self, id )
		self.questState = npcQSignMgr.getStateBySignID( id ) == csdefine.QUEST_STATE_NOT_FINISH
	
	def playPreCompleteEffect( self ):
		"""
		���������(δ��)������ʾ��Ч
		"""
		if self.preCompleteEffect:return
		self.preCompleteEffect = rds.skillEffect.createEffectByID( Const.PRE_ECOMPLETE_EFFECT, self.getModel(), self.getModel(), Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )
		if self.preCompleteEffect:
			self.preCompleteEffect.start()
	
	def stopPreCompleteEffect( self ):
		"""
		�������
		ֹͣ�����(δ��)������ʾ��Ч
		"""
		if self.preCompleteEffect:
			self.preCompleteEffect.stop()
			self.preCompleteEffect = None

	def onSendQuetions( self, title, answers, questAccount, questInfo ):
		"""
		�����ʴ�
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_NPC_QUESTIONS", title, answers, questAccount, questInfo )

	def onAnswerSuceed( self, isSucceed ):
		ECenter.fireEvent( "EVT_ON_IS_ANSWER_SUCCEED", isSucceed )

	def refurbishQuestStatus( self ):
		"""
		����cell�����Լ�������״̬
		"""
		if self.inWorld and self.hasFlag( csdefine.ENTITY_FLAG_QUEST_ISSUER ):
			self.cell.questStatus()

	def onSay( self, npcName, msg ) :
		"""
		defined method
		NPC ˵��
		hyw--2009.09.03
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
			if not self.isOwnerVisible():
				return
				
		spkName = "N\0" + npcName
		BigWorld.player().chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, self.id, spkName, msg, [] )
	
	def onSayBupple( self,msg ):
		"""
		defined method
		npc˵�������������ݿɼ�
		"""
		from guis.otheruis.floatnames.FloatName import _fnameMgr as f
		q = f._FloadNameMgr__pyFNames.get( self.id, None )
		if q:
			q.showMsg_( msg )


	# ----------------------------------------------------------------
	# about action
	# ----------------------------------------------------------------
	def set_modelNumber( self, oldModelNumber = 0 ):
		"""
		������֪ͨģ�ͱ���иı�
		"""
		self.createModel()
		self.flushAttachments_()

	def set_modelScale( self, oldScale ):
		"""
		"""
		model = self.getModel()
		if model is None: return
		if self.scaleTime != -1:
			scaleTime = self.scaleTime
		else:
			scaleTime = Const.NPC_MODEL_SCALE_TIME_LEN
		rds.effectMgr.scaleModel( model, ( self.modelScale, self.modelScale, self.modelScale ), scaleTime )
		self.scaleTime = -1
		
	def onSetModelScaleTime( self, scaleTime):
		"""
		�ɷ���������ģ������ʱ��
		"""
		self.scaleTime = scaleTime
		
	def set_flags( self, oldFlag ) :
		"""
		NPCObject��flags��Ǳ�����ʱ����
		"""
		# ģ�ͽ���Ϊ��ɫ�Ĵ���
		flag = 1 << csdefine.ENTITY_FLAG_CHANG_COLOR_RED
		oldHasRedBlendFlag = flag & oldFlag == flag
		if self.hasFlag( csdefine.ENTITY_FLAG_CHANG_COLOR_RED ) and not oldHasRedBlendFlag:
			model = self.getModel()
			if model is None: return
			model.originColorBlend = ( 1.0, 1.0, 1.0, 1.0 )
			model.targetColorBlend = ( 1.0, 0, 0, 1.0 )
			model.colorBlendTimeLen = 2.0
			model.enableColorBlend = True
		elif oldHasRedBlendFlag and not self.hasFlag( csdefine.ENTITY_FLAG_CHANG_COLOR_RED ):
			model = self.getModel()
			if model is None: return
			model.enableColorBlend = False

		# ʹ�ò���entity���������filter
		if self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_FLY ):
			self.filter = BigWorld.AvatarFilter()
		else:
			flag = 1 << csdefine.ENTITY_FLAG_MONSTER_FLY
			if flag & oldFlag == flag:							# ����Ǵ�ENTITY_FLAG_MONSTER_FLYת�����������filter
				self.filter = BigWorld.AvatarDropFilter()

		# ���ܱ����ѡ��(ͬʱ���ɹ���)
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):
			self.setSelectable( False )
			rds.targetMgr.unbindTarget( self )

		flag = 1 << csdefine.ENTITY_FLAG_CAN_NOT_SELECTED
		oldHasCanNotSelectFlag = flag & oldFlag == flag

		if oldHasCanNotSelectFlag:
			self.setSelectable( True )

		# ���ɼ�
		if self.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ) or oldFlag & ( 1 << csdefine.ENTITY_FLAG_UNVISIBLE ):
			self.updateVisibility()

		flag = 1 << csdefine.ENTITY_FLAG_NPC_NAME
		oldNpcNameFlag = flag & oldFlag == flag
		# ����NPC������ʾ��־
		if self.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ) and not oldNpcNameFlag:
			ECenter.fireEvent( "EVT_ON_ENTITY_NPC_NAME_FLAG", self )
		# �Ƴ�NPC������ʾ��־
		if not self.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ) and oldNpcNameFlag:
			ECenter.fireEvent( "EVT_ON_ENTITY_RESET_NAME_FLAG", self )

		ECenter.fireEvent( "EVT_ON_NPC_FLAGS_CHANGED", self )

	def isCloseCollide( self, Flag ):
		"""
		�����Ƿ�ر���ײ
		"""
		if Flag:
			self.delModel( self.collideModel )
			self.collideModel = None
		self.isCollide = Flag

	def openCollide( self ):
		"""
		������ײ
		"""
		if self.isCollide: return
		if self.collideModel:
			self.delModel( self.collideModel )
		model = self.getModel()
		if not model: return
		pyStaticModel = rds.npcModel.createStaticModel( self.modelNumber, model.matrix, True )
		pyStaticModel.visible = False
		self.addModel( pyStaticModel )
		self.collideModel = pyStaticModel

	def set_ownerVisibleInfos( self, values ):
		"""
		����ӵ���߿ɼ�
		"""
		self.updateVisibility()

	def updateQuestVisibility( self ):
		"""
		��������NPCģ����ʾ
		"""
		ECenter.fireEvent( "EVT_ON_QUEST_ENTITY_ENTER_WORLD", self.className, self.id )

	def set_nameColor( self, oldColor ):
		"""
		����ͷ����ɫ���
		"""
		ECenter.fireEvent( "EVT_ON_NPC_NAMECOLOR_CHANGED", self )
	
	def isOwnerVisible( self ):
		"""
		����Լ��Ƿ��ǹ���Ŀɼ�ӵ����
		"""
		if self.ownerVisibleInfos == ( 0, 0 ):
			return False
		
		pID = self.ownerVisibleInfos[ 0 ]
		tID = self.ownerVisibleInfos[ 1 ]
		player = BigWorld.player()
		if pID == player.id or tID !=0 and tID == player.teamID:
			return True
		
		return False

	def getModel( self ):
		"""
		���ص�ǰ��ģ��
		return pyModel
		"""
		if self.model is None: return None
		if self.model.__class__.__name__ == "PyModelObstacle":
			if len( self.models ):
				return self.models[0]
			return None
		return self.model

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� NPCObject.createModel
		"""
		isStatic = rds.npcModel.isStaticModel( self.modelNumber )
		if isStatic:
			# ��̬ģ�͵����ŷ���
			m = Math.Matrix()
			m.setScale( ( self.modelScale, self.modelScale, self.modelScale ) )
			matrix = Math.Matrix( self.matrix )
			matrix.preMultiply( m )
			# ������̬ģ��
			model = rds.npcModel.createStaticModel( self.modelNumber, matrix, 0 )
			self.setModel( model )
			if self.model is None:
				ERROR_MSG( "entity %s loaded model %s fault." % ( self.className, self.modelNumber ) )
				return
			rds.npcModel.createDynamicModelBG( self.modelNumber + Const.DYNAMIC_MODEL_NAME,  Functor( self.onModelLoadFinish, isStatic, event ) )
		else:
			rds.npcModel.createDynamicModelBG( self.modelNumber, Functor( self.onModelLoadFinish, isStatic, event )  )
		#ģ����ײ���
		if self.hasFlag( csdefine.ENTITY_FLAG_MODEL_COLLIDE ):
			self.openCollide()
		
	def onModelLoadFinish( self, isStatic, event, pyModel ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		if pyModel is None: return
		if isStatic:
			self.model.visible = False
			self.addModel( pyModel  )
			# ����pyModel��Ϣ��PyModelObstacle һ��
			pyModel.scale = ( self.modelScale, self.modelScale, self.modelScale )
			pyModel.position = self.position
			pyModel.yaw = self.yaw
			rds.actionMgr.playAction( pyModel, Const.MODEL_ACTION_WJ_STAND )
		else:
			self.setModel( pyModel, event )
			pyModel.motors = ()
			pyModel.scale = ( self.modelScale, self.modelScale, self.modelScale )
			rds.actionMgr.playAction( pyModel, Const.MODEL_ACTION_WJ_STAND )
		#ģ����ײ���
		if self.hasFlag( csdefine.ENTITY_FLAG_MODEL_COLLIDE ):
			self.openCollide()
		
	def getBoundingBox( self ):
		"""
		virtual method.
		���ش��������bounding box�ĳ����ߡ����Vector3ʵ����
		��������ģ���б����Ź�����Ҫ�ṩ���ź��ֵ��

		@return: Vector3
		"""
		if len( self.modelNumber ) > 0:
			try:
				return Math.Vector3( g_boundData[ self.modelNumber ] ) * self.modelScale
			except KeyError, error:
				pass
		return GameObject.getBoundingBox( self )

	def onTargetFocus( self ):
		"""
		Ŀ�꽹���¼�
		"""
		GameObject.onTargetFocus( self )
		if self.questState:
			rds.ccursor.set( "pickup" )		# modified by hyw( 2008.08.29 )

	def onTargetBlur( self ):
		"""
		���������ƿ�
		"""
		GameObject.onTargetBlur( self )
		rds.ccursor.set( "normal" )			# modified by hyw( 2008.08.29 )

	def setFilterLastPosition( self, pos ):
		"""
		define method
		"""
		self.filter.setLastPosition( pos )

	def setFilterYaw( self, yaw ):
		"""
		define method
		�������ò�������ķ���
		"""
		if hasattr( self.filter, "setYaw" ):
			self.filter.setYaw( yaw )
		model = self.getModel()
		if model: model.yaw = yaw

	def setVisible( self, isVisible ):
		"""
		define method
		�����Ƿ�ɼ� by ����
		"""
		self.setVisibility( isVisible )

	def restartFilterMoving( self ):
		self.filter.restartMoving()

	def initCacheTasks( self ):
		"""
		��ʼ������������
		"""
		GameObject.initCacheTasks( self )
		self.addCacheTask( csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT0 )

	def setTempModelNumber( self, modelNumber, ctime ):
		"""
		��ʱ�ı�һ�¿ͻ���ģ��
		define mothod
		"""
		oldModel = self.modelNumber

		def resetModel():
			self.modelNumber = oldModel
			self.set_modelNumber()

		self.modelNumber = modelNumber
		self.set_modelNumber()
		BigWorld.callback( ctime, resetModel )

	def hideTheirFewTimeForQuest( self, htime ):
		"""
		��ʱ�������Լ�
		define mothod
		"""
		def resetVisible():
			self.setVisibility( True )

		self.setVisibility(False)
		BigWorld.callback( htime, resetVisible )

	def getParticleType( self ):
		"""
		ʵʱ�������Ӵ�������
		"""
		player = BigWorld.player()
		if player is None:
			return Define.TYPE_PARTICLE_NPC

		if player.targetEntity == self:
			return Define.TYPE_PARTICLE_PIN

		return Define.TYPE_PARTICLE_NPC

# --------------------------------------------------------------------
# NPCObject.py
# --------------------------------------------------------------------

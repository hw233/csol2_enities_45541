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
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化
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
		创建entity的filter模块
		"""
		return BigWorld.DumbFilter()

	def enterWorld( self ) :
		"""
		it will be called, when character enter world
		"""
		#  初始化模型相关
		self.createModel( Define.MODEL_LOAD_ENTER_WORLD )
		self.setVisibility( False )
		GameObject.enterWorld( self )

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return

		# 向服务器请求更新任务状态
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
		设置npc交互距离
		"""
		self.attrDistance = distance

	def onSetName( self, uname ):
		"""
		define method.
		设置名称
		"""
		self.uname = uname
		ECenter.fireEvent( "EVT_ON_ENTITY_NAME_CHANGED", self.id, uname )

	def getName( self ):
		"""
		取得entity名称
		"""
		return self.uname

	def onSetTitle( self, title ):
		"""
		define method.
		设置称号
		"""
		self.title = title

	def getTitle( self ):
		"""
		virtual method.
		获取头衔
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
		NPC和玩家对话的距离
		"""
		return csconst.COMMUNICATE_DISTANCE

	def onSetOwnFamilyName( self, familyName ):
		"""
		define method.
		设置所属家族名称
		"""
		self.own_familyName = familyName
		ECenter.fireEvent( "EVT_ON_NPC_FAMILY_NAME_CHANGE", self.id, familyName )

	# -------------------------------------------------
	def isInteractionRange( self, entity ):
		"""
		判断一个entity是否在自己的交互范围内
		"""
		return self.position.flatDistTo( entity.position ) < self.getRoleAndNpcSpeakDistance()

	# ----------------------------------------------------------------
	# about gossip and quest
	# ----------------------------------------------------------------
	"""
	def onSetGossipText( self, gossipText ):
		设置闲聊内容

		@type gossipText: string
		GUIFacade.onSetGossipText( gossipText )
	"""

	"""
	def onAddGossipOption( self, talkID, title ):
		增加闲聊选项

		@type talkID: string
		@type  title: string
		GUIFacade.onAddGossipOption( talkID, title )
	"""

	"""
	def onAddGossipQuest( self, questID, title ):
		增加任务选项

		@type questID: int32
		@type   title: string
		GUIFacade.onAddGossipQuest( questID, title )
	"""

#	def onGossipComplete( self, targetID ):
#		闲聊消息发送完毕
#		GUIFacade.onGossipComplete( targetID )

#	def onEndGossip( self ) :
#		GUIFacade.onEndGossip( self )

	def onQuestStatus( self, id ):
		"""
		define
		任务状态改变通告

		@param state: 值为QUEST_STATE_*按值向左移动位数后的组合；即 state & (1<<QUEST_STATE_NOT_HAVE) 不为0则表示有可接任务，其余类推
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
		播放已完成(未交)任务提示光效
		"""
		if self.preCompleteEffect:return
		self.preCompleteEffect = rds.skillEffect.createEffectByID( Const.PRE_ECOMPLETE_EFFECT, self.getModel(), self.getModel(), Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )
		if self.preCompleteEffect:
			self.preCompleteEffect.start()
	
	def stopPreCompleteEffect( self ):
		"""
		任务完成
		停止已完成(未交)任务提示光效
		"""
		if self.preCompleteEffect:
			self.preCompleteEffect.stop()
			self.preCompleteEffect = None

	def onSendQuetions( self, title, answers, questAccount, questInfo ):
		"""
		任务问答
		"""
		ECenter.fireEvent( "EVT_ON_RECIEVE_NPC_QUESTIONS", title, answers, questAccount, questInfo )

	def onAnswerSuceed( self, isSucceed ):
		ECenter.fireEvent( "EVT_ON_IS_ANSWER_SUCCEED", isSucceed )

	def refurbishQuestStatus( self ):
		"""
		请求cell更新自己的任务状态
		"""
		if self.inWorld and self.hasFlag( csdefine.ENTITY_FLAG_QUEST_ISSUER ):
			self.cell.questStatus()

	def onSay( self, npcName, msg ) :
		"""
		defined method
		NPC 说话
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
		npc说话，仅聊天泡泡可见
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
		服务器通知模型编号有改变
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
		由服务器设置模型缩放时间
		"""
		self.scaleTime = scaleTime
		
	def set_flags( self, oldFlag ) :
		"""
		NPCObject的flags标记被设置时调用
		"""
		# 模型渐变为红色的处理
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

		# 使用不把entity拉到地面的filter
		if self.hasFlag( csdefine.ENTITY_FLAG_MONSTER_FLY ):
			self.filter = BigWorld.AvatarFilter()
		else:
			flag = 1 << csdefine.ENTITY_FLAG_MONSTER_FLY
			if flag & oldFlag == flag:							# 如果是从ENTITY_FLAG_MONSTER_FLY转变过来，更换filter
				self.filter = BigWorld.AvatarDropFilter()

		# 不能被鼠标选择(同时不可攻击)
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):
			self.setSelectable( False )
			rds.targetMgr.unbindTarget( self )

		flag = 1 << csdefine.ENTITY_FLAG_CAN_NOT_SELECTED
		oldHasCanNotSelectFlag = flag & oldFlag == flag

		if oldHasCanNotSelectFlag:
			self.setSelectable( True )

		# 不可见
		if self.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ) or oldFlag & ( 1 << csdefine.ENTITY_FLAG_UNVISIBLE ):
			self.updateVisibility()

		flag = 1 << csdefine.ENTITY_FLAG_NPC_NAME
		oldNpcNameFlag = flag & oldFlag == flag
		# 新增NPC名称显示标志
		if self.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ) and not oldNpcNameFlag:
			ECenter.fireEvent( "EVT_ON_ENTITY_NPC_NAME_FLAG", self )
		# 移除NPC名称显示标志
		if not self.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ) and oldNpcNameFlag:
			ECenter.fireEvent( "EVT_ON_ENTITY_RESET_NAME_FLAG", self )

		ECenter.fireEvent( "EVT_ON_NPC_FLAGS_CHANGED", self )

	def isCloseCollide( self, Flag ):
		"""
		设置是否关闭碰撞
		"""
		if Flag:
			self.delModel( self.collideModel )
			self.collideModel = None
		self.isCollide = Flag

	def openCollide( self ):
		"""
		开启碰撞
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
		设置拥有者可见
		"""
		self.updateVisibility()

	def updateQuestVisibility( self ):
		"""
		更新任务NPC模型显示
		"""
		ECenter.fireEvent( "EVT_ON_QUEST_ENTITY_ENTER_WORLD", self.className, self.id )

	def set_nameColor( self, oldColor ):
		"""
		设置头顶颜色标记
		"""
		ECenter.fireEvent( "EVT_ON_NPC_NAMECOLOR_CHANGED", self )
	
	def isOwnerVisible( self ):
		"""
		检查自己是否是怪物的可见拥有者
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
		返回当前的模型
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
		创建模型
		继承 NPCObject.createModel
		"""
		isStatic = rds.npcModel.isStaticModel( self.modelNumber )
		if isStatic:
			# 静态模型的缩放方法
			m = Math.Matrix()
			m.setScale( ( self.modelScale, self.modelScale, self.modelScale ) )
			matrix = Math.Matrix( self.matrix )
			matrix.preMultiply( m )
			# 创建静态模型
			model = rds.npcModel.createStaticModel( self.modelNumber, matrix, 0 )
			self.setModel( model )
			if self.model is None:
				ERROR_MSG( "entity %s loaded model %s fault." % ( self.className, self.modelNumber ) )
				return
			rds.npcModel.createDynamicModelBG( self.modelNumber + Const.DYNAMIC_MODEL_NAME,  Functor( self.onModelLoadFinish, isStatic, event ) )
		else:
			rds.npcModel.createDynamicModelBG( self.modelNumber, Functor( self.onModelLoadFinish, isStatic, event )  )
		#模型碰撞标记
		if self.hasFlag( csdefine.ENTITY_FLAG_MODEL_COLLIDE ):
			self.openCollide()
		
	def onModelLoadFinish( self, isStatic, event, pyModel ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		if pyModel is None: return
		if isStatic:
			self.model.visible = False
			self.addModel( pyModel  )
			# 设置pyModel信息和PyModelObstacle 一样
			pyModel.scale = ( self.modelScale, self.modelScale, self.modelScale )
			pyModel.position = self.position
			pyModel.yaw = self.yaw
			rds.actionMgr.playAction( pyModel, Const.MODEL_ACTION_WJ_STAND )
		else:
			self.setModel( pyModel, event )
			pyModel.motors = ()
			pyModel.scale = ( self.modelScale, self.modelScale, self.modelScale )
			rds.actionMgr.playAction( pyModel, Const.MODEL_ACTION_WJ_STAND )
		#模型碰撞标记
		if self.hasFlag( csdefine.ENTITY_FLAG_MODEL_COLLIDE ):
			self.openCollide()
		
	def getBoundingBox( self ):
		"""
		virtual method.
		返回代表自身的bounding box的长、高、宽的Vector3实例；
		如果自身的模型有被缩放过，需要提供缩放后的值。

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
		目标焦点事件
		"""
		GameObject.onTargetFocus( self )
		if self.questState:
			rds.ccursor.set( "pickup" )		# modified by hyw( 2008.08.29 )

	def onTargetBlur( self ):
		"""
		鼠标从箱子移开
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
		用于设置不动物体的方向。
		"""
		if hasattr( self.filter, "setYaw" ):
			self.filter.setYaw( yaw )
		model = self.getModel()
		if model: model.yaw = yaw

	def setVisible( self, isVisible ):
		"""
		define method
		设置是否可见 by 姜毅
		"""
		self.setVisibility( isVisible )

	def restartFilterMoving( self ):
		self.filter.restartMoving()

	def initCacheTasks( self ):
		"""
		初始化缓冲器任务
		"""
		GameObject.initCacheTasks( self )
		self.addCacheTask( csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT0 )

	def setTempModelNumber( self, modelNumber, ctime ):
		"""
		暂时改变一下客户端模型
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
		暂时的隐藏自己
		define mothod
		"""
		def resetVisible():
			self.setVisibility( True )

		self.setVisibility(False)
		BigWorld.callback( htime, resetVisible )

	def getParticleType( self ):
		"""
		实时返回粒子创建类型
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

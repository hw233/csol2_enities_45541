# -*- coding: gb18030 -*-
#
# $Id: GameObject.py,v 1.22 2008-07-15 08:51:10 phw Exp $

"""
"""
from Function import Functor

import BigWorld
import Math
import utils
import event.EventCenter as ECenter
import GUIFacade
import GUI
import csarithmetic
import EntityCache
from bwdebug import *
from gbref import rds
from UnitSelect import UnitSelect
import Define
import csdefine
import csconst
from ModelColorMgr import ModelColorMgr
import Const
from VisibleRule import g_visibleRules

g_entityCache = EntityCache.EntityCache.instance()

class GameObject( BigWorld.Entity ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Entity.__init__( self )

		# 在物体上实现效果时用到的变量，用于存放效果实例
		# 这个变量只能存放Effect实例，初始值为None
		self.effect = {}
		self.skilleffect = {}

		self.selectable = False		# 是否能够被选中
		self.useGlowEff = True	# 是否使用Glow效果
		self._cacheTasks = []		# entity的缓冲器任务
		self.isCacheOver = False	# 缓冲器任务是否已经完成
		# entity 的附带物，必须继承 EntityAttachment，一般为 UI 相关
		self.__attachments = []
		self.modelColorMgr = ModelColorMgr( self.model )
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID]

	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		return None

	# ----------------------------------------------------------------
	# entity type about
	# ----------------------------------------------------------------
	def isEntityType( self, type ):
		"""
		判断自己是否为指定类型的entity

		@rtype:  BOOL
		"""
		return self.utype == type

	def getEntityType( self ):
		"""
		取得自己的entity类型

		@rtype:  INT8
		"""
		return self.utype


	# ----------------------------------------------------------------
	# flags about
	# ----------------------------------------------------------------
	def hasFlag( self, flag ):
		"""
		判断一个entity是否有指定的标志

		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		@return: BOOL
		"""
		flag = 1 << flag
		return ( self.flags & flag ) == flag

	# ----------------------------------------------------------------
	# called by engine
	# ----------------------------------------------------------------
	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		# 这方法会在引擎调用enterWorld函数之前调用
		# 并且这方法在后台线程调用，不占用主线程的资源
		# 必须返回一个tuple或者list类型
		"""
		return ()

	def enterWorld( self ) :
		"""
		it will be called, when character enter world
		"""
		g_entityCache.insert( self )

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			self.isCacheOver = True
			return

		ECenter.fireEvent( "EVT_ON_ENTITY_ENTER_WORLD", self )
		self.notifyAttachments_( "onEnterWorld" )
		self.isCacheOver = True

		if rds.statusMgr.isInWorld():
			self.setFilter()

	def setFilter( self ):
		"""
		设定Filter
		"""
		filter = self.filterCreator()
		if filter: self.filter = filter

	def __clearAttachments( self, model ):
		for node in model.nodes():
			attachments = list( node.attachments )
			for attachment in attachments:
				node.detach( attachment )

	def leaveWorld( self ) :
		"""
		it will be called, when character leave world
		"""
		g_entityCache.remove( self.id )
		rds.targetMgr.unbindTarget( self )
		ECenter.fireEvent( "EVT_ON_ENTITY_LEAVE_WORLD", self )
		self.notifyAttachments_( "onLeaveWorld" )
		self.__attachments = []

		if isinstance( self.model, BigWorld.Model ):
			self.__clearAttachments( self.model )
			self.model.OnActionStart = None
		self.model = None

		models = list( self.models )
		for model in models:
			if isinstance( model, BigWorld.Model ):
				self.__clearAttachments( model )
				for motor in model.motors:
					cb = getattr( motor, "proximityCallback", None)
					if callable( cb ):
						cb()
			self.delModel( model )

		self.modelColorMgr = None

	# ----------------------------------------------------------------
	# attachment
	# ----------------------------------------------------------------
	def attach( self, attachment ) :
		"""
		添加一个附加物
		@type			attachment : EntityAttachment
		@param			attachment : 要添加的附加物
		"""
		if attachment not in self.__attachments :
			self.__attachments.append( attachment )
			self.notifyAttachments_( "onAttached", self )

	def detach( self, attachment ) :
		"""
		删除一个附加物
		@type			attachment : EntityAttachment
		@param			attachment : 要删除的附加物
		"""
		if attachment in self.__attachments :
			self.__attachments.remove( attachment )
			self.notifyAttachments_( "onDetached" )

	def clearAttachments( self ) :
		"""
		清除所有附加物
		"""
		for attachment in self.__attachments[:] :
			self.__attachments.remove( attachment )
			self.notifyAttachments_( "onDetached" )

	def notifyAttachments_( self, triggerName, *args ) :
		for attach in self.__attachments :
			trigger = getattr( attach, triggerName, None )
			if trigger is not None :
				trigger( *args )

	def flushAttachments_( self ) :
		for attach in self.__attachments :
			attach.flush()

	def getLeftNameColor( self ):
		"""
		获取玩家名字的颜色
		"""
		for attachment in self.__attachments :
			if hasattr( attachment, "leftColor" ) :
				return attachment.leftColor


	# ----------------------------------------------------------------
	# triggers
	# ----------------------------------------------------------------
	def onTargetClick( self, player ) :
		"""
		when I have been clicked as target, it will be called
		@type	player	:	instance
		@param	player	:	玩家实例
		@rtype			:	int
		@return			:	TARGET_CLICK_FAIL 点击失败, TARGET_CLICK_SUCC 点击成功,TARGET_CLICK_MOVE 点击移动
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_CLICKED", self.id )

	def onTargetFocus( self ) :
		"""
		when the mouse focuses me, it will be called
		"""
		if GUI.mcursor().visible:
			self.notifyAttachments_( "onTargetFocus" )
			self.onSetTargetFocus()
			if self.useGlowEff:
				try:
					self.model.enableShine = True
				except:
					pass

		if self.model and self.model.visible :
			ECenter.fireEvent( "EVT_ON_ENTITY_GOT_FOCUS", self.id )

	def onSetTargetFocus( self ):
		"""
		显示焦点光圈
		"""
		if rds.targetMgr.bindTargetCheck( self ):
			UnitSelect().setFocus( self )

	def onTargetBlur( self ) :
		"""
		when the mouse leaves me, it will be called
		"""
		self.notifyAttachments_( "onTargetBlur" )
		if self.useGlowEff:
			try:
				self.model.enableShine = False
			except:
				pass
		UnitSelect().detachFocus()
		ECenter.fireEvent( "EVT_ON_ENTITY_LOST_FOCUS", self.id )

	# ---------------------------------------
	def onBecomeTarget( self ) :
		"""
		当成为玩家的 Target 时被调用
		"""
		self.notifyAttachments_( "onBecomeTarget" )

	def onLoseTarget( self ) :
		"""
		当成为玩家的 Target 时被调用
		"""
		self.notifyAttachments_( "onLoseTarget" )

	def onCameraDirChanged( self, direction ):
		"""
		相机方向改变通知。
		此调用来自CamerasMgr::CameraHandler::handleMouseEvent()，
		且只有BigWorld.player()的onCameraDirChanged()方法会被调用。
		设计此方法的目的是让相机视角（相机看的方向）改变时可以让PlayerEntity做一些需要的事情。
		"""
		pass	# 默认什么事都不做


	# ----------------------------------------------------------------
	# misc
	# ----------------------------------------------------------------
	def getName( self ):
		"""
		virtual method.
		@return: the name of entity
		@rtype:  STRING
		"""
		return ""

	def getTitle( self ):
		"""
		virtual method.
		获取头衔
		@return: string
		"""
		return ""

	def accessNodes( self ):
		"""
		访问常用的Node点
		"""
		if not self.inWorld: return
		if self.model is None: return

		for nodeName in Const.MODEL_ACCESS_NODES:
			try:
				self.model.node( nodeName )
			except:
				pass

	def setModel( self, model, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		设置模型
		"""
		oldModel = self.model
		# 设置模型
		self.model = model

		# 访问Node点
		self.accessNodes()
		
		if self.inWorld:
			if event == Define.MODEL_LOAD_ENTER_WORLD and self.isSameClientPlanes():
				self.fadeInModel()
			elif self.id != BigWorld.player().id:
				self.model.visible = False

		# 刷新选择光圈
		UnitSelect().refreshTarget( self )
		if rds.targetMgr.bindTargetCheck( self ) :
			UnitSelect().refreshFocus( self )
		self.onModelChange( oldModel, model )
		
	def getUSelectSize( self ):
		"""
		获取选择光圈大小
		"""
		return -1

	def fadeInModel( self ):
		"""
		渐入模型
		"""
		rds.effectMgr.fadeInModel( self.model )

	def onModelChange( self, oldModel, newModel ):
		"""
		模型更换通知
		"""
		if self.modelColorMgr:
			self.modelColorMgr.onModelChange( oldModel, newModel )

	def getModel( self ):
		"""
		返回模型
		"""
		return self.model

	def getModelSize( self ):
		"""
		获取模型的长、宽、高
		@return Vector3
		"""
		model = self.getModel()
		return utils.getModelSize( model )

	def getOriginalModelSize( self ):
		"""
		获取模型的长、宽、高
		@return Vector3
		"""
		model = self.getModel()
		return utils.getOriginalModelSize( model )

	def getHeadPosition( self ) :
		"""
		获取角色头顶位置坐标
		"""
		pos = self.position
		pos = ( pos.x, pos.y + self.getModelSize().y, pos.z )
		return utils.world2PScreen( pos )

	def getHeadTexture( self ):
		"""
		获取角色头像
		@return: STRING
		"""
		return ""

	def canSelect( self ):
		return True

	def createFootTrigger( self, nodeName, isLeft = 1, callback = None ):
		"""
		创建一个FootTrigger实例，并关联到nodeName指定的骨骼(node)节点。

		@param nodeName: 创建的FootTrigger实例绑定到model的哪个node上
		@param   isLeft: 是否是左脚（1），右脚为0
		@param callback: 当脚踏到地上时的回调
		@return: 成功则返回被创建的FootTrigger实例，失败则返回None。
		"""
		if self.model is None:
			return None		# 对于没有模型的entity来说，不应该创建FootTrigger。
		node = self.model.node( nodeName )
		if node is None:
			return None		# 对于不存在指定的node的model来说，不创建FootTrigger。

		footTrigger = BigWorld.FootTrigger( isLeft )
		footTrigger.footstepCallback = callback
		node.attach( footTrigger )
		return footTrigger

	def deleteFootTrigger( self, nodeName, footTrigger ):
		"""
		detach某个node上的某个FootTrigger实例

		@param nodeName: 要清除哪个node上的
		@param footTrigger: 要detach的FootTrigger实例
		"""
		if self.model:
			return
		node = self.model.node( nodeName )
		if node is None:
			return
		node.detach( footTrigger )

	# ----------------------------------------------------------------
	# bounding box
	# ----------------------------------------------------------------
	def getBoundingBox( self ):
		"""
		virtual method.
		返回代表自身的bounding box的长、高、宽的Vector3实例
		如果自身的模型有被缩放过，需要提供缩放后的值。

		@return: Vector3
		"""
		return Math.Vector3( ( 0.0, 0.0, 0.0 ) )

	def distanceBB( self, destEntity ):
		"""
		计算与目标entity的boundingbox边界之间的3D坐标系的距离

		@return: float
		"""
		# 当前直接以bounding box的宽的一半作为bounding box的中心到边界的距离
		if destEntity.__class__.__name__ != "MonsterBuilding":
			s1 = self.getBoundingBox().z / 2
			d1 = destEntity.getBoundingBox().z / 2
			return self.position.distTo( destEntity.position ) - s1 - d1
		else:
			return destEntity.distanceBB( self )

	def flatDistanceBB( self, destEntity ):
		"""
		计算与目标entity的boundingbox边界之间的平面距离

		@return: float
		"""
		# 当前直接以bounding box的宽的一半作为bounding box的中心到边界的距离
		s1 = self.getBoundingBox().z / 2
		d1 = destEntity.getBoundingBox().z / 2
		return self.position.flatDistTo( destEntity.position ) - s1 - d1

	def separationBB( self, destPos, dist ):
		"""
		计算自身的bounding box靠destPos的边界离destPos一定距离(dist)的点。

		@param dist: 自身与目标entity应该相关的距离
		"""
		# 当前直接以bounding box的宽的一半作为bounding box的中心到边界的距离
		return csarithmetic.getSeparatePoint3( self.position, destPos, dist + self.getBoundingBox().z / 2 )

	# ----------------------------------------------------------------
	# defs
	# ----------------------------------------------------------------
	def remoteCall( self, name, args ):
		"""
		define method.
		远程方法调用，此方法用于让其它cellapp、baseapp调用未在.def中声明的方法；
		此方法在cellapp/baseapp调用clientapp的未声明方法最有价值，这样可以减少.def中client的声明方法，以其达到网络数据最少占用率。
		client top-level property Efficient to 61 (limit is 256)
		client method Efficient to 62 (limit is 15872)
		base method Efficient to 62 (limit is 15872)
		cell method Efficient to 62 (limit is 15872)

		@param name: STRING; 要调用的方法名称
		@param args: PY_ARGS; 被调用方法的参数列表，具体参数个数由各方法自行处理；
		"""
		try:
			method = getattr( self, name )
		except AttributeError, errstr:
			ERROR_MSG( "%s(%i): class %s has not method %s." % (self.getName(), self.id, self.__class__.__name__, name) )
			return
		method( *args )


	# ----------------------------------------------------------------
	# set_*
	# ----------------------------------------------------------------
	def set_title( self, oldTitle ) :
		ECenter.fireEvent( "EVT_ON_ENTITY_TITLE_CHANGED", self, oldTitle, self.getTitle() )

	def set_utype( self, oldValue ):
		"""
		when the utype changed, it will be called
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_UTYPE_CHANGED", self )
		ECenter.fireEvent( "EVT_ON_ENTITY_RESET_NAME_FLAG", self )
		self.notifyAttachments_( "onEnterWorld" )
	
	def set_planesID( self, oldValue ):
		"""
		设置新的位面ID
		"""
		self.updateVisibility()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getVisibility( self ) :
		"""
		指出角色是否可见，没有模型和模型 visible 为 False，皆为不可见，返回 False
		hyw -- 09.01.10
		"""
		model = self.getModel()
		if model:
			return model.visible
		return False

	def setVisibility( self, visible ) :
		"""
		设置模型可见性
		hyw -- 09.01.10
		"""
		model = self.getModel()
		if model:
			model.visible = visible
		if visible:
			if hasattr( self, "_oldTargetCaps" ):
				self.targetCaps = self._oldTargetCaps
				del self._oldTargetCaps
		else:
			if self.targetCaps != [] :
				self._oldTargetCaps = self.targetCaps
				self.targetCaps = []
			rds.targetMgr.unbindTarget( self )

	# -------------------------------------------------
	def entitiesInRange( self, rng, cnd = lambda ent : True, pos = None ) :
		"""
		搜索 entity 身边或指定点周边的所有 entity
		从 gbref 中移到这里，并修改了实现方式(hyw -- 2008.11.07)
		@type			rng : float
		@patam			rng : 搜索的半径
		@type			cnd : functor/method
		@param			cnd : 条件函数，它必须包含一个参数以表示遍历到的 entity，如果调用 cnd 返回 True，则表示参数 ent 是合法的 entity
		@type			pos : Vector3
		@param			pos : 搜索的位置，如果为 None，则以我本 Entity 的 position 作为搜索点
		@rtype				: list
		@return				: 返回所有要求的 entity
		"""
		entities = []
		if pos is None : pos = self.position
		dists = {}
		for e in BigWorld.entities.values() :
			dist = e.position.distTo( pos )
			if dist <= rng and cnd( e ) and self.isSameClientPlanes():
				entities.append( e )
				dists[e.id] = dist

		def distance_cmp( ent0, ent1 ) :
			d0 = dists[ent0.id]
			d1 = dists[ent1.id]
			if d0 < d1 : return -1
			elif d0 == d1 : return 0
			else : return 1
		entities.sort( cmp = distance_cmp )
		return entities

	# ----------------------------------------------------------------
	def setFilterLastPosition( self, pos ):
		"""
		define method
		用于控制移动物体不动的事情，限制位置同步信息的传输，减少服务器与客户端传输数据流量。
		"""
		pass

	def setFilterYaw( self, yaw ):
		"""
		define method
		用于设置不动物体的方向。
		"""
		pass

	def restartFilterMoving( self ):
		"""
		define method
		用于控制移动物体不动的事情，限制位置同步信息的传输，减少服务器与客户端传输数据流量。
		"""
		pass

	# -------------------------------------------------
	def initCacheTasks( self ):
		"""
		初始化EntityCache缓冲器任务
		"""
		pass

	def getCacheTasks( self ):
		"""
		获取EntityCache缓冲器任务
		"""
		return self._cacheTasks

	def onAddCacheTask( self, taskType ):
		"""
		define method.
		服务器主动向客户端添加某个任务
		"""
		DEBUG_MSG( "onAddCacheTask::%s taskType %i" % ( self.__class__.__name__, taskType ) )
		self.isCacheOver = False
		self.addCacheTask( taskType )
		g_entityCache.addUrgent( self )

	def addCacheTask( self, taskType ):
		"""
		define method.
		服务器主动向客户端添加某个任务
		"""
		for task in self._cacheTasks:
			if task.getType() == taskType:
				return
		self._cacheTasks.append( g_entityCache.getTask( taskType ) )

	# ----------------------------------------------------------------
	# 服务器通知播放一个动画
	# ----------------------------------------------------------------
	def onPlayAction( self, actionName ):
		"""
		Define method
		服务器通知播放一个动作
		"""
		rds.actionMgr.playAction( self.getModel(), actionName )

	def getParticleType( self ):
		"""
		实时返回粒子创建类型
		"""
		return Define.TYPE_PARTICLE_NPC

	# ----------------------------------------------------------------
	# planes
	# ----------------------------------------------------------------
	def isSameClientPlanes( self ):
		"""
		是否是同一位面
		"""
		if BigWorld.player() and hasattr( BigWorld.player(), "planesID" ) and hasattr( self, "planesID" ):
			return BigWorld.player().planesID == self.planesID
			
		return True
	
	def isSamePlanes( self, entity ):
		return self.planesID == entity.planesID
		
	def filterPlanesEntity( self, entitiesInTrap ):
		"""
		过滤掉不同位面的entity
		"""
		newList = []
		for e in entitiesInTrap:
			if isinstance( e, GameObject ) and e.isSameClientPlanes():
				newList.append( e )
		
		return newList
	
	def addTrapExt( self, radius, callback ):
		"""
		添加客户端陷阱
		"""
		func = Functor( self.onTrapExt, callback )
		return self.addTrap(radius, func )
	
	def onTrapExt( self, callback, entitiesInTrap ):
		"""
		客户端陷阱回调
		"""
		if rds.statusMgr.isInWorld():
			callback( self.filterPlanesEntity( entitiesInTrap ) )
		
	def addBoxTrapExt( self, pitch, yaw, roll, width, height, long, callback ):
		"""
		添加箱子型陷阱
		"""
		func = Functor( self.onBoxTrapExt, callback )
		return self.addBoxTrap( pitch, yaw, roll, width, height, long, func )
	
	def onBoxTrapExt( self, callback, entitiesInTrap ):
		"""
		箱子型陷阱触发回调
		"""
		if rds.statusMgr.isInWorld():
			callback( self.filterPlanesEntity( entitiesInTrap ) )
			
	#---------------------------------------------------------------
	#目标相关
	#---------------------------------------------------------------
	def setSelectable( self, canSelect ):
		"""
		设置能否被选中
		"""
		if canSelect:
			self.targetCaps = [1]
		else:
			self.targetCaps = []
	
	#---------------------------------------------------------------
	#模型显示部分
	#---------------------------------------------------------------		
	def updateVisibility( self ):
		"""
		更新模型显示方式
		"""
		visibleType = self.getModeVisibleType()
		self.setModelVisible( visibleType )
		self.updateQuestVisibility()

	def updateQuestVisibility( self ):
		pass

	def getModeVisibleType( self ):
		"""
		获取模型显示方式
		"""
		l = []
		for iRule in self.visibleRules:
			l.append( g_visibleRules[iRule]( self ) )
				
		return self.choseVisibleType( l )
		
	def setModelVisible( self, visibleType ):
		"""
		virtual method
		"""
		if visibleType == Define.MODEL_VISIBLE_TYPE_FALSE:
			self.setVisibility( False )
		else:
			self.setVisibility( True )
	
	def choseVisibleType( self, visibleTypeList ):
		"""	
		模型显示筛选规则	
		"""
		if Define.MODEL_VISIBLE_TYPE_FALSE in visibleTypeList:
			return Define.MODEL_VISIBLE_TYPE_FALSE
		elif Define.MODEL_VISIBLE_TYPE_FBUTBILL in visibleTypeList:
			return Define.MODEL_VISIBLE_TYPE_FBUTBILL
		elif Define.MODEL_VISIBLE_TYPE_SNEAK in visibleTypeList:
			return Define.MODEL_VISIBLE_TYPE_SNEAK
		else:
			return Define.MODEL_VISIBLE_TYPE_TRUE					
		
# GameObject.py
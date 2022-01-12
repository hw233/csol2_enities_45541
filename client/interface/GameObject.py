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

		# ��������ʵ��Ч��ʱ�õ��ı��������ڴ��Ч��ʵ��
		# �������ֻ�ܴ��Effectʵ������ʼֵΪNone
		self.effect = {}
		self.skilleffect = {}

		self.selectable = False		# �Ƿ��ܹ���ѡ��
		self.useGlowEff = True	# �Ƿ�ʹ��GlowЧ��
		self._cacheTasks = []		# entity�Ļ���������
		self.isCacheOver = False	# �����������Ƿ��Ѿ����
		# entity �ĸ��������̳� EntityAttachment��һ��Ϊ UI ���
		self.__attachments = []
		self.modelColorMgr = ModelColorMgr( self.model )
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID]

	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return None

	# ----------------------------------------------------------------
	# entity type about
	# ----------------------------------------------------------------
	def isEntityType( self, type ):
		"""
		�ж��Լ��Ƿ�Ϊָ�����͵�entity

		@rtype:  BOOL
		"""
		return self.utype == type

	def getEntityType( self ):
		"""
		ȡ���Լ���entity����

		@rtype:  INT8
		"""
		return self.utype


	# ----------------------------------------------------------------
	# flags about
	# ----------------------------------------------------------------
	def hasFlag( self, flag ):
		"""
		�ж�һ��entity�Ƿ���ָ���ı�־

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
		# �ⷽ�������������enterWorld����֮ǰ����
		# �����ⷽ���ں�̨�̵߳��ã���ռ�����̵߳���Դ
		# ���뷵��һ��tuple����list����
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
		EntityCache�������
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
		�趨Filter
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
		���һ��������
		@type			attachment : EntityAttachment
		@param			attachment : Ҫ��ӵĸ�����
		"""
		if attachment not in self.__attachments :
			self.__attachments.append( attachment )
			self.notifyAttachments_( "onAttached", self )

	def detach( self, attachment ) :
		"""
		ɾ��һ��������
		@type			attachment : EntityAttachment
		@param			attachment : Ҫɾ���ĸ�����
		"""
		if attachment in self.__attachments :
			self.__attachments.remove( attachment )
			self.notifyAttachments_( "onDetached" )

	def clearAttachments( self ) :
		"""
		������и�����
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
		��ȡ������ֵ���ɫ
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
		@param	player	:	���ʵ��
		@rtype			:	int
		@return			:	TARGET_CLICK_FAIL ���ʧ��, TARGET_CLICK_SUCC ����ɹ�,TARGET_CLICK_MOVE ����ƶ�
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
		��ʾ�����Ȧ
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
		����Ϊ��ҵ� Target ʱ������
		"""
		self.notifyAttachments_( "onBecomeTarget" )

	def onLoseTarget( self ) :
		"""
		����Ϊ��ҵ� Target ʱ������
		"""
		self.notifyAttachments_( "onLoseTarget" )

	def onCameraDirChanged( self, direction ):
		"""
		�������ı�֪ͨ��
		�˵�������CamerasMgr::CameraHandler::handleMouseEvent()��
		��ֻ��BigWorld.player()��onCameraDirChanged()�����ᱻ���á�
		��ƴ˷�����Ŀ����������ӽǣ�������ķ��򣩸ı�ʱ������PlayerEntity��һЩ��Ҫ�����顣
		"""
		pass	# Ĭ��ʲô�¶�����


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
		��ȡͷ��
		@return: string
		"""
		return ""

	def accessNodes( self ):
		"""
		���ʳ��õ�Node��
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
		����ģ��
		"""
		oldModel = self.model
		# ����ģ��
		self.model = model

		# ����Node��
		self.accessNodes()
		
		if self.inWorld:
			if event == Define.MODEL_LOAD_ENTER_WORLD and self.isSameClientPlanes():
				self.fadeInModel()
			elif self.id != BigWorld.player().id:
				self.model.visible = False

		# ˢ��ѡ���Ȧ
		UnitSelect().refreshTarget( self )
		if rds.targetMgr.bindTargetCheck( self ) :
			UnitSelect().refreshFocus( self )
		self.onModelChange( oldModel, model )
		
	def getUSelectSize( self ):
		"""
		��ȡѡ���Ȧ��С
		"""
		return -1

	def fadeInModel( self ):
		"""
		����ģ��
		"""
		rds.effectMgr.fadeInModel( self.model )

	def onModelChange( self, oldModel, newModel ):
		"""
		ģ�͸���֪ͨ
		"""
		if self.modelColorMgr:
			self.modelColorMgr.onModelChange( oldModel, newModel )

	def getModel( self ):
		"""
		����ģ��
		"""
		return self.model

	def getModelSize( self ):
		"""
		��ȡģ�͵ĳ�������
		@return Vector3
		"""
		model = self.getModel()
		return utils.getModelSize( model )

	def getOriginalModelSize( self ):
		"""
		��ȡģ�͵ĳ�������
		@return Vector3
		"""
		model = self.getModel()
		return utils.getOriginalModelSize( model )

	def getHeadPosition( self ) :
		"""
		��ȡ��ɫͷ��λ������
		"""
		pos = self.position
		pos = ( pos.x, pos.y + self.getModelSize().y, pos.z )
		return utils.world2PScreen( pos )

	def getHeadTexture( self ):
		"""
		��ȡ��ɫͷ��
		@return: STRING
		"""
		return ""

	def canSelect( self ):
		return True

	def createFootTrigger( self, nodeName, isLeft = 1, callback = None ):
		"""
		����һ��FootTriggerʵ������������nodeNameָ���Ĺ���(node)�ڵ㡣

		@param nodeName: ������FootTriggerʵ���󶨵�model���ĸ�node��
		@param   isLeft: �Ƿ�����ţ�1�����ҽ�Ϊ0
		@param callback: ����̤������ʱ�Ļص�
		@return: �ɹ��򷵻ر�������FootTriggerʵ����ʧ���򷵻�None��
		"""
		if self.model is None:
			return None		# ����û��ģ�͵�entity��˵����Ӧ�ô���FootTrigger��
		node = self.model.node( nodeName )
		if node is None:
			return None		# ���ڲ�����ָ����node��model��˵��������FootTrigger��

		footTrigger = BigWorld.FootTrigger( isLeft )
		footTrigger.footstepCallback = callback
		node.attach( footTrigger )
		return footTrigger

	def deleteFootTrigger( self, nodeName, footTrigger ):
		"""
		detachĳ��node�ϵ�ĳ��FootTriggerʵ��

		@param nodeName: Ҫ����ĸ�node�ϵ�
		@param footTrigger: Ҫdetach��FootTriggerʵ��
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
		���ش��������bounding box�ĳ����ߡ����Vector3ʵ��
		��������ģ���б����Ź�����Ҫ�ṩ���ź��ֵ��

		@return: Vector3
		"""
		return Math.Vector3( ( 0.0, 0.0, 0.0 ) )

	def distanceBB( self, destEntity ):
		"""
		������Ŀ��entity��boundingbox�߽�֮���3D����ϵ�ľ���

		@return: float
		"""
		# ��ǰֱ����bounding box�Ŀ��һ����Ϊbounding box�����ĵ��߽�ľ���
		if destEntity.__class__.__name__ != "MonsterBuilding":
			s1 = self.getBoundingBox().z / 2
			d1 = destEntity.getBoundingBox().z / 2
			return self.position.distTo( destEntity.position ) - s1 - d1
		else:
			return destEntity.distanceBB( self )

	def flatDistanceBB( self, destEntity ):
		"""
		������Ŀ��entity��boundingbox�߽�֮���ƽ�����

		@return: float
		"""
		# ��ǰֱ����bounding box�Ŀ��һ����Ϊbounding box�����ĵ��߽�ľ���
		s1 = self.getBoundingBox().z / 2
		d1 = destEntity.getBoundingBox().z / 2
		return self.position.flatDistTo( destEntity.position ) - s1 - d1

	def separationBB( self, destPos, dist ):
		"""
		���������bounding box��destPos�ı߽���destPosһ������(dist)�ĵ㡣

		@param dist: ������Ŀ��entityӦ����صľ���
		"""
		# ��ǰֱ����bounding box�Ŀ��һ����Ϊbounding box�����ĵ��߽�ľ���
		return csarithmetic.getSeparatePoint3( self.position, destPos, dist + self.getBoundingBox().z / 2 )

	# ----------------------------------------------------------------
	# defs
	# ----------------------------------------------------------------
	def remoteCall( self, name, args ):
		"""
		define method.
		Զ�̷������ã��˷�������������cellapp��baseapp����δ��.def�������ķ�����
		�˷�����cellapp/baseapp����clientapp��δ�����������м�ֵ���������Լ���.def��client����������������ﵽ������������ռ���ʡ�
		client top-level property Efficient to 61 (limit is 256)
		client method Efficient to 62 (limit is 15872)
		base method Efficient to 62 (limit is 15872)
		cell method Efficient to 62 (limit is 15872)

		@param name: STRING; Ҫ���õķ�������
		@param args: PY_ARGS; �����÷����Ĳ����б�������������ɸ��������д���
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
		�����µ�λ��ID
		"""
		self.updateVisibility()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getVisibility( self ) :
		"""
		ָ����ɫ�Ƿ�ɼ���û��ģ�ͺ�ģ�� visible Ϊ False����Ϊ���ɼ������� False
		hyw -- 09.01.10
		"""
		model = self.getModel()
		if model:
			return model.visible
		return False

	def setVisibility( self, visible ) :
		"""
		����ģ�Ϳɼ���
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
		���� entity ��߻�ָ�����ܱߵ����� entity
		�� gbref ���Ƶ�������޸���ʵ�ַ�ʽ(hyw -- 2008.11.07)
		@type			rng : float
		@patam			rng : �����İ뾶
		@type			cnd : functor/method
		@param			cnd : �������������������һ�������Ա�ʾ�������� entity��������� cnd ���� True�����ʾ���� ent �ǺϷ��� entity
		@type			pos : Vector3
		@param			pos : ������λ�ã����Ϊ None�������ұ� Entity �� position ��Ϊ������
		@rtype				: list
		@return				: ��������Ҫ��� entity
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
		���ڿ����ƶ����岻�������飬����λ��ͬ����Ϣ�Ĵ��䣬���ٷ�������ͻ��˴�������������
		"""
		pass

	def setFilterYaw( self, yaw ):
		"""
		define method
		�������ò�������ķ���
		"""
		pass

	def restartFilterMoving( self ):
		"""
		define method
		���ڿ����ƶ����岻�������飬����λ��ͬ����Ϣ�Ĵ��䣬���ٷ�������ͻ��˴�������������
		"""
		pass

	# -------------------------------------------------
	def initCacheTasks( self ):
		"""
		��ʼ��EntityCache����������
		"""
		pass

	def getCacheTasks( self ):
		"""
		��ȡEntityCache����������
		"""
		return self._cacheTasks

	def onAddCacheTask( self, taskType ):
		"""
		define method.
		������������ͻ������ĳ������
		"""
		DEBUG_MSG( "onAddCacheTask::%s taskType %i" % ( self.__class__.__name__, taskType ) )
		self.isCacheOver = False
		self.addCacheTask( taskType )
		g_entityCache.addUrgent( self )

	def addCacheTask( self, taskType ):
		"""
		define method.
		������������ͻ������ĳ������
		"""
		for task in self._cacheTasks:
			if task.getType() == taskType:
				return
		self._cacheTasks.append( g_entityCache.getTask( taskType ) )

	# ----------------------------------------------------------------
	# ������֪ͨ����һ������
	# ----------------------------------------------------------------
	def onPlayAction( self, actionName ):
		"""
		Define method
		������֪ͨ����һ������
		"""
		rds.actionMgr.playAction( self.getModel(), actionName )

	def getParticleType( self ):
		"""
		ʵʱ�������Ӵ�������
		"""
		return Define.TYPE_PARTICLE_NPC

	# ----------------------------------------------------------------
	# planes
	# ----------------------------------------------------------------
	def isSameClientPlanes( self ):
		"""
		�Ƿ���ͬһλ��
		"""
		if BigWorld.player() and hasattr( BigWorld.player(), "planesID" ) and hasattr( self, "planesID" ):
			return BigWorld.player().planesID == self.planesID
			
		return True
	
	def isSamePlanes( self, entity ):
		return self.planesID == entity.planesID
		
	def filterPlanesEntity( self, entitiesInTrap ):
		"""
		���˵���ͬλ���entity
		"""
		newList = []
		for e in entitiesInTrap:
			if isinstance( e, GameObject ) and e.isSameClientPlanes():
				newList.append( e )
		
		return newList
	
	def addTrapExt( self, radius, callback ):
		"""
		��ӿͻ�������
		"""
		func = Functor( self.onTrapExt, callback )
		return self.addTrap(radius, func )
	
	def onTrapExt( self, callback, entitiesInTrap ):
		"""
		�ͻ�������ص�
		"""
		if rds.statusMgr.isInWorld():
			callback( self.filterPlanesEntity( entitiesInTrap ) )
		
	def addBoxTrapExt( self, pitch, yaw, roll, width, height, long, callback ):
		"""
		�������������
		"""
		func = Functor( self.onBoxTrapExt, callback )
		return self.addBoxTrap( pitch, yaw, roll, width, height, long, func )
	
	def onBoxTrapExt( self, callback, entitiesInTrap ):
		"""
		���������崥���ص�
		"""
		if rds.statusMgr.isInWorld():
			callback( self.filterPlanesEntity( entitiesInTrap ) )
			
	#---------------------------------------------------------------
	#Ŀ�����
	#---------------------------------------------------------------
	def setSelectable( self, canSelect ):
		"""
		�����ܷ�ѡ��
		"""
		if canSelect:
			self.targetCaps = [1]
		else:
			self.targetCaps = []
	
	#---------------------------------------------------------------
	#ģ����ʾ����
	#---------------------------------------------------------------		
	def updateVisibility( self ):
		"""
		����ģ����ʾ��ʽ
		"""
		visibleType = self.getModeVisibleType()
		self.setModelVisible( visibleType )
		self.updateQuestVisibility()

	def updateQuestVisibility( self ):
		pass

	def getModeVisibleType( self ):
		"""
		��ȡģ����ʾ��ʽ
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
		ģ����ʾɸѡ����	
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
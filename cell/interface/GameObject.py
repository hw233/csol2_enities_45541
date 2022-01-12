# -*- coding: gb18030 -*-
#
# $Id: GameObject.py,v 1.30 2008-09-01 03:29:59 zhangyuxing Exp $

"""
"""
import BigWorld
from bwdebug import *
import ECBExtend
import csarithmetic
import csconst
import csdefine
import Math
import EntityCache
from ObjectScripts.GameObjectFactory import g_objFactory
from optimize_with_cpp.interface import GameObject_func as GOBJ_CPP_OPTIMIZE

g_entityCache = EntityCache.EntityCache.instance()

# Extraȫ������By wsf
import inspect
g_extraClsNameTuple = ( "Monster", "GameObject", "NPCObject" )		# EXTRA�ṩ֧�ֵĽű������б�
g_clsNameMap = {}										# ���������й��������ɵ���ʱӳ��


class GameObject( BigWorld.Entity, ECBExtend.ECBExtend ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Entity.__init__( self )
		ECBExtend.ECBExtend.__init__( self )

		script = self.getScript()
		if script:
			script.initEntity( self )

	# -------------------------------------------------
	# entity type about
	# -------------------------------------------------
	def getName( self ):
		"""
		virtual method.
		@return: the name of entity
		@rtype:  STRING
		"""
		return ""

	def getScript( self ):
		"""
		@return: �����Լ���ȫ�ֹ�����
		@rtype:  instance
		"""
		if len( self.className ):
			return g_objFactory.getObject( self.className )
		#ERROR_MSG( "%s:%s(%i): my className is NULL." % (self.__class__.__name__, self.getName(), self.id) )
		return None

	def isEntityType( self, etype ) :
		"""
		�ж��Ƿ���ĳ������( hyw )
		@type		etype : MACRO DEFINATION
		@param		etype : entity ����
		@rtype			  : bool
		@return			  : ����� etype �򷵻� True
		"""
		return self.utype == etype

	def getEntityType( self ):
		"""
		ȡ���Լ���entity����

		@rtype:  INT8
		"""
		return self.utype

	def setEntityType( self, type ):
		"""
		virtual method.
		�����Լ���entity����
		"""
		self.utype = type

	def getEntityTypeName( self ):
		"""
		��ȡ����entityʵ���Ļ���������Ҳ����entity.__class__.__name__

		@return: STRING
		"""
		return self.__class__.__name__


	# -------------------------------------------------
	# flags about
	# -------------------------------------------------
	def setFlag( self, flag ):
		"""
		�������ñ�־

		@param flag: ENTITY_FLAG_* ���ƺ���ϵ�ֵ
		@type  flag: INT
		"""
		self.flags = flag

	def addFlag( self, flag ):
		"""
		�������ñ�־

		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		"""
		flag = 1 << flag
		self.flags |= flag

	def removeFlag( self, flag ):
		"""
		�������ñ�־

		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		"""
		# ��32λ��ʹ�ã����Ǳ�־λ�����ʹ���������Ҫ��UINT32����ǰ�õ���INT32
		# ��ʹ��UINT32������һ��ԭ�������ǿ��ܲ�������ô���־��
		# ��һ��ԭ�������ʹ��UINT32��python��ʹ����INT64���������ֵ

		# ��0λϵͳ��������32λ�����ã�����Ҫ�Ӹ�31�ı�ǣ������Ѳ����ã���Ҫ���������͸�ΪINT64 by chenweilan
		flag = 1 << flag
		self.flags &= flag ^ 0x7FFFFFFFFFFFFFFF

	def hasFlag( self, flag ):
		"""
		�ж�һ��entity�Ƿ���ָ���ı�־
		��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�

		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		@return: BOOL
		"""
		return GOBJ_CPP_OPTIMIZE.hasFlag(self, flag)


	# -------------------------------------------------
	# mapping about
	# -------------------------------------------------

	def getTempMapping( self ):
		return self.tempMapping


	def queryTemp( self, key, default = None ):
		"""
		���ݹؼ��ֲ�ѯ��ʱmapping����֮��Ӧ��ֵ
		��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�

		@return: ����ؼ��ֲ������򷵻�defaultֵ
		"""
		return GOBJ_CPP_OPTIMIZE.queryTemp(self, key, default)


	def setTemp( self, key, value ):
		"""
		define method.
		��һ��key��дһ��ֵ
		��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�

		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		@param value: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
		"""
		GOBJ_CPP_OPTIMIZE.setTemp(self, key, value)


	def popTemp( self, key, default = None ):
		"""
		�Ƴ�������һ����key���Ӧ��ֵ
		"""
		return self.tempMapping.pop( key, default )

	def removeTemp( self, key ):
		"""
		define method.
		�Ƴ�һ����key���Ӧ��ֵ
		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		"""
		self.tempMapping.pop( key, None )

	def addTempInt( self, key, value ):
		"""
		��һ��key���Ӧ��ֵ���һ��ֵ��
		ע�⣺�˷����������Դ��Ŀ���ֵ�Ƿ�ƥ�����ȷ
		"""
		v = self.queryTempInt( key )
		self.setTemp( key, value + v )

	def queryTempInt( self, key ):
		"""
		���ݹؼ��ֲ�ѯ��ʱmapping����֮��Ӧ��ֵ

		@return: ����ؼ��ֲ������򷵻�0
		"""
		try:
			return self.tempMapping[key]
		except KeyError:
			return 0

	def queryTempStr( self, key ):
		"""
		���ݹؼ��ֲ�ѯ��ʱmapping����֮��Ӧ��ֵ

		@return: ����ؼ��ֲ������򷵻ؿ��ַ���""
		"""
		try:
			return self.tempMapping[key]
		except KeyError:
			return ""

	# ------------------------------------------------
	# think about
	# ------------------------------------------------
	def onThink( self ):
		"""
		virtual method.
		AI˼��
		"""
		pass

	def think( self, delay = 0.0 ):
		"""
		����������
		@param delay:	�ȴ��´δ���think��ʱ�䣬���delayΪ0����������
		@type  delay:	FLOAT
		"""
		if delay > 0.0:
			if self.thinkControlID < 0:	# ��thinkControlIDֵС��0ʱ��ʾ����think�����Ǵ�ֵ����С��0
				return
			t = BigWorld.time()
			if self.thinkControlID != 0:
				if self.thinkWaitTime - t <= delay:
					return	# ��ǰʣ��ʱ�����С���µĴ����ȴ�ʱ�䣬��ʹ�õ�ǰtimer��
				self.cancel( self.thinkControlID )
			self.thinkWaitTime = t + delay
			self.thinkControlID = self.addTimer( delay, 0.0, ECBExtend.THINK_TIMER_CBID )
		else:
			# stop if we waiting think
			if self.thinkControlID > 0:
				self.cancel( self.thinkControlID )
				self.thinkControlID = 0
			elif self.thinkControlID < 0:	# ��thinkControlIDֵС��0ʱ��ʾ����think�����Ǵ�ֵ����С��0
				return
			self.onThink()

	def pauseThink( self, stop = True ):
		"""
		��ֹ/����think��Ϊ��
		think��Ϊ����ֹ�Ժ�����ٴο������������ж�think�ĵ�����Ϊ���ᱻ���ԡ�
		"""
		if stop:
			if self.thinkControlID > 0:
				self.cancel( self.thinkControlID )
			self.thinkControlID = -1
		else:
			self.thinkControlID = 0

	def onThinkTimer( self, timerID, cbID ):
		"""
		ECBExtend timer callback.
		"""
		self.think( 0 )


	# -------------------------------------------------
	# space about
	# -------------------------------------------------
	def getCurrentSpaceBase( self ):
		"""
		ȡ��entity��ǰ���ڵ�space��space entity base
		@return: ����ҵ����򷵻���Ӧ��base���Ҳ����򷵻�None.
				�Ҳ�����ԭ��ͨ������Ϊspace����destoryed�У����Լ���û���յ�ת��֪ͨ��destroy.
		"""
		try:
			return BigWorld.cellAppData["spaceID.%i" % self.spaceID]
		except KeyError:
			return None
	
	def getCurrentSpaceCell( self ):
		"""
		ȡ��entity��ǰ���ڵ�space��space entity base
		@return: ����ҵ����򷵻���Ӧ��base���Ҳ����򷵻�None.
				�Ҳ�����ԭ��ͨ������Ϊspace����destoryed�У����Լ���û���յ�ת��֪ͨ��destroy.
		"""
		spaceCell = None
		spaceBase = self.getCurrentSpaceBase()
		if spaceBase:
			cellEntity = BigWorld.entities.get( spaceBase.id, None )
			if cellEntity:
				spaceCell = cellEntity
			else:
				spaceCell = spaceBase.cell

		return spaceCell

	def getCurrentSpaceType( self ):
		"""
		��ȡ��ǰ����space������ ���忴csdefine.SPACE_TYPE_*
		"""
		try:
			return int( BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) )
		except ValueError:
			return csdefine.SPACE_TYPE_NORMAL

	def getCurrentSpaceLineNumber( self ):
		"""
		��ȡ��ǰ����space������ �������0�� ���ʾ��ͼ��֧�ֶ��ߡ�
		"""
		try:
			return int( BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) )
		except ValueError:
			return 0

	def getCurrentSpaceData( self, key ):
		"""
		see also function BigWorld.getSpaceDataFirstForKey() from BigWorld cellApp python API;
		Gets space data for a key in the space which entity live in. Only appropriate for keys that should have only one value.

		@param key: the key to get data for; KEY_SPACEDATA_*
		@return: the value of the first entry for the key
		"""
		return BigWorld.getSpaceDataFirstForKey( self.spaceID, key )

	def getSpaceManager( self ):
		"""
		ȡ��SpaceManager��base mailbox
		@return: SpaceManager��base mailbox
		"""
		return BigWorld.globalData["SpaceManager"]	# ����������쳣�ͱ�ʾ��BUG

	def requestNewSpace( self, spaceType, mailbox ):
		"""
		��spaceManagerҪ�󴴽�һ���µĿռ�
		@param spaceType:	�ռ������ռ�Ĺؼ���
		@type spaceType:	string
		@param mailbox:	ʵ��mailbox: �ռ䴴����ɺ�֪ͨ��ʵ��mailbox ���Mailbox�ϱ�����onRequestCell����
		@type mailbox:	mailbox
		"""
		space = g_objFactory.getObject( spaceType )
		self.getSpaceManager().requestNewSpace( spaceType, mailbox, space.packedDomainData( self ) )

	def getCurrentSpaceScript( self ):
		"""
		��ȡ��ǰspace object script
		"""
		return g_objFactory.getObject( self.spaceType )

	# -------------------------------------------------
	# misc
	# -------------------------------------------------
	def createNPCObject( self, npcID, position, direction, state ):
		"""
		define method
		(Զ��)����һ������ҿ��ƶ��󣬱�������entity���뱻��������ͬһspace�ϡ�

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		self.createObjectRemote( npcID, self.spaceID, position, direction, state )

	def createObjectNear( self, npcID, position, direction, state ):
		"""
		virtual method.
		����һ��entity, ������
		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		return g_objFactory.createEntity( npcID, self.spaceID, position, direction, state )
	
	def createObjectNearPlanes( self, npcID, position, direction, state ):
		"""
		virtual method.
		����һ��entity, �������½�entity�뵱ǰentityͬһλ��
		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		state[ "planesID" ] = self.planesID
		return self.createObjectNear( npcID, position, direction, state )
		
	def createObjectRemote( self, npcID, spaceID, position, direction, state ):
		"""
		define method.Զ�̵���
		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		g_objFactory.createEntity( npcID, spaceID, position, direction, state )
	
	def createEntityNear( self, entityType, position, direction, state ):
		"""
		virtual method.
		����һ��entity, ������
		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		return BigWorld.createEntity( entityType, self.spaceID, position, direction, state )
	
	def createEntityNearPlanes( self, entityType, position, direction, state ):
		"""
		virtual method.
		����һ��entity, ������
		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		state[ "planesID" ] = self.planesID
		return self.createEntityNear( entityType, position, direction, state )
	
	def createEntityRemote( self, entityType, spaceID, position, direction, state ):
		"""
		define method.Զ�̵���
		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		BigWorld.createEntity( entityType, spaceID, position, direction, state )


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
			ERROR_MSG( "%s(%i): class %s has no method %s." % (self.getName(), self.id, self.__class__.__name__, name) )
			return
		#DEBUG_MSG( "remoteCall: name=%s, args=%s" % ( name, str(args) ) )
		method( *args )

	def forwardCall( self, entityID, name, args ):
		"""
		define method.
		Զ�̷�������ת�����Դ˽ӿ�������entityΪrealEntity������entityID��ָ����entity���ϵ�ĳ��������
		�˷�����Ҫ���ڼ�ʹ�ô�������Ľű��е��ض����ܴ��롣

		@param entityID: OBJECT_ID; Ҫ���÷�����entity�����entity�Ҳ�������Դ˴ε��á�
		@param name: STRING; Ҫ���õķ�������
		@param args: PY_ARGS; �����÷����Ĳ����б�������������ɸ��������д���
		"""
		entity = BigWorld.entities.get( entityID )
		if entity is None:
			WARNING_MSG( "target entity not found. target entity id = %d, method name = %s, param = %s." % (entityID, name, str(args)) )
			return

		try:
			method = getattr( entity, name )
		except AttributeError, errstr:
			ERROR_MSG( "%s(%i): class %s has no method %s." % (self.getName(), self.id, entity.__class__.__name__, name) )
			return
		method( *args )

	def forwardScriptCall( self, scriptName, name, args ):
		"""
		define method.
		Զ�̷�������ת�����Դ˽ӿ�������entityΪrealEntity������scriptName��ָ����ȫ�ֽű��ϵ�ĳ��������
		�˷�����Ҫ���ڼ�ʹ�ô�������Ľű��е��ض����ܴ��롣
		���ر��������ڵ�ǰ����������entity��cellapp���Ҳ���ָ����entity����������ø�entity����Ӧ�Ľű��������

		@param scriptName: STRING; Ҫ���÷����Ľű���(className)�����entity�Ҳ�������Դ˴ε��á�
		@param name: STRING; Ҫ���õķ�������
		@param args: PY_ARGS; �����÷����Ĳ����б�������������ɸ��������д���
		"""
		scriptClass = g_objFactory.getObject( scriptName )
		if scriptClass is None :								# 2007.12.14: mofified by hyw
			WARNING_MSG( "script not found. script name = %s, method name = %s, param = %s." % (scriptName, name, str(args)) )
			return

		try:
			method = getattr( scriptClass, name )
		except AttributeError, errstr:
			ERROR_MSG( "%s(%i): class %s has no method %s." % (self.getName(), self.id, scriptClass.__class__.__name__, name) )
			return
		method( *args )

	def remoteScriptCall( self, name, args ):
		"""
		define method.
		Զ�̽ű��������ã��Դ˽ӿ�������entityΪrealEntity�������Լ�������Ľű��ϵ�ĳ��������
		�˷�����Ҫ���ڼ�ʹ�ô�������Ľű��е��ض����ܴ��롣

		@param name: STRING; Ҫ���õķ�������
		@param args: PY_ARGS; �����÷����Ĳ����б�������������ɸ��������д���
		"""
		scriptClass = self.getScript()

		try:
			method = getattr( scriptClass, name )
		except AttributeError, errstr:
			ERROR_MSG( "%s(%i): class %s has no method %s." % (self.getName(), self.id, scriptClass.__class__.__name__, name) )
			return
		method( self, *args )

	def getBoundingBox( self ):
		"""
		virtual method.
		���ش��������bounding box�ĳ����ߡ����Vector3ʵ��
		��������ģ���б����Ź�����Ҫ�ṩ���ź��ֵ��

		@return: Vector3
		"""
		return Math.Vector3( ( 0.0, 0.0, 0.0 ) )

	def getDownToGroundPos( self ):
		"""
		��ȡ��Entity.position��Ӧ�ĵ���� by mushuang
		��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
		"""
		return GOBJ_CPP_OPTIMIZE.getDownToGroundPos(self)


	def distanceBB( self, destEntity ):
		"""
		������Ŀ��entity��boundingbox�߽�֮���3D����ϵ�ľ���
		��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�

		@return: float
		"""
		if destEntity.__class__.__name__ != "MonsterBuilding":
			return GOBJ_CPP_OPTIMIZE.distanceBB(self, destEntity)
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

	def sysBroadcast( self, msg ) :
		"""
		defined method
		��ϵͳ�㲥Ƶ���й㲥һ����Ϣ
		hyw--2009.06.30
		"""
		self.getGBAE().globalChat( csdefine.CHAT_CHANNEL_SYSBROADCAST, self.id, self.getName(), msg, [] )		# GBEA һ�����ڣ��������� base ���������Ѿ��ҵ�

	def getGBAE( self ) :
		"""
		��ȡ������globalData�е�baseMailbox
		"""
		return BigWorld.globalData[ csconst.C_PREFIX_GBAE ]

	def requestEntityData( self, srcEntityID, targetEntityID, taskType, isLastTask ):
		"""
		Expose method.
		��ҿͻ���������������ȡĳentity��������Ϣ��
		"""
		entity = BigWorld.entities.get( targetEntityID, None )
		if entity:
			task = g_entityCache.getTask( taskType )
			if task:
				task.do( entity, self, isLastTask )
			else:
				ERROR_MSG( "not fond task %i." % taskType )

	def onSpaceGone( self ):
		"""
		space delete
		"""
		DEBUG_MSG("Space gone delete entity!")

	def getExtraClsName( self ):
		"""
		for entity extra.ע�⣺�ṩ��Entity Extra���ã�������entity��Ӧ��extra��Ϣ��
		���ӳ�䵽Extra֧�ֵ��������Ա�����Ӧ��Extra��ʼ����14:06 2012-12-26 by wangshufeng��
		"""
		global g_clsNameMap
		global g_extraClsNameTuple
		tempClsList = []

		extraClassName = self.__class__.__name__
		for classType in inspect.getmro( self.__class__ ):
			if not issubclass( classType, BigWorld.Entity ):	# ���˵���entity class
				continue
			className = classType.__name__
			if g_clsNameMap.has_key( className ):
				extraClassName = g_clsNameMap[className]
				break
			tempClsList.append( className )
			if className in g_extraClsNameTuple:
				extraClassName = className
				break

		# �̳��������м�����className����Ӧ��extraClassName
		for temp in tempClsList:
			g_clsNameMap[temp] = extraClassName
		return extraClassName

	# ----------------------------------------------------------------
	# planes
	# ----------------------------------------------------------------
	def isSamePlanes( self, entity ):
		"""
		�Ƿ�ͬһλ��
		"""
		return self.isSamePlanesExt( entity ) #cellExtra
	
	def addProximityExt( self, range, userData = 0):
		"""
		����һ������
		"""
		return self.addProximity( range, userData )
	
	def onEnterTrap( self, entityEntering, range, controllerID ):
		"""
		��entity��������
		"""
		if not entityEntering.isDestroyed and self.isSamePlanes( entityEntering ):#ֻ��ͬһλ��ID����ҲŻᴥ��
			self.onEnterTrapExt( entityEntering, range, controllerID )
		
	def onEnterTrapExt( self, entityEntering, range, controllerID ):
		"""
		virtual method.
		��entity��������
		"""
		pass
	
	def onLeaveTrap( self, entityLeaving, range, controllerID ):
		"""
		��entity�뿪����
		"""
		if self.isDestroyed:
			return
			
		if not entityLeaving.isDestroyed:
			if self.isSamePlanes( entityLeaving ): #ֻ��ͬһλ��ID����ҲŻᴥ��
				self.onLeaveTrapExt( entityLeaving, range, controllerID )
		else:
			self.__onLevelTrapPickRemove( entityLeaving.id )
	
	def onLeaveTrapID( self, entityID, range, userData ):
		"""
		�뿪trap, �Ѿ����͵����cellapp����,���淽��
		"""
		
		self.__onLevelTrapPickRemove( entityID )
	
	def onLeaveTrapExt( self, entityLeaving, range, controllerID ):
		"""
		virtual method.
		��ͨ�뿪���崥��
		"""
		pass
	
	def __onLevelTrapPickRemove( self, entityID ):
		"""
		�뿪����entity��destroy����ΪTrue��ʱ����
		"""
		if self.isDestroyed:
			return
		
		removeDoArgs = self.onLevelTrapPickRemoteDo()
		if removeDoArgs: #���û���������Ͳ�ҪȥԶ�̵�����
			globalBaseMB = self.getGBAE()
			if globalBaseMB is None :
				ERROR_MSG( "The globalBaseMB should not be None, or all of that must have been breakdown!" )
				return
				
			args = ( self.planesID, removeDoArgs )
			globalBaseMB.globalCallEntityCellMothod( entityID, "onLeaveTrapRemoteDo", args )
	
	def onLevelTrapPickRemoteDo( self ):
		"""
		virtual method.
		entity�������ڴ��ͣ��������ߵĵ��ã�destroy����Ϊtrue��ʱ��
		��ʽ��[ ( ��������, [����1�� ����2����] ), ( ��������, [����1�� ����2����] ), �� ]
		"""
		return []
	
	def onLeaveTrapRemoteDo( self, planesID, args ):
		"""
		define method.
		Զ���뿪����ִ��
		"""
		if self.planesID == planesID and len( args ):
			for methodInfo in args:
				methodName = methodInfo[ 0 ]
				methodArgs = methodInfo[ 1 ]
				method = getattr( self, methodName )
				method( *methodArgs )
		

	def planesAllClients( self, clientMethod, args ):
		"""
		�������Χ��entity�ͻ��˷���Ϣ
		"""
		roles = self.entitiesInRangeExt( csconst.ROLE_AOI_RADIUS, "Role" )
		roles.append( self ) #����Լ�
		for role in roles:
			client = role.clientEntity( self.id )
			getattr( client, clientMethod )( *args )
	
	def planesOtherClients( self, clientMethod, args ):
		"""
		����Χ���Լ���Ŀͻ��˷���Ϣ
		"""
		roles = self.entitiesInRangeExt( csconst.ROLE_AOI_RADIUS, "Role" )
		for role in roles:
			client = role.clientEntity( self.id )
			getattr( client, clientMethod )( *args )
	
# GameObject.py

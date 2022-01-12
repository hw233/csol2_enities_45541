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

# Extra全局数据By wsf
import inspect
g_extraClsNameTuple = ( "Monster", "GameObject", "NPCObject" )		# EXTRA提供支持的脚本类名列表
g_clsNameMap = {}										# 服务器运行过程中生成的临时映射


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
		@return: 返回自己的全局公共类
		@rtype:  instance
		"""
		if len( self.className ):
			return g_objFactory.getObject( self.className )
		#ERROR_MSG( "%s:%s(%i): my className is NULL." % (self.__class__.__name__, self.getName(), self.id) )
		return None

	def isEntityType( self, etype ) :
		"""
		判断是否是某种类型( hyw )
		@type		etype : MACRO DEFINATION
		@param		etype : entity 类型
		@rtype			  : bool
		@return			  : 如果是 etype 则返回 True
		"""
		return self.utype == etype

	def getEntityType( self ):
		"""
		取得自己的entity类型

		@rtype:  INT8
		"""
		return self.utype

	def setEntityType( self, type ):
		"""
		virtual method.
		设置自己的entity类型
		"""
		self.utype = type

	def getEntityTypeName( self ):
		"""
		获取产生entity实例的基础类名，也就是entity.__class__.__name__

		@return: STRING
		"""
		return self.__class__.__name__


	# -------------------------------------------------
	# flags about
	# -------------------------------------------------
	def setFlag( self, flag ):
		"""
		重新设置标志

		@param flag: ENTITY_FLAG_* 左移后组合的值
		@type  flag: INT
		"""
		self.flags = flag

	def addFlag( self, flag ):
		"""
		重新设置标志

		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		"""
		flag = 1 << flag
		self.flags |= flag

	def removeFlag( self, flag ):
		"""
		重新设置标志

		@param flag: ENTITY_FLAG_*
		@type  flag: INT
		"""
		# 第32位不使用，那是标志位，如果使用了则必须要用UINT32，当前用的是INT32
		# 不使用UINT32的其中一个原因是我们可能不会有这么多标志，
		# 另一个原因是如果使用UINT32，python会使用是INT64来保存这个值

		# 第0位系统保留，第32位不能用，现在要加个31的标记，长度已不够用，需要将数据类型改为INT64 by chenweilan
		flag = 1 << flag
		self.flags &= flag ^ 0x7FFFFFFFFFFFFFFF

	def hasFlag( self, flag ):
		"""
		判断一个entity是否有指定的标志
		禁止直接编辑该方法，请到下层模块中修改。

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
		根据关键字查询临时mapping中与之对应的值
		禁止直接编辑该方法，请到下层模块中修改。

		@return: 如果关键字不存在则返回default值
		"""
		return GOBJ_CPP_OPTIMIZE.queryTemp(self, key, default)


	def setTemp( self, key, value ):
		"""
		define method.
		往一个key里写一个值
		禁止直接编辑该方法，请到下层模块中修改。

		@param   key: 任何PYTHON原类型(建议使用字符串)
		@param value: 任何PYTHON原类型(建议使用数字或字符串)
		"""
		GOBJ_CPP_OPTIMIZE.setTemp(self, key, value)


	def popTemp( self, key, default = None ):
		"""
		移除并返回一个与key相对应的值
		"""
		return self.tempMapping.pop( key, default )

	def removeTemp( self, key ):
		"""
		define method.
		移除一个与key相对应的值
		@param   key: 任何PYTHON原类型(建议使用字符串)
		"""
		self.tempMapping.pop( key, None )

	def addTempInt( self, key, value ):
		"""
		放一个key相对应的值里加一个值；
		注意：此方法并不检查源和目标的值是否匹配或正确
		"""
		v = self.queryTempInt( key )
		self.setTemp( key, value + v )

	def queryTempInt( self, key ):
		"""
		根据关键字查询临时mapping中与之对应的值

		@return: 如果关键字不存在则返回0
		"""
		try:
			return self.tempMapping[key]
		except KeyError:
			return 0

	def queryTempStr( self, key ):
		"""
		根据关键字查询临时mapping中与之对应的值

		@return: 如果关键字不存在则返回空字符串""
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
		AI思考
		"""
		pass

	def think( self, delay = 0.0 ):
		"""
		设置心跳。
		@param delay:	等待下次触发think的时间，如果delay为0则立即触发
		@type  delay:	FLOAT
		"""
		if delay > 0.0:
			if self.thinkControlID < 0:	# 当thinkControlID值小于0时表示不再think，除非此值不再小于0
				return
			t = BigWorld.time()
			if self.thinkControlID != 0:
				if self.thinkWaitTime - t <= delay:
					return	# 当前剩余时间如果小于新的触发等待时间，则使用当前timer。
				self.cancel( self.thinkControlID )
			self.thinkWaitTime = t + delay
			self.thinkControlID = self.addTimer( delay, 0.0, ECBExtend.THINK_TIMER_CBID )
		else:
			# stop if we waiting think
			if self.thinkControlID > 0:
				self.cancel( self.thinkControlID )
				self.thinkControlID = 0
			elif self.thinkControlID < 0:	# 当thinkControlID值小于0时表示不再think，除非此值不再小于0
				return
			self.onThink()

	def pauseThink( self, stop = True ):
		"""
		中止/开启think行为；
		think行为被中止以后除非再次开启，否则所有对think的调用行为都会被忽略。
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
		取得entity当前所在的space的space entity base
		@return: 如果找到了则返回相应的base，找不到则返回None.
				找不到的原因通常是因为space处于destoryed中，而自己还没有收到转移通知或destroy.
		"""
		try:
			return BigWorld.cellAppData["spaceID.%i" % self.spaceID]
		except KeyError:
			return None
	
	def getCurrentSpaceCell( self ):
		"""
		取得entity当前所在的space的space entity base
		@return: 如果找到了则返回相应的base，找不到则返回None.
				找不到的原因通常是因为space处于destoryed中，而自己还没有收到转移通知或destroy.
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
		获取当前所在space的类型 具体看csdefine.SPACE_TYPE_*
		"""
		try:
			return int( BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) )
		except ValueError:
			return csdefine.SPACE_TYPE_NORMAL

	def getCurrentSpaceLineNumber( self ):
		"""
		获取当前所在space的线数 如果返回0， 则表示地图不支持多线。
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
		取得SpaceManager的base mailbox
		@return: SpaceManager的base mailbox
		"""
		return BigWorld.globalData["SpaceManager"]	# 如果产生了异常就表示有BUG

	def requestNewSpace( self, spaceType, mailbox ):
		"""
		向spaceManager要求创建一个新的空间
		@param spaceType:	空间名，空间的关键字
		@type spaceType:	string
		@param mailbox:	实体mailbox: 空间创建完成后通知的实体mailbox 这个Mailbox上必需有onRequestCell方法
		@type mailbox:	mailbox
		"""
		space = g_objFactory.getObject( spaceType )
		self.getSpaceManager().requestNewSpace( spaceType, mailbox, space.packedDomainData( self ) )

	def getCurrentSpaceScript( self ):
		"""
		获取当前space object script
		"""
		return g_objFactory.getObject( self.spaceType )

	# -------------------------------------------------
	# misc
	# -------------------------------------------------
	def createNPCObject( self, npcID, position, direction, state ):
		"""
		define method
		(远程)创建一个非玩家控制对象，被创建的entity将与被调用者在同一space上。

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		self.createObjectRemote( npcID, self.spaceID, position, direction, state )

	def createObjectNear( self, npcID, position, direction, state ):
		"""
		virtual method.
		创建一个entity, 近距离
		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		return g_objFactory.createEntity( npcID, self.spaceID, position, direction, state )
	
	def createObjectNearPlanes( self, npcID, position, direction, state ):
		"""
		virtual method.
		创建一个entity, 并保持新建entity与当前entity同一位面
		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		state[ "planesID" ] = self.planesID
		return self.createObjectNear( npcID, position, direction, state )
		
	def createObjectRemote( self, npcID, spaceID, position, direction, state ):
		"""
		define method.远程调用
		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		g_objFactory.createEntity( npcID, spaceID, position, direction, state )
	
	def createEntityNear( self, entityType, position, direction, state ):
		"""
		virtual method.
		创建一个entity, 近距离
		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		return BigWorld.createEntity( entityType, self.spaceID, position, direction, state )
	
	def createEntityNearPlanes( self, entityType, position, direction, state ):
		"""
		virtual method.
		创建一个entity, 近距离
		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: new entity
		"""
		state[ "planesID" ] = self.planesID
		return self.createEntityNear( entityType, position, direction, state )
	
	def createEntityRemote( self, entityType, spaceID, position, direction, state ):
		"""
		define method.远程调用
		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		BigWorld.createEntity( entityType, spaceID, position, direction, state )


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
			ERROR_MSG( "%s(%i): class %s has no method %s." % (self.getName(), self.id, self.__class__.__name__, name) )
			return
		#DEBUG_MSG( "remoteCall: name=%s, args=%s" % ( name, str(args) ) )
		method( *args )

	def forwardCall( self, entityID, name, args ):
		"""
		define method.
		远程方法调用转发，以此接口所属的entity为realEntity，调用entityID所指定的entity身上的某个方法；
		此方法主要用于简化使用次数不多的脚本中的特定功能代码。

		@param entityID: OBJECT_ID; 要调用方法的entity，如果entity找不到则忽略此次调用。
		@param name: STRING; 要调用的方法名称
		@param args: PY_ARGS; 被调用方法的参数列表，具体参数个数由各方法自行处理；
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
		远程方法调用转发，以此接口所属的entity为realEntity，调用scriptName所指定的全局脚本上的某个方法；
		此方法主要用于简化使用次数不多的脚本中的特定功能代码。
		它特别适用于在当前方法所属的entity的cellapp中找不到指定的entity，但又想调用该entity所对应的脚本的情况。

		@param scriptName: STRING; 要调用方法的脚本名(className)，如果entity找不到则忽略此次调用。
		@param name: STRING; 要调用的方法名称
		@param args: PY_ARGS; 被调用方法的参数列表，具体参数个数由各方法自行处理；
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
		远程脚本方法调用，以此接口所属的entity为realEntity，调用自己相关联的脚本上的某个方法；
		此方法主要用于简化使用次数不多的脚本中的特定功能代码。

		@param name: STRING; 要调用的方法名称
		@param args: PY_ARGS; 被调用方法的参数列表，具体参数个数由各方法自行处理；
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
		返回代表自身的bounding box的长、高、宽的Vector3实例
		如果自身的模型有被缩放过，需要提供缩放后的值。

		@return: Vector3
		"""
		return Math.Vector3( ( 0.0, 0.0, 0.0 ) )

	def getDownToGroundPos( self ):
		"""
		获取此Entity.position对应的地面点 by mushuang
		禁止直接编辑该方法，请到下层模块中修改。
		"""
		return GOBJ_CPP_OPTIMIZE.getDownToGroundPos(self)


	def distanceBB( self, destEntity ):
		"""
		计算与目标entity的boundingbox边界之间的3D坐标系的距离
		禁止直接编辑该方法，请到下层模块中修改。

		@return: float
		"""
		if destEntity.__class__.__name__ != "MonsterBuilding":
			return GOBJ_CPP_OPTIMIZE.distanceBB(self, destEntity)
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

	def sysBroadcast( self, msg ) :
		"""
		defined method
		在系统广播频道中广播一条消息
		hyw--2009.06.30
		"""
		self.getGBAE().globalChat( csdefine.CHAT_CHANNEL_SYSBROADCAST, self.id, self.getName(), msg, [] )		# GBEA 一定存在，否则所有 base 服务器都已经挂掉

	def getGBAE( self ) :
		"""
		获取保存在globalData中的baseMailbox
		"""
		return BigWorld.globalData[ csconst.C_PREFIX_GBAE ]

	def requestEntityData( self, srcEntityID, targetEntityID, taskType, isLastTask ):
		"""
		Expose method.
		玩家客户端像服务器请求获取某entity的数据信息。
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
		for entity extra.注意：提供给Entity Extra调用，方便获得entity对应的extra信息。
		获得映射到Extra支持的类名，以便做相应的Extra初始化。14:06 2012-12-26 by wangshufeng。
		"""
		global g_clsNameMap
		global g_extraClsNameTuple
		tempClsList = []

		extraClassName = self.__class__.__name__
		for classType in inspect.getmro( self.__class__ ):
			if not issubclass( classType, BigWorld.Entity ):	# 过滤掉非entity class
				continue
			className = classType.__name__
			if g_clsNameMap.has_key( className ):
				extraClassName = g_clsNameMap[className]
				break
			tempClsList.append( className )
			if className in g_extraClsNameTuple:
				extraClassName = className
				break

		# 继承树上所有检测过的className都对应到extraClassName
		for temp in tempClsList:
			g_clsNameMap[temp] = extraClassName
		return extraClassName

	# ----------------------------------------------------------------
	# planes
	# ----------------------------------------------------------------
	def isSamePlanes( self, entity ):
		"""
		是否同一位面
		"""
		return self.isSamePlanesExt( entity ) #cellExtra
	
	def addProximityExt( self, range, userData = 0):
		"""
		创建一个陷阱
		"""
		return self.addProximity( range, userData )
	
	def onEnterTrap( self, entityEntering, range, controllerID ):
		"""
		有entity触发陷阱
		"""
		if not entityEntering.isDestroyed and self.isSamePlanes( entityEntering ):#只有同一位面ID的玩家才会触发
			self.onEnterTrapExt( entityEntering, range, controllerID )
		
	def onEnterTrapExt( self, entityEntering, range, controllerID ):
		"""
		virtual method.
		有entity触发陷阱
		"""
		pass
	
	def onLeaveTrap( self, entityLeaving, range, controllerID ):
		"""
		有entity离开陷阱
		"""
		if self.isDestroyed:
			return
			
		if not entityLeaving.isDestroyed:
			if self.isSamePlanes( entityLeaving ): #只有同一位面ID的玩家才会触发
				self.onLeaveTrapExt( entityLeaving, range, controllerID )
		else:
			self.__onLevelTrapPickRemove( entityLeaving.id )
	
	def onLeaveTrapID( self, entityID, range, userData ):
		"""
		离开trap, 已经传送到别的cellapp调用,引擎方法
		"""
		
		self.__onLevelTrapPickRemove( entityID )
	
	def onLeaveTrapExt( self, entityLeaving, range, controllerID ):
		"""
		virtual method.
		普通离开陷阱触发
		"""
		pass
	
	def __onLevelTrapPickRemove( self, entityID ):
		"""
		离开陷阱entity的destroy属性为True的时候处理
		"""
		if self.isDestroyed:
			return
		
		removeDoArgs = self.onLevelTrapPickRemoteDo()
		if removeDoArgs: #如果没有做操作就不要去远程调用了
			globalBaseMB = self.getGBAE()
			if globalBaseMB is None :
				ERROR_MSG( "The globalBaseMB should not be None, or all of that must have been breakdown!" )
				return
				
			args = ( self.planesID, removeDoArgs )
			globalBaseMB.globalCallEntityCellMothod( entityID, "onLeaveTrapRemoteDo", args )
	
	def onLevelTrapPickRemoteDo( self ):
		"""
		virtual method.
		entity在陷阱内传送，或者下线的调用（destroy属性为true的时候）
		格式：[ ( 方法名字, [参数1， 参数2……] ), ( 方法名字, [参数1， 参数2……] ), … ]
		"""
		return []
	
	def onLeaveTrapRemoteDo( self, planesID, args ):
		"""
		define method.
		远程离开陷阱执行
		"""
		if self.planesID == planesID and len( args ):
			for methodInfo in args:
				methodName = methodInfo[ 0 ]
				methodArgs = methodInfo[ 1 ]
				method = getattr( self, methodName )
				method( *methodArgs )
		

	def planesAllClients( self, clientMethod, args ):
		"""
		给玩家周围的entity客户端发消息
		"""
		roles = self.entitiesInRangeExt( csconst.ROLE_AOI_RADIUS, "Role" )
		roles.append( self ) #添加自己
		for role in roles:
			client = role.clientEntity( self.id )
			getattr( client, clientMethod )( *args )
	
	def planesOtherClients( self, clientMethod, args ):
		"""
		给周围除自己外的客户端发消息
		"""
		roles = self.entitiesInRangeExt( csconst.ROLE_AOI_RADIUS, "Role" )
		for role in roles:
			client = role.clientEntity( self.id )
			getattr( client, clientMethod )( *args )
	
# GameObject.py

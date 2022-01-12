# -*- coding: gb18030 -*-
"""
场景基类
"""
import BigWorld
import time

from interface.GameObject import GameObject

import SpawnPointScript

from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objFactory = GameObjectFactory.instance()
from bwdebug import *
from WatchDog import WatchDog
import Language

import Love3
import Const
import csconst

WATCH_KEY_CELL = "C-CELL: %s, %i"
# player id, space name, space number, time
TELEPORT_KEY = "SPACE WATCH DOG: player teleports over.[player id %i, space %s, space number %i, at %f]"

PROCESS_ENTER_TIMERCB 			= 1002

class SpaceNormal( BigWorld.Base, GameObject ):
	"""
	标准场景。
	@ivar domainMB:			一个声明的属性，记录了它的领域空间mailbox，用于某些需要通知其领域空间的操作，此接口如果为None则表示当前不可使用
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		super( SpaceNormal, self ).__init__()
		self.spaceNumber	= self.cellData["spaceNumber"]	# 空间的ID	: 	类型int32，来自创建时传递。
		self.__currSpawnID	= 0								# 临时变量	:	用于场景初始化时记录当前加载的spawnPoint索引
		self._shouldDestroy = False							# 临时变量，用于决定当收到onLoseCell()消息时是否destroy space
		self._shouldDeleteFromDB = False					# 临时变量，用于决定当收到onLoseCell()消息时且_shouldDestroy为True时，是否要把space从数据库删除
		self._deleteID 		= 0								# 空间退出timer
		self._players 		= {}							# 记录当前在此space的玩家 {entityID : entityMailbox, ...}
		self.params			= self.cellData["params"]
		self.domainMB		= self.cellData["domainMB"]
		self.createTime = time.time()

		# 记录cell entity所在的spaceID，
		# 用于SpaceFace::cell::teleportToSpace()判断目标地图与源地图是否是同一地图。
		# 默认值 -1，表示还未获得spaceID，也未获得cell component
		# 值 -2，表示已获得cell component——onGetCell()被调用，但还未获得spaceID
		# 值 >= 0，表示已获得相应的spaceID
		self.spaceID		= -1

		self._enters = []
		self._logons = []
		self._creates = []
		self._processPlayerEnterTimer = 0
		
		self.isSpawnPointLoaderOver = False

		# 注册存在别名的spawPoint
		self._loadSpawnPointAlias	= {}
		self.registerSpawnPointAlias( "MonsterSpawnPoint", "SpawnPoint" )
		self.registerSpawnPointAlias( "NPCSpawnPoint", "SpawnPoint" )

		# 注册要加载的entity的类别
		self.loadEntityUseFunc = {}
		self.registerLoadEntityType( "NPCObject" )
		self.registerLoadEntityType( "QuestBox" )
		self.registerLoadEntityType( "CollectPoint" )
		self.registerLoadEntityType( "QuestBoxTrap" )
		
		# 注册要加载的特殊 entity的类别
		self.registerSpecialLoadEntityType( "AreaRestrictTransducer" )
		self.registerSpecialLoadEntityType( "SpaceDoor" )
		self.registerSpecialLoadEntityType( "SpaceDoorLiuWangMu" )
		
		self.monsterCount = 0								#当前地图的怪物数量
		self.monsterCountCheckNumber = 1000					#当怪物数量达到一定值时，提出警告

		self.wd = WatchDog()

	#-----------------------------------------------
	# 进入、离开， Space entity的创建、销毁流程
	#-----------------------------------------------
	def checkPlayerEnterTimer( self, delay = 0.5 ):
		"""
		检查是否应该启动timer 用来隔一段时间将enter队列里的玩家传入副本
		"""
		if self._processPlayerEnterTimer == 0:
			self._processPlayerEnterTimer = self.addTimer( delay, 0.1, PROCESS_ENTER_TIMERCB )

	def pushPlayerToEnterList( self, position, direction, playerbase, pickData ):
		"""
		压入等待进入的玩家
		"""
		self._enters.append( ( position, direction, playerbase, pickData ) )
		self.checkPlayerEnterTimer()
		
	def registerLogonPlayer( self, playerbase ):
		"""
		注册在这个space登陆的玩家
		"""
		self._logons.append( playerbase )
		self.checkPlayerEnterTimer()

	def registerCreatePlayer( self, playerbase ):
		"""
		注册手动创建这个副本的玩家
		"""
		self._creates.append( playerbase )
		self.checkPlayerEnterTimer()

	def createCell( self ):
		"""
		define method.
		创建space cell部分
		"""
		INFO_MSG("%s space %d(%i) create cell."%( self.className, self.spaceNumber, self.id ) )
		if not hasattr( self, "cell" ):
			self.wd.watch(WATCH_KEY_CELL % (self.className, self.spaceNumber))
			self.createInNewSpace()		# 创建空间 创建cell

	def onGetSpaceID( self, spaceID ):
		"""
		defined method.
		由cell通报自身在哪个space中

		@param spaceID: CellEntity.spaceID
		"""
		INFO_MSG("%s space %d(%i) got spaceID %i."%( self.className, self.spaceNumber, self.id, spaceID ) )
		assert self.spaceID < 0
		s = self.spaceID
		self.spaceID = spaceID
		if s == -2:
			# space cell 创建完成通报，必须等拿到spaceID后再通知
			INFO_MSG("%s space %d(%i) got cell and spaceID %i, notify to domain space."%( self.className, self.spaceNumber, self.id, self.spaceID ) )
			self.domainMB.onSpaceGetCell( self.spaceNumber )
			self.wd.release(WATCH_KEY_CELL % (self.className, self.spaceNumber))

	def registerPlayer( self, baseMailbox ):
		"""
		注册进入此space的mailbox和玩家名称
		"""
		self._players[ baseMailbox.id ] = baseMailbox

	def unregisterPlayer( self, baseMailbox ):
		"""
		取消该玩家的记录
		"""
		if self._players.has_key( baseMailbox.id ):
			self._players.pop( baseMailbox.id )

	def getCurrentPlayerCount( self ):
		"""
		获得当前space上玩家的数量
		"""
		return len( self._players )

	def checkSpaceFull( self ):
		"""
		检测空间满员状态
		baseMailbox.client.spaceMessage( csstatus.SPACE_MISS_MEMBER_FULL )
		"""
		if len( self._players ) >= self.maxPlayer:
			return False
		return True

	def banishPlayer( self ):
		"""
		驱赶空间里的所有玩家
		"""
		INFO_MSG( "start banish the all player in the space ..." )
		for baseMailBox in self._players.itervalues():
			baseMailBox.cell.gotoForetime()
		
	def onProcessEnterTimer( self, timerID ):
		"""
		检查进入
		"""
		if len( self._creates ) > 0:
			self.requestCellComponent( self._creates.pop( 0 ) )
		elif len( self._logons ) > 0:
			self.entityCreateCell( self._logons.pop( 0 ) )
		elif len( self._enters ) > 0:
			position, direction, playerBase, pickData = self._enters.pop( 0 )
			if pickData.get( "gotoPlane", False ): #判断是否进入位面
				self._teleportEntityToPlanes( position, direction, playerBase, pickData )
			else:
				self._teleportEntity( position, direction, playerBase, pickData )
		if (self._enters) <= 0:   #只有列表为空时才取消，不然会造成队伍传送，只传送一人的bug
			self._processPlayerEnterTimer = 0
			self.delTimer( timerID )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		self.registerPlayer( baseMailbox )		# 记录进入该副本的玩家的mailbox
		self.getScript().onEnter( self, baseMailbox, params )

		print TELEPORT_KEY % (baseMailbox.id, self.className, self.spaceNumber, BigWorld.time())

	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		玩家离开空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onLeave时的一些额外参数
		@type params: py_dict
		"""
		self.unregisterPlayer( baseMailbox )
		self.getScript().onLeave( self, baseMailbox, params )

	def closeSpace( self, deleteFromDB = True ):
		"""
		define method.
		destroy space的唯一入口，所有的space删除都应该走此接口；
		space生命周期结束，删除space
		"""
		INFO_MSG("%s space %d(%i) close. spaceID: %s."%( self.className, self.spaceNumber, self.id, self.spaceID ) )

		if hasattr( self, "cell" ):
			# 如果cell部份还存在则必须在onLostCell()中执行销毁动作
			self._shouldDestroy = True
			self._shouldDeleteFromDB = deleteFromDB
			self.onBeforeDestroyCellEntity()
			self.destroyCellEntity()
		else:
			self.__onClose()
			self.destroy( deleteFromDB = deleteFromDB )

	def __onClose( self ):
		"""
		space关闭（destroy）时执行的一些额外事情。
		如向自己的领域发出通知，注销对spaceNumber的占用，调用脚本执行额外事情等
		"""
		self.getScript().onCloseSpace( self )

		if self.domainMB:
			self.domainMB.onSpaceCloseNotify( self.spaceNumber )

		self.getSpaceManager().removeSpaceNumber( self.spaceNumber )

	def entityCreateCell( self, playerBase ):
		"""
		define method.
		让玩家在该空间创建cell
		@param playerBase	:	玩家Base
		@type playerBase	:	mailbox
		"""
		try:
			playerBase.createCellFromSpace( self.cell )
		except:
			EXCEHOOK_MSG( "createCellFromSpace is error!", \
						self.getScript().getClassName(), \
						self.spaceNumber, \
						self.__currSpawnID, \
						self._shouldDestroy, \
						self._shouldDeleteFromDB, \
						self._deleteID, \
						self._players, \
						self.params, \
						self.domainMB )
						
	#-------------------------------------------------
	# 关于Spawn file
	#-------------------------------------------------
	def registerSpawnPointAlias( self, configSpawnPointType, spawnPointEntityAlias ):
		"""
		注册要创建的SpawnPoint别名
		@param	configSpawnPointType	: SpawnPoint的在配置中的类别
		@type 	configSpawnPointType	: String
		@param	SpawnPointEntityAlias	: SpawnPoint的脚本类别
		@type 	SpawnPointEntityAlias	: String
		"""
		self._loadSpawnPointAlias[ configSpawnPointType ] = spawnPointEntityAlias
	
	def registerLoadEntityType( self, entityType ):
		"""
		注册要创建的entity 类别
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		"""
		self.loadEntityUseFunc[ entityType ] = self._createEntityFactory
	
	def registerSpecialLoadEntityType( self, entityType ):
		"""
		注册要创建的entity 类别
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		"""
		self.loadEntityUseFunc[ entityType ] = self._createEntityDirect

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		pass

	def initLoadEntityParams( self, params ):
		"""
		virtual method.
		初始化要创建的entity的参数,
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	params			: 底层已经给出的默认创建参数
		@type 	params			: dict
		"""
		return params

	def checkNeedSpawn( self, sec ):
		"""
		virtual method.
		检查是否需要创建出生点
		"""
		# ignore client only entity
		if sec.readBool( "clientOnly" ):
			return False

		# ignore custom patrol entity
		if sec["type"].asString in csconst.CLIENT_ENTITY_TYPE:
			return False

		return True
	
	def createSpawnPoint( self ):
		"""
		出生点加载
		@return: BOOL
			True:		还没有加载完
			False:		加载完毕
		"""
		spawnFile = self.getScript().getSpaceSpawnFile( self )
		section = self.getScript().getSpawnSection()

		if section is None:
			ERROR_MSG( "spawn file %s not found." % spawnFile )
			self.onSpawnPointLoadedOver( Const.SPACE_LOADSPAWN_RET_NOT_FOUND_FILE )
			return False

		childs = len( section )

		while self.__currSpawnID < childs:
			sec = section.child( self.__currSpawnID )
			# 检查是否需要创建出生点
			if not self.checkNeedSpawn( sec ):
				self.__currSpawnID += 1
				continue

			entityType = sec["type"].asString
			if entityType == "":
				continue
				
			matrix = sec["transform"].asMatrix
			try:
				e = self._createOneSpawnEntity( entityType, sec, matrix )
			except RuntimeError, err:
				# RuntimeError: Unable to allocate id
				# 这种问题表示服务器临时不够entity id使用了，因此我们需要等待下一次的分配
				# 当然，当前暂时不考虑entity id由于长时间运行后真正不够的情况
				EXCEHOOK_MSG("Create spawn point wrong - RuntimeError")
				return True
			except:
				# 有可能是由于配置错误引起的错误，只输出一个日志
				EXCEHOOK_MSG("Create spawn point wrong")
			else:
				self.onLoadedEntity( entityType, e )

			self.__currSpawnID += 1
			if ( self.__currSpawnID % 5 ) == 0:
				break

		if self.__currSpawnID == childs:
			INFO_MSG( "spawn file %s loaded over. total entity: %i" % ( self.getScript().getSpaceSpawnFile( self ), self.__currSpawnID ) )
			self.onSpawnPointLoadedOver( Const.SPACE_LOADSPAWN_RET_OVER )
			return False
		else:
			return True
	
	def _createOneSpawnEntity( self, entityType, sec, matrix ):
		"""
		创建一个spawn entity, 这里的entity指的不一定是SpawnPoint，还有直接创建的有base的entity
		"""
		func = self.loadEntityUseFunc.get( entityType, None ) #这里只配置不使用SpawnPoint的
		if not func: #如果是是none，则认为默认使用spawnPoint的方式刷出
			func = self._createEntitySpawnPoint
			
		self._recordSpawnInfos( entityType, sec, matrix )
		
		return func( entityType, sec, matrix )
				
	def _createEntityDirect( self, entityType, section, matrix ):
		"""
		直接创建普通的entity
		"""
		newEntity = BigWorld.createBaseLocally(
				entityType,
				section[ "properties" ],
				createOnCell = self.cell,
				position = matrix.applyToOrigin(),
				direction = (matrix.roll, matrix.pitch, matrix.yaw)
			)
		return newEntity
	
	def _createEntityFactory( self, entityType, section, matrix ):
		"""
		直接创建entity， 通过GameObjectFactory创建
		"""
		params = {	"PYDATASECTION"	: section[ "properties" ],
					"createOnCell"	: self.cell,
					"position"		: matrix.applyToOrigin(),
					"direction"		: ( matrix.roll, matrix.pitch, matrix.yaw ),
				}
		
		newEntity = g_objFactory.createLocalBase( section.readString( "properties/className" ), self.initLoadEntityParams( params ) )
		return newEntity
	
	def _createEntitySpawnPoint( self, entityType, section, matrix ):
		"""
		通过SpawnPoint来控制entity的创建（这里是创建SpawnPoint）
		"""
		createType = ""
		if entityType in self._loadSpawnPointAlias:
			createType = self._loadSpawnPointAlias[ entityType ]
		else:
			createType = entityType
			
		newEntity = SpawnPointScript.createEntity( createType, section[ "properties" ], self, matrix.applyToOrigin(), (matrix.roll, matrix.pitch, matrix.yaw) )
		return newEntity
	
	def _recordSpawnInfos( self, entityType, section, matrix ):
		"""
		记录刷出entity的数据，用于类似怪物恢复的功能
		"""
		pass
	
	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		self.isSpawnPointLoaderOver = True
	
	#--------------------------------------
	# space公用消息接口
	#--------------------------------------
	def onWriteToDBComplete( self, success, base ):
		"""
		Write To DataBase Events
		"""
		if success:
			if self.domainMB:	# space 存盘通报
				self.domainMB.onSpaceWriteToDBNotify( self.spaceNumber, self.databaseID )
		else:
			ERROR_MSG( "space Write to Database Error!" )

	def requestCellComponent( self, mailbox ):
		"""
		define method.
		请求cell mailbox
		@param mailbox:	实体mailbox: 空间创建完成后通知的实体mailbox 这个Mailbox上必需有onRequestCell方法
		@type mailbox:	mailbox
		"""
		# 这里返回 cellmailbox and basemailbox 是因为在cell上 创建者有需求获得该entity的base做为存储后使用，
		# 在cell上 如果只用self.cell.base 在2个entity不在同一个cell上时 是会出现错误的， 因此这里返回一个真实的base
		mailbox.onRequestCell( self.cell, self )

	def teleportEntity( self, position, direction, baseMailbox, pickData ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		self.pushPlayerToEnterList( position, direction, baseMailbox, pickData )

	def _teleportEntity( self, position, direction, baseMailbox, pickData ):
		"""
		传送一个entity到指定的space中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		self.getScript().onSpaceTeleportEntity( self, position, direction, baseMailbox, pickData )
	
	def _teleportEntityToPlanes( self, position, direction, baseMailbox, pickData ):
		"""
		普通地图用进入位面，不是真的进入一个位面，只是为了让它不读图，作用仅此而已
		传送一个entity到指定的space位面中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		self.getScript().onPlanesTeleportEntity( self, position, direction, baseMailbox, pickData, 0 ) #不是位面地图，默认的planesID=0

	def createNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(远程)创建一个非玩家控制对象 该对象拥有base部分

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		self.createNPCObject( self.cell, npcID, position, direction, state )

	def onChatChannelMessage( self, channelID, spkID, spkName, msg, blobArgs ) :
		"""
		defined method
		处理一条频道消息，将他发给所有本space上的玩家
		@type				channelID	: UINT32
		@param				channelID	: 频道 ID
		@param				spkID		: OBJECT_ID
		@type				spkID		: 发言者 entityID
		@param				spkName 	: 源说话者名字
		@type				spkName		: STRING
		@type				msg		 	: STRING
		@param				msg		 	: 消息内容
		"""
		for e in self._players.itervalues():
			e.client.chat_onChannelMessage( channelID, spkID, spkName, msg, blobArgs )

	def onBeforeDestroyCellEntity( self ):
		"""
		删除cell entity 前，做一些事情
		"""
		pass

	def addMonsterCount( self ):
		"""
		define method
		"""
		self.monsterCount += 1
		if self.monsterCount % self.monsterCountCheckNumber == 0:
			WARNING_MSG("Space(%s) monster count more than %i"%(self.className, self.monsterCount ))
			
	def subMonsterCount( self ):
		"""
		define method
		"""
		self.monsterCount -= 1
		
	def allPlayersRemoteCall( self, rFuncName, args ):
		"""
		define method
		地图内所有玩家调用cell某方法
		"""
		for e in self._players.itervalues():
			getattr( e.cell, rFuncName )( *args )
	
	#---------------------------------------------------------------------
	#引擎回调
	#---------------------------------------------------------------------
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == PROCESS_ENTER_TIMERCB:
			self.onProcessEnterTimer( id )
			return
	
	def onLoseCell( self ):
		"""
		CELL死亡
		"""
		self.__currSpawnID = 0
		self.domainMB.onSpaceLoseCell( self.spaceNumber )
		if self._shouldDestroy:
			self.__onClose()
			self.destroy( deleteFromDB = self._shouldDeleteFromDB )

	def onGetCell( self ):
		"""
		cell实体创建完成通知，回调callbackMailbox.onSpaceComplete，通知创建完成。
		"""
		# create spawn point into this space on other thread.
		if len( self.getScript().getSpaceSpawnFile( self ) ) == 0:
			self.onSpawnPointLoadedOver( Const.SPACE_LOADSPAWN_RET_OPEN_FILE_ERROR )
		else:
			Love3.g_spawnLoader.registerSpace( self )		# 加到队列中

		# space cell 创建完成通报，必须等拿到spaceID后再通知
		if self.spaceID >= 0:
			INFO_MSG("%s space %d(%i) got cell and spaceID %i, notify to domain space."%( self.className, self.spaceNumber, self.id, self.spaceID ) )
			self.domainMB.onSpaceGetCell( self.spaceNumber )
			self.wd.release(WATCH_KEY_CELL % (self.className, self.spaceNumber))
		else:
			self.spaceID = -2
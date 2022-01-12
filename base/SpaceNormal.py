# -*- coding: gb18030 -*-
"""
��������
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
	��׼������
	@ivar domainMB:			һ�����������ԣ���¼����������ռ�mailbox������ĳЩ��Ҫ֪ͨ������ռ�Ĳ������˽ӿ����ΪNone���ʾ��ǰ����ʹ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		super( SpaceNormal, self ).__init__()
		self.spaceNumber	= self.cellData["spaceNumber"]	# �ռ��ID	: 	����int32�����Դ���ʱ���ݡ�
		self.__currSpawnID	= 0								# ��ʱ����	:	���ڳ�����ʼ��ʱ��¼��ǰ���ص�spawnPoint����
		self._shouldDestroy = False							# ��ʱ���������ھ������յ�onLoseCell()��Ϣʱ�Ƿ�destroy space
		self._shouldDeleteFromDB = False					# ��ʱ���������ھ������յ�onLoseCell()��Ϣʱ��_shouldDestroyΪTrueʱ���Ƿ�Ҫ��space�����ݿ�ɾ��
		self._deleteID 		= 0								# �ռ��˳�timer
		self._players 		= {}							# ��¼��ǰ�ڴ�space����� {entityID : entityMailbox, ...}
		self.params			= self.cellData["params"]
		self.domainMB		= self.cellData["domainMB"]
		self.createTime = time.time()

		# ��¼cell entity���ڵ�spaceID��
		# ����SpaceFace::cell::teleportToSpace()�ж�Ŀ���ͼ��Դ��ͼ�Ƿ���ͬһ��ͼ��
		# Ĭ��ֵ -1����ʾ��δ���spaceID��Ҳδ���cell component
		# ֵ -2����ʾ�ѻ��cell component����onGetCell()�����ã�����δ���spaceID
		# ֵ >= 0����ʾ�ѻ����Ӧ��spaceID
		self.spaceID		= -1

		self._enters = []
		self._logons = []
		self._creates = []
		self._processPlayerEnterTimer = 0
		
		self.isSpawnPointLoaderOver = False

		# ע����ڱ�����spawPoint
		self._loadSpawnPointAlias	= {}
		self.registerSpawnPointAlias( "MonsterSpawnPoint", "SpawnPoint" )
		self.registerSpawnPointAlias( "NPCSpawnPoint", "SpawnPoint" )

		# ע��Ҫ���ص�entity�����
		self.loadEntityUseFunc = {}
		self.registerLoadEntityType( "NPCObject" )
		self.registerLoadEntityType( "QuestBox" )
		self.registerLoadEntityType( "CollectPoint" )
		self.registerLoadEntityType( "QuestBoxTrap" )
		
		# ע��Ҫ���ص����� entity�����
		self.registerSpecialLoadEntityType( "AreaRestrictTransducer" )
		self.registerSpecialLoadEntityType( "SpaceDoor" )
		self.registerSpecialLoadEntityType( "SpaceDoorLiuWangMu" )
		
		self.monsterCount = 0								#��ǰ��ͼ�Ĺ�������
		self.monsterCountCheckNumber = 1000					#�����������ﵽһ��ֵʱ���������

		self.wd = WatchDog()

	#-----------------------------------------------
	# ���롢�뿪�� Space entity�Ĵ�������������
	#-----------------------------------------------
	def checkPlayerEnterTimer( self, delay = 0.5 ):
		"""
		����Ƿ�Ӧ������timer ������һ��ʱ�佫enter���������Ҵ��븱��
		"""
		if self._processPlayerEnterTimer == 0:
			self._processPlayerEnterTimer = self.addTimer( delay, 0.1, PROCESS_ENTER_TIMERCB )

	def pushPlayerToEnterList( self, position, direction, playerbase, pickData ):
		"""
		ѹ��ȴ���������
		"""
		self._enters.append( ( position, direction, playerbase, pickData ) )
		self.checkPlayerEnterTimer()
		
	def registerLogonPlayer( self, playerbase ):
		"""
		ע�������space��½�����
		"""
		self._logons.append( playerbase )
		self.checkPlayerEnterTimer()

	def registerCreatePlayer( self, playerbase ):
		"""
		ע���ֶ�����������������
		"""
		self._creates.append( playerbase )
		self.checkPlayerEnterTimer()

	def createCell( self ):
		"""
		define method.
		����space cell����
		"""
		INFO_MSG("%s space %d(%i) create cell."%( self.className, self.spaceNumber, self.id ) )
		if not hasattr( self, "cell" ):
			self.wd.watch(WATCH_KEY_CELL % (self.className, self.spaceNumber))
			self.createInNewSpace()		# �����ռ� ����cell

	def onGetSpaceID( self, spaceID ):
		"""
		defined method.
		��cellͨ���������ĸ�space��

		@param spaceID: CellEntity.spaceID
		"""
		INFO_MSG("%s space %d(%i) got spaceID %i."%( self.className, self.spaceNumber, self.id, spaceID ) )
		assert self.spaceID < 0
		s = self.spaceID
		self.spaceID = spaceID
		if s == -2:
			# space cell �������ͨ����������õ�spaceID����֪ͨ
			INFO_MSG("%s space %d(%i) got cell and spaceID %i, notify to domain space."%( self.className, self.spaceNumber, self.id, self.spaceID ) )
			self.domainMB.onSpaceGetCell( self.spaceNumber )
			self.wd.release(WATCH_KEY_CELL % (self.className, self.spaceNumber))

	def registerPlayer( self, baseMailbox ):
		"""
		ע������space��mailbox���������
		"""
		self._players[ baseMailbox.id ] = baseMailbox

	def unregisterPlayer( self, baseMailbox ):
		"""
		ȡ������ҵļ�¼
		"""
		if self._players.has_key( baseMailbox.id ):
			self._players.pop( baseMailbox.id )

	def getCurrentPlayerCount( self ):
		"""
		��õ�ǰspace����ҵ�����
		"""
		return len( self._players )

	def checkSpaceFull( self ):
		"""
		���ռ���Ա״̬
		baseMailbox.client.spaceMessage( csstatus.SPACE_MISS_MEMBER_FULL )
		"""
		if len( self._players ) >= self.maxPlayer:
			return False
		return True

	def banishPlayer( self ):
		"""
		���Ͽռ�����������
		"""
		INFO_MSG( "start banish the all player in the space ..." )
		for baseMailBox in self._players.itervalues():
			baseMailBox.cell.gotoForetime()
		
	def onProcessEnterTimer( self, timerID ):
		"""
		������
		"""
		if len( self._creates ) > 0:
			self.requestCellComponent( self._creates.pop( 0 ) )
		elif len( self._logons ) > 0:
			self.entityCreateCell( self._logons.pop( 0 ) )
		elif len( self._enters ) > 0:
			position, direction, playerBase, pickData = self._enters.pop( 0 )
			if pickData.get( "gotoPlane", False ): #�ж��Ƿ����λ��
				self._teleportEntityToPlanes( position, direction, playerBase, pickData )
			else:
				self._teleportEntity( position, direction, playerBase, pickData )
		if (self._enters) <= 0:   #ֻ���б�Ϊ��ʱ��ȡ������Ȼ����ɶ��鴫�ͣ�ֻ����һ�˵�bug
			self._processPlayerEnterTimer = 0
			self.delTimer( timerID )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		��ҽ����˿ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		self.registerPlayer( baseMailbox )		# ��¼����ø�������ҵ�mailbox
		self.getScript().onEnter( self, baseMailbox, params )

		print TELEPORT_KEY % (baseMailbox.id, self.className, self.spaceNumber, BigWorld.time())

	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		����뿪�ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onLeaveʱ��һЩ�������
		@type params: py_dict
		"""
		self.unregisterPlayer( baseMailbox )
		self.getScript().onLeave( self, baseMailbox, params )

	def closeSpace( self, deleteFromDB = True ):
		"""
		define method.
		destroy space��Ψһ��ڣ����е�spaceɾ����Ӧ���ߴ˽ӿڣ�
		space�������ڽ�����ɾ��space
		"""
		INFO_MSG("%s space %d(%i) close. spaceID: %s."%( self.className, self.spaceNumber, self.id, self.spaceID ) )

		if hasattr( self, "cell" ):
			# ���cell���ݻ������������onLostCell()��ִ�����ٶ���
			self._shouldDestroy = True
			self._shouldDeleteFromDB = deleteFromDB
			self.onBeforeDestroyCellEntity()
			self.destroyCellEntity()
		else:
			self.__onClose()
			self.destroy( deleteFromDB = deleteFromDB )

	def __onClose( self ):
		"""
		space�رգ�destroy��ʱִ�е�һЩ�������顣
		�����Լ������򷢳�֪ͨ��ע����spaceNumber��ռ�ã����ýű�ִ�ж��������
		"""
		self.getScript().onCloseSpace( self )

		if self.domainMB:
			self.domainMB.onSpaceCloseNotify( self.spaceNumber )

		self.getSpaceManager().removeSpaceNumber( self.spaceNumber )

	def entityCreateCell( self, playerBase ):
		"""
		define method.
		������ڸÿռ䴴��cell
		@param playerBase	:	���Base
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
	# ����Spawn file
	#-------------------------------------------------
	def registerSpawnPointAlias( self, configSpawnPointType, spawnPointEntityAlias ):
		"""
		ע��Ҫ������SpawnPoint����
		@param	configSpawnPointType	: SpawnPoint���������е����
		@type 	configSpawnPointType	: String
		@param	SpawnPointEntityAlias	: SpawnPoint�Ľű����
		@type 	SpawnPointEntityAlias	: String
		"""
		self._loadSpawnPointAlias[ configSpawnPointType ] = spawnPointEntityAlias
	
	def registerLoadEntityType( self, entityType ):
		"""
		ע��Ҫ������entity ���
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		"""
		self.loadEntityUseFunc[ entityType ] = self._createEntityFactory
	
	def registerSpecialLoadEntityType( self, entityType ):
		"""
		ע��Ҫ������entity ���
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		"""
		self.loadEntityUseFunc[ entityType ] = self._createEntityDirect

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		pass

	def initLoadEntityParams( self, params ):
		"""
		virtual method.
		��ʼ��Ҫ������entity�Ĳ���,
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	params			: �ײ��Ѿ�������Ĭ�ϴ�������
		@type 	params			: dict
		"""
		return params

	def checkNeedSpawn( self, sec ):
		"""
		virtual method.
		����Ƿ���Ҫ����������
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
		���������
		@return: BOOL
			True:		��û�м�����
			False:		�������
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
			# ����Ƿ���Ҫ����������
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
				# ���������ʾ��������ʱ����entity idʹ���ˣ����������Ҫ�ȴ���һ�εķ���
				# ��Ȼ����ǰ��ʱ������entity id���ڳ�ʱ�����к��������������
				EXCEHOOK_MSG("Create spawn point wrong - RuntimeError")
				return True
			except:
				# �п������������ô�������Ĵ���ֻ���һ����־
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
		����һ��spawn entity, �����entityָ�Ĳ�һ����SpawnPoint������ֱ�Ӵ�������base��entity
		"""
		func = self.loadEntityUseFunc.get( entityType, None ) #����ֻ���ò�ʹ��SpawnPoint��
		if not func: #�������none������ΪĬ��ʹ��spawnPoint�ķ�ʽˢ��
			func = self._createEntitySpawnPoint
			
		self._recordSpawnInfos( entityType, sec, matrix )
		
		return func( entityType, sec, matrix )
				
	def _createEntityDirect( self, entityType, section, matrix ):
		"""
		ֱ�Ӵ�����ͨ��entity
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
		ֱ�Ӵ���entity�� ͨ��GameObjectFactory����
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
		ͨ��SpawnPoint������entity�Ĵ����������Ǵ���SpawnPoint��
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
		��¼ˢ��entity�����ݣ��������ƹ���ָ��Ĺ���
		"""
		pass
	
	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		self.isSpawnPointLoaderOver = True
	
	#--------------------------------------
	# space������Ϣ�ӿ�
	#--------------------------------------
	def onWriteToDBComplete( self, success, base ):
		"""
		Write To DataBase Events
		"""
		if success:
			if self.domainMB:	# space ����ͨ��
				self.domainMB.onSpaceWriteToDBNotify( self.spaceNumber, self.databaseID )
		else:
			ERROR_MSG( "space Write to Database Error!" )

	def requestCellComponent( self, mailbox ):
		"""
		define method.
		����cell mailbox
		@param mailbox:	ʵ��mailbox: �ռ䴴����ɺ�֪ͨ��ʵ��mailbox ���Mailbox�ϱ�����onRequestCell����
		@type mailbox:	mailbox
		"""
		# ���ﷵ�� cellmailbox and basemailbox ����Ϊ��cell�� �������������ø�entity��base��Ϊ�洢��ʹ�ã�
		# ��cell�� ���ֻ��self.cell.base ��2��entity����ͬһ��cell��ʱ �ǻ���ִ���ģ� ������ﷵ��һ����ʵ��base
		mailbox.onRequestCell( self.cell, self )

	def teleportEntity( self, position, direction, baseMailbox, pickData ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		self.pushPlayerToEnterList( position, direction, baseMailbox, pickData )

	def _teleportEntity( self, position, direction, baseMailbox, pickData ):
		"""
		����һ��entity��ָ����space��
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		self.getScript().onSpaceTeleportEntity( self, position, direction, baseMailbox, pickData )
	
	def _teleportEntityToPlanes( self, position, direction, baseMailbox, pickData ):
		"""
		��ͨ��ͼ�ý���λ�棬������Ľ���һ��λ�棬ֻ��Ϊ����������ͼ�����ý��˶���
		����һ��entity��ָ����spaceλ����
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		self.getScript().onPlanesTeleportEntity( self, position, direction, baseMailbox, pickData, 0 ) #����λ���ͼ��Ĭ�ϵ�planesID=0

	def createNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(Զ��)����һ������ҿ��ƶ��� �ö���ӵ��base����

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		self.createNPCObject( self.cell, npcID, position, direction, state )

	def onChatChannelMessage( self, channelID, spkID, spkName, msg, blobArgs ) :
		"""
		defined method
		����һ��Ƶ����Ϣ�������������б�space�ϵ����
		@type				channelID	: UINT32
		@param				channelID	: Ƶ�� ID
		@param				spkID		: OBJECT_ID
		@type				spkID		: ������ entityID
		@param				spkName 	: Դ˵��������
		@type				spkName		: STRING
		@type				msg		 	: STRING
		@param				msg		 	: ��Ϣ����
		"""
		for e in self._players.itervalues():
			e.client.chat_onChannelMessage( channelID, spkID, spkName, msg, blobArgs )

	def onBeforeDestroyCellEntity( self ):
		"""
		ɾ��cell entity ǰ����һЩ����
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
		��ͼ��������ҵ���cellĳ����
		"""
		for e in self._players.itervalues():
			getattr( e.cell, rFuncName )( *args )
	
	#---------------------------------------------------------------------
	#����ص�
	#---------------------------------------------------------------------
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == PROCESS_ENTER_TIMERCB:
			self.onProcessEnterTimer( id )
			return
	
	def onLoseCell( self ):
		"""
		CELL����
		"""
		self.__currSpawnID = 0
		self.domainMB.onSpaceLoseCell( self.spaceNumber )
		if self._shouldDestroy:
			self.__onClose()
			self.destroy( deleteFromDB = self._shouldDeleteFromDB )

	def onGetCell( self ):
		"""
		cellʵ�崴�����֪ͨ���ص�callbackMailbox.onSpaceComplete��֪ͨ������ɡ�
		"""
		# create spawn point into this space on other thread.
		if len( self.getScript().getSpaceSpawnFile( self ) ) == 0:
			self.onSpawnPointLoadedOver( Const.SPACE_LOADSPAWN_RET_OPEN_FILE_ERROR )
		else:
			Love3.g_spawnLoader.registerSpace( self )		# �ӵ�������

		# space cell �������ͨ����������õ�spaceID����֪ͨ
		if self.spaceID >= 0:
			INFO_MSG("%s space %d(%i) got cell and spaceID %i, notify to domain space."%( self.className, self.spaceNumber, self.id, self.spaceID ) )
			self.domainMB.onSpaceGetCell( self.spaceNumber )
			self.wd.release(WATCH_KEY_CELL % (self.className, self.spaceNumber))
		else:
			self.spaceID = -2
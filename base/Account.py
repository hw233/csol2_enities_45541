# -*- coding: gb18030 -*-
# $Id: Account.py,v 1.74 2008-09-02 06:54:56 phw Exp $
#
"""
帐号管理
基本思想：在角色entity的.def中加入"parentDBID"属性，用于记录该角色所属的帐号，
当用户登录进来后Account entity即搜索(queryRoles)所有"parentDBID"等于自己的databaseID的角色并发送给client，
client可以在登录界面对角色就行增加(createRole)、删除(deleteRole)，或选择一角色进行登录(login)。
"""

import time
import cschannel_msgs
import ShareTexts as ST
import _md5
import struct
import BigWorld
import csdefine
import csconst
import csstatus
import ItemTypeEnum
import Const
import items
import RoleBorn								# use by init Item or Skill or else
import ItemBagRole
import sys
from bwdebug import *
from Function import Functor
from Function import ipToStr
from KitbagBase import KitbagBase
from KitbagsTypeImpl import KitbagsTypeImpl
from ChatProfanity import chatProfanity		# 聊天敏感词汇及处理
from AccountChecker import Checker
import Love3
import Language
from MsgLogger import g_logger
import ChangeRoleName
from CustomAccountData import CustomAccountData
import BackgroundTask
from urllib import urlopen
import socket

g_items = items.instance()

ACCOUNT_CHECK_TIMER = 0
ACCOUNT_KICK_TIMER = 1

socket.setdefaulttimeout(5.0)	#设置超时时间

# --------------------------------------------------------------------
# inner global methods
# --------------------------------------------------------------------
def queryRoles( parentID, callback ):
	"""
	query all roles which parent account is  parentID
	"""
	query = "select id, sm_playerName, sm_level, sm_raceclass, sm_lifetime, sm_hairNumber, sm_faceNumber, \
			sm_bodyFDict_modelNum, sm_bodyFDict_iLevel,\
			sm_volaFDict_modelNum, sm_volaFDict_iLevel,\
			sm_breechFDict_modelNum, sm_breechFDict_iLevel,\
			sm_feetFDict_modelNum, sm_feetFDict_iLevel,\
			sm_lefthandFDict_modelNum, sm_lefthandFDict_iLevel, sm_lefthandFDict_stAmount,\
			sm_righthandFDict_modelNum, sm_righthandFDict_iLevel, sm_righthandFDict_stAmount,\
			sm_talismanNum, sm_fashionNum, sm_adornNum, sm_headTextureID\
			from tbl_Role where sm_parentDBID = %i and sm_roleState != 1 " % parentID
	INFO_MSG( query )
	BigWorld.executeRawDatabaseCommand( query, callback )

def queryRolesEquipModel( parentIDs, callback ):
	"""
	query all roles equip model
	"""
	ids = list( parentIDs )
	last = ids.pop()
	s = [str( id ) + "," for id in ids]					# 保证2L不会变成"2L",而是变成"2"
	s.append( str(last) )
	query = "select parentID, sm_value from `tbl_Role_equipModel` where parentID in (%s)" % "".join(s)
	INFO_MSG( query )
	BigWorld.executeRawDatabaseCommand( query, callback )

def deleteRole( roleID, callback ):
	"""
	给角色加个标志，表示删除
	"""
	deleteTime = int(time.time())
	sql_sentence = "UPDATE tbl_Role SET sm_roleState = 1,sm_deleteTime = %s where id = %s" %(deleteTime,roleID)
	INFO_MSG( sql_sentence )
	BigWorld.executeRawDatabaseCommand( sql_sentence, callback )

def queryAdultInfo( account ):
	"""
	查询是否成年
	"""
	#示例接口: "http://verify.gyyx.cn:81/User/GameAdultService.ashx?" 
	
	try:
		interfacePath = BigWorld.globalData["adultQueryAddr"]
	except:
		ERROR_MSG("adultQueryAddr has not be configed!" )
		return -1
	params = "account=%s"
	addrPath = interfacePath + params%( account )
	INFO_MSG( "Adult check path: %s"%addrPath )
	try:
		ht = urlopen( addrPath ).read()
	except Exception, errstr:
		ERROR_MSG("Open the adult check address fault! error: %s"%errstr )
		return -1
	if ht not in ["false", "true"]:
		ERROR_MSG("Check adult return answer is not Know!! %s"%ht)
		return -1
	return ht == "true"


class QueryAdultInfoThread( BackgroundTask.BackgroundTask ):
	"""
	查询是否成年人线程
	"""
	def __init__( self, accountEntityID ):
		"""
		"""
		self.accountEntityID = accountEntityID
		BackgroundTask.BackgroundTask.__init__( self )


	def doBackgroundTask( self, mgr ):
		#读取网页字符
		#有效->关闭网页字符
		accountEntity = BigWorld.entities.get( self.accountEntityID )
		if accountEntity:
			self.result = int( queryAdultInfo( accountEntity.playerName ) )
			if self.result == -1:
				ERROR_MSG( "account %s query, but overtime!"%(accountEntity.playerName) )
				return
			INFO_MSG("account %s is adult: %i"%(accountEntity.playerName, self.result) )
			mgr.addMainThreadTask( self )


	def doMainThreadTask( self, mgr ):
		accountEntity = BigWorld.entities.get( self.accountEntityID )
		if accountEntity:
			if accountEntity.avatar:
				accountEntity.avatar.wallow_setAgeState( self.result )
			else:
				accountEntity.customData.set( "adult", str( self.result ) )

g_threadMgr = BackgroundTask.Manager()				#线程管理器
g_threadMgr.startThreads( 5 )						#同时开5条线程，只是避免玩家同时上线的问题

# --------------------------------------------------------------------
# implement account class
# --------------------------------------------------------------------
class Account( BigWorld.Proxy ):
	"""
	base inventory
	@type				storeItems	: dictionary
	@ivar				storeItems	: item list ( defined in def )
	@type				storedMoney	: INT32
	@param				storedMoney	: how much money store in inventory ( defined in def )
	"""
	def __init__(self):
		BigWorld.Proxy.__init__( self )
		self.avatar = None
		self.validMD5Check = True
		self.lastClientPort = 0
		self.deleteDBID = None

		# 设置互斥标记，用于避免在查询所有角色这一行为完成之前创建新角色。
		# 当值为True时则表示可以接受客户端请求的创建、删除角色等行为，
		# 否则不允许接受类似的操作请求。
		self.__rolesLoaded = False

		self.__isLogin = False			# 表示是否已经有一个login请求正在执行
		self.__destroySelf = True		# 如果是选择角色进入世界，则该变量被置为 False
		self.__roleInfoDict = {}			# 记录当前的角色的信息{roleDBID1:roleName1, roleDBID2:roleName2, ...}
		self.__tmpLoginTo = ""			# 临时记录登录到哪个城市
		self.__tmpRoles = []			# 临时记录所有的角色列表,等待获得角色的装备后一起发送

		self.loginState = Const.ACCOUNT_INITIAL_STATE
		self.isClientLogin = False				# 客户端是否登录过
		self.isLogOnAttempt = False				# 是否是另外的客户端重复登陆
		self.isLogOnAttemptWarning = False		# 当是另外的客户端重复登录时，是否需要警告
		self.loginTimerID = 0					# 登录timerID
		self.loginTimeOutTimerID = 0			# 登录等待时间过长，玩家被踢下线的timer
		self.firstLogIn	= True					# 是否第一次登录游戏(用于记录玩家第一次登录游戏的时间。)
		self.customData = CustomAccountData( self.playerName, self.databaseID )	#	加载公共的账号数据
		self.checker = Checker( self.id )		# 账号登陆前的账号检测器 包括 检测是否封号 是否锁号 密保卡等...

		# 反外挂验证数据，16:04 2009-11-12，wsf
		self.antiRobotCount = 0		# 第几次验证
		self.verifySuccess = False	# 验证是否成功



	def __del__(self):
		# phw注：在此处访问self.xxx属性会产生类似于以下的警告，如以下的INFO_MSG()就用就产生了类似于下面的警告。
		# WARNING: Base.playerName should not be accessed since Account entity id 3091 is destroyed
		#INFO_MSG( "%s(%i): Account destroyed" % ( self.playerName, self.id ) )
		pass

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onQueryRoles( self, resultSet, rows, errstr ):
		"""
		The object to call back (e.g. a function) with the result of the command execution.
		The callback will be called with 3 parameters: result set, number of affected rows and error string.

		@param resultSet:	list of list of string like as [ [ field1, field2, ... ], ... ];
						The result set parameter is a list of rows.
						Each row is a list of strings containing field values.
						The XML database will always return a result set with 1 row and 1 column containing the return code of the command.
						The result set will be None for commands to do not return a result set e.g. DELETE,
						or if there was an error in executing the command.
		@param rows:	The number of a affected rows parameter is a number indicating the number of rows affected by the command.
						This parameter is only relevant for commands to do not return a result set e.g. DELETE.
						This parameter is None for commands that do return a result set or if there was and error in executing the command.
		@param errstr:	The error string parameter is a string describing the error that occurred if there was an error in executing the command.
						This parameter is None if there was no error in executing the command.
		"""
		if errstr is not None:
			ERROR_MSG( errstr )
			return
		print "resultSet--Begin>>>",resultSet
		#return
		for k in resultSet:
			for index, value in enumerate( k ):
				if value == None:
					k[index] = 0
		print "resultSet--end>>>",resultSet
		roles = resultSet									# [ [ id, playerName, level, raceclass, lifetime, hairNumber ], ... ]
		self.__roleInfoDict = {}
		for roleInfo in roles:		# 汇总所有角色用于登录、删除操作时认证
			self.__roleInfoDict[long( roleInfo[0] )] = roleInfo[1]
		self.__tmpRoles = []
		for role in roles:
			loginRole = {}
			loginRole["roleID"]		 		= long( role[0] )
			loginRole["roleName"]	 		= role[1]
			loginRole["level"]		 		= int( role[2] )
			loginRole["raceclass"]	 		= int( role[3] )
			loginRole["lifetime"]	 		= float( role[4] )
			loginRole["hairNumber"]	 		= int( role[5] )
			loginRole["faceNumber"]			= int( role[6] )
			loginRole["bodyFDict"]			= { "modelNum" : int( role[7] ), "iLevel" : int( role[8] ) }
			loginRole["volaFDict"]			= { "modelNum" : int( role[9] ), "iLevel" : int( role[10] ) }
			loginRole["breechFDict"]		= { "modelNum" : int( role[11] ), "iLevel" : int( role[12] ) }
			loginRole["feetFDict"]			= { "modelNum" : int( role[13] ), "iLevel" : int( role[14] ) }
			loginRole["lefthandFDict"]		= { "modelNum" : int( role[15] ), "iLevel" : int( role[16] ), "stAmount" : int( role[17] ) }
			loginRole["righthandFDict"]		= { "modelNum" : int( role[18] ), "iLevel" : int( role[19] ), "stAmount" : int( role[20] ) }
			loginRole["talismanNum"]		= int( role[21] )
			loginRole["fashionNum"]			= int( role[22] )
			loginRole["adornNum"]			= int( role[23] )
			loginRole["headTextureID"]	= int( role[24] )
			self.__tmpRoles.append( loginRole )

		# 此情况有可能发生
		if self.isDestroyed:
			return

		self.client.initRolesCB( self.__tmpRoles )
		if not self.isClientLogin:
			self.isClientLogin = True
			self.client.onAccountLogin()
		self.__rolesLoaded = True	# 解锁，role的

	def onQueryRolesEquipModel( self, resultSet, rows, errstr ):
		"""
		The object to call back (e.g. a function) with the result of the command execution.
		The callback will be called with 3 parameters: result set, number of affected rows and error string.

		@param resultSet:	list of list of string like as [ [ field1, field2, ... ], ... ];
						The result set parameter is a list of rows.
						Each row is a list of strings containing field values.
						The XML database will always return a result set with 1 row and 1 column containing the return code of the command.
						The result set will be None for commands to do not return a result set e.g. DELETE,
						or if there was an error in executing the command.
		@param rows:	The number of a affected rows parameter is a number indicating the number of rows affected by the command.
						This parameter is only relevant for commands to do not return a result set e.g. DELETE.
						This parameter is None for commands that do return a result set or if there was and error in executing the command.
		@param errstr:	The error string parameter is a string describing the error that occurred if there was an error in executing the command.
						This parameter is None if there was no error in executing the command.
		"""
		if errstr is not None:
			ERROR_MSG( errstr )
			return

		modelNumbers = {}
		vals = resultSet	# [ [ parentID, sm_value ], ... ]
		for strRID, strNumber in vals:
			roleID = long( strRID )
			modelNumber = int( strNumber )
			if roleID not in modelNumbers :
				modelNumbers[roleID] = []
			modelNumbers[roleID].append( modelNumber )

		for loginRole in self.__tmpRoles:				# send roles info to client
			roleID = loginRole["roleID"]
			if roleID in modelNumbers:
				loginRole["equipModels"] = modelNumbers[roleID]
			else:
				INFO_MSG( "%s(%i): celldata equipModel is [] " % ( loginRole["roleName"], loginRole["roleID"] ) )
		self.client.initRolesCB( self.__tmpRoles )

	# ---------------------------------------
	def __onAvatarReady( self, avatar ):
		if avatar != None:
			self.lastLogonDBID = avatar.databaseID
			self.avatar = avatar
			avatar.accountEntity = self
			avatar.accountName = self.playerName       # 记录角色的账号名
			INFO_MSG("now avatar %s is ready..............."  % avatar.playerName )
			avatar.roleLogonMessage()                  # 写入玩家上线的日志
			self.giveClientTo( avatar )
			self.__destroySelf = False
		else:
			#self.statusMessage( "Failed to create your avatar."  )
			self.statusMessage( csstatus.ACCOUNT_STATE_CREATE_FAIL )
			#self.addTimer( 3.5 )

	def onLoadedAvatar( self, baseRef, databaseID, wasActive ):
		"""
		This is an optional callable object that will be called when the function createBaseFromDBID operation completes.
		The callable object will be called with three arguments: baseRef, databaseID and wasActive.
		If the operation was successful then baseRef will be a reference to the newly created Base entity,
		databaseID will be the database ID of the entity and wasActive will indicate whether the entity was already active.
		If wasActive is true,
		then baseRef is referring to a pre-existing Base entity and may be a mailbox rather than a direct reference to a base entity.
		If the operation failed, then baseRef will be None,
		databaseID will be 0 and wasActive will be false.
		The most common reason for failure is the that entity does not exist in the database but intermittent failures like timeouts or unable to allocate IDs may also occur.
		"""
		# 理论上，下面这行永远不会触发
		#assert wasActive is False, "%s(%i): the target entity was active, I can't do it." % (self.playerName, self.id)
		# 根据实际的运行结果表明，在某些特殊的情况下，wasActive 参数是有可能为True
		# 我实在是没有想明白，在什么样的状况下会让角色没有Account？
		# 如果那个在其它baseapp的角色的Account还存活着，那么玩家不可能会登录到当前baseapp。
		# 是否有可能由于在玩家下线时Account和Role是同时destroy，而Account所要存储的数据量较小，
		# 所以先destroyed了，然后玩家在很短的时间内重新登录并选择了该还没有destroy完毕的角色
		# 进行登录，从而产生这个现象？
		# 但什么样的人和机器才能达到这个速度？毕竟角色从存储到destroy不太可能会要这么长的时间。
		# 无论如何，当前如果发现了wasActive参数为True，那么我就尝试让目标entity下线，以保证
		# 下次加载的正确性。
		# 由于不知道已经加载的entity或basemailbox是什么状况，所以我们直接把旧的baseRef给踢下去。

		if wasActive:
			ERROR_MSG( "%s(%i): the target entity was active, I can't do it." % (self.playerName, self.id) )
			baseRef.logout()
			return

		if self.isDestroyed:
			# 经测试，在某些情况下确实会发生此问题。
			ERROR_MSG( "%s(%i): Failed to load Avatar '%i' for player, because account entity is destroyed." % (self.playerName, self.id, databaseID), baseRef )
			if baseRef is not None:
				baseRef.destroySelf()
			return

		if baseRef is not None:
			# 根据日志的现象来看，这里确实发生了传进来的baseRef不是一个entity
			if baseRef.__class__.__name__ != "Role":
				# 作下面的处理是为了将来有可能会去掉上面的assert，根据实际运行测试得知，
				# 上面assert的情况还是会发生的。
				# 初步怀疑出现这样的问题的原因是有其它地方（系统行为）加载了Role entity，
				# 刚好这时玩家上线。但实际上当前并没有地方有此行为。
				entity = BigWorld.entities.get( baseRef.id )
				if entity is None:
					# 如果下面这行日志错误出现了，表明引擎底层有bug，因为wasActive与baseRef不匹配
					# 如果没有出现，那很可能是<shouldResolveMailBoxes>参数设为True引起的问题。
					# 但似乎不太可能，因为这种情况只是偶然发生。
					# 当然，这里还有一种情况：那就是baseapp的自动backup机制搞出来的问题。
					# 无论如果，我们都把角色给踢出去，希望在下次重新登录时能正常。
					ERROR_MSG( "%s(%i): Failed to load Avatar '%i' for player, it's already loaded in other server. mailbox detail: %s" % ( self.playerName, self.id, databaseID, str( baseRef ) ) )
					baseRef.logout()	# 尝试性的让目标entity退出
					self.logoff()		# 尝试把玩家踢出，让玩家自己重连，以期能重新解决问题。
					return
				else:
					baseRef = entity

			INFO_MSG( baseRef.cellData["playerName"], ": lifetime =", baseRef.lifetime, "city =", self.__tmpLoginTo )
			self.__initKitbag( baseRef )		# check avatar's kitbags
			self.__initBankBag( baseRef )		# 检查钱庄
			self.__initGold( baseRef )
			self.__initSilver( baseRef )
			self.__onAvatarReady( baseRef )

			LOG_MSG( "init role base success, role_name = %s, role_dbid = %s, role_id = %s, account_name = %s, account_dbid = %s, account_id = %s"\
					%( baseRef.cellData["playerName"], baseRef.cellData["databaseID"], baseRef.id, self.playerName, self.databaseID, self.id ) )
			
			

		else:
			ERROR_MSG( "%s(%i): Failed to load Avatar '%i' for player, baseRef was None." % ( self.playerName, self.id, databaseID ) )
			self.__onAvatarReady( None )
		self.__isLogin = False

	# ---------------------------------------
	def onWriteRoleToDBRollback( self, success, avatar ):
		if success:
			self.__roleInfoDict[avatar.databaseID] = avatar.cellData["playerName"]
			loginRole = {}
			loginRole["roleID"]		 		= avatar.databaseID
			loginRole["roleName"]			= avatar.cellData["playerName"]
			loginRole["level"]		 		= avatar.cellData["level"]
			loginRole["raceclass"]	 		= avatar.cellData["raceclass"]
			loginRole["lifetime"]	 		= avatar.lifetime
			loginRole["hairNumber"]	 		= avatar.cellData["hairNumber"]
			loginRole["faceNumber"]	 		= avatar.cellData["faceNumber"]
			loginRole["bodyFDict"]			= avatar.cellData["bodyFDict"]
			loginRole["volaFDict"]		 	= avatar.cellData["volaFDict"]
			loginRole["breechFDict"]	 	= avatar.cellData["breechFDict"]
			loginRole["feetFDict"]	 		= avatar.cellData["feetFDict"]
			loginRole["lefthandFDict"]	 	= avatar.cellData["lefthandFDict"]
			loginRole["righthandFDict"]		= avatar.cellData["righthandFDict"]
			loginRole["talismanNum"]		= avatar.cellData["talismanNum"]
			loginRole["fashionNum"]			= avatar.cellData["fashionNum"]
			loginRole["adornNum"]			= avatar.cellData["adornNum"]
			loginRole["headTextureID"]	= avatar.cellData["headTextureID"]

			# 在创建角色的过程中，玩家有可能已经退出服务器
			# 因此有可能会出现异常，从而导致该entity没有destroyed，
			# 然后引起onLoadedAvatar()在重新登录且选择刚没有destroyed
			# 的entity进游戏时失败(assert)。
			# 因为那时候Account entity可能与此刚创建的avatar不在同一个baseapp中。
			if not self.isDestroyed:
				# 如面下在的调用出现类似于“TypeError: Method addRoleCB, argument 1: Expected PyFixedDictDataInstance, dict found”的错误，
				# 表示上面的loginRole字典与alias.xml里定义的FixedDict的属性数量不匹配。
				self.client.addRoleCB( loginRole )							# notify client
			try:
				g_logger.accountRoleAddLog( self.playerName, loginRole["roleID"], loginRole["roleName"])
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		else:
			self.statusMessage( csstatus.ACCOUNT_STATE_NAME_EXIST )
		# destroy entity
		avatar.destroy( writeToDB = False )

	# -------------------------------------------------
	def __initKitbag( self, entity ):
		"""
		初始化一个role entity的kitbags属性
		"""
		kits = entity.cellData["kitbags"]
		if not kits.get( csdefine.KB_EQUIP_ID ):
			INFO_MSG( "init equip kitbag." )
			equip = g_items.createDynamicItem( csdefine.ITEMID_KITBAG_EQUIP )
			kits[csdefine.KB_EQUIP_ID] = equip
			INFO_MSG( "Equip kitbag created!" )

		if not kits.get( csdefine.KB_COMMON_ID ):
			INFO_MSG( "init normal kitbag." )
			kitbag = g_items.createDynamicItem( csdefine.ITEMID_KITBAG_NORMAL )
			kits[csdefine.KB_COMMON_ID] = kitbag
			INFO_MSG( "Common kitbag created!" )

	def __initBankBag( self, entity ):
		"""
		初始化一个role entity的bankBags属性
		"""
		if not entity.bankNameList:
			entity.bankNameList.append( "" )

	def __initGold( self, entity ):
		"""
		初始化role Entity的gold属性
		"""
		entity.gold = self.gold

	def __initSilver( self, entity ):
		"""
		初始化role entity的silver属性
		"""
		entity.silver = self.silver

	def __checkRoleInfo( self, roleDBID, newName ):
		"""
		查找角色信息
		"""
		query = "SELECT sm_tong_dbID FROM tbl_Role WHERE id = %i" % roleDBID
		INFO_MSG( query )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__noticeOfChangeName, roleDBID, newName ) )

	def __noticeOfChangeName( self, roleDBID, newName, result, dummy, errstr ):
		"""
		改名通知
		"""
		if errstr:
			ERROR_MSG( errstr )
			ERROR_MSG( "changeName: query role Info failed! playerDBID is %s"%( roleDBID ) )
			return
		if len( result ) == 0:
			ERROR_MSG( "changeName: query role Info failed! result is None, playerDBID is %s"%( roleDBID ) )
		else:
			tongDBID = int( result[0][0] )
			if tongDBID:
				BigWorld.globalBases["TongManager"].memberNameChanged( tongDBID, roleDBID, newName )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def statusMessage( self, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		if self.isDestroyed: return
		args = args == () and "" or str( args )
		self.client.onStatusMessage( statusID, args )


	def queryCurDate( self ):
		"""
		获取服务器的当前时间
		"""
		return time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))

	def onAccountlockedNotify( self, lockTime ) :
		"""
		账号锁住时被触发
		"""
		self.client.onAccountlockedNotify( lockTime )

	def onBeginLogAccount( self ):
		"""
		开始登陆账号
		"""
		if self.avatar is not None:
			if not self.avatar.isDestroyed:
				INFO_MSG( "avatar '%s(entityID=%i, databaseID = %i)' already logon, logout it now." % ( self.avatar.getName(), self.avatar.id, self.avatar.databaseID ) )
				self.avatar.logout()	# 把旧角色注销
				#self.avatar.statusMessage( csstatus.ACCOUNT_STATE_FORCE_LOGOUT )	# do something in here
			else:
				self.avatar = None

		self.lastClientIpAddr = self.clientAddr[0]		# 记录最后登进来的IP地址，用于帐号重登录判断
		self.lastClientPort = self.clientAddr[1]

		if self.isLogOnAttempt:							# 如果是挤掉别的客户端登录
			self.isLogOnAttempt = False
			if self.isLogOnAttemptWarning :
				self.isLogOnAttemptWarning = False
				self.statusMessage( csstatus.ACCOUNT_STATE_FORCE_KICK )
			Love3.loginAttemper.loginAttempt( self )
			self.firstLogIn = True						# 如果是被挤掉那么就认为是一次新的登录
		else:
			if self.loginState ==  Const.ACCOUNT_INITIAL_STATE:
				if self.grade > 0:
					self.changeLoginState( Const.ACCOUNT_LOGIN_STATE )
				else:
					self.changeLoginState( Const.ACCOUNT_WAITTING_STATE )
			else:
				self.queryRoles()

		if self.firstLogIn:								# 如果是新的一次登录
			self.last_login = int( time.time())			# 记录时间
			self.firstLogIn = False						# 标记已经登陆(避免返回选择的时候覆盖掉这个值)
			r = self.customData.query( "adult" )
			if r is None or r == "0":
				INFO_MSG("account %s query adult info!"%( self.playerName ) )
				g_threadMgr.addBackgroundTask( QueryAdultInfoThread( self.id ) )
				

	def queryRoles( self ):
		"""
		请求账户的角色信息
		"""
		try:
			g_logger.accountLogonLog( self.playerName, self.lastClientIpAddr, cschannel_msgs.ACCOUNT_NOTICE_1 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		queryRoles( self.databaseID, self.onQueryRoles )

	def onAvatarClientGetCell( self ):
		"""
		帐号角色登录完毕
		"""
		self.changeLoginState( Const.ACCOUNT_GAMMING_STATE )
		if self.firstLoginTime == 0:				# 记录角色创建帐号后第一次登陆服务器的时间
			self.firstLoginTime = int( time.time())
			self.writeToDB()

	def isLoginState( self, state ):
		"""
		是否在state状态
		"""
		return self.loginState == state

	def changeLoginState( self, state ):
		"""
		改变登录状态
		"""
		if self.loginState == state:
			return

		if self.loginState == Const.ACCOUNT_LOGIN_STATE:	# 离开了登录状态，那么删除登录timer
			self.delTimer( self.loginTimeOutTimerID )
		elif self.loginState == Const.ACCOUNT_INITIAL_STATE:
			if not Love3.loginAttemper.canLogin( self ):
				self.statusMessage( csstatus.ACCOUNT_LOGIN_BUSY )
				self.logoff()
				return

		self.loginState = state
		if state == Const.ACCOUNT_WAITTING_STATE:
			Love3.loginAttemper.onAccountReady( self )
			try:
				g_logger.accountLogonLog( self.playerName, self.lastClientIpAddr, cschannel_msgs.ACCOUNT_NOTICE_2 )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		elif state == Const.ACCOUNT_LOGIN_STATE:
			self.queryRoles()
			self.loginTimeOutTimerID = self.addTimer( 600.0, 0, ACCOUNT_KICK_TIMER )	# 10分钟后不登录就踢下线
		elif state == Const.ACCOUNT_GAMMING_STATE:
			Love3.loginAttemper.loginComplete( self )

	# ----------------------------------------------------------------
	# methods called by engine
	# ----------------------------------------------------------------
	def onEntitiesEnabled( self ):
		if Love3.g_baseApp.runState != 0:
			INFO_MSG( "%s: server is shut down, unable to login!" % self.playerName )
			Love3.g_baseApp.deregisterAccount( self )
			self.destroy()
			return

		INFO_MSG( "%s: account entities enable." % self.playerName )

		# 任何时候都允许玩家登录，即当一个帐号已登录，
		# 后面有人使用相同的帐号登录时会把前面已登录的客户端踢出游戏。
		self.addProxyData( csdefine.PROXYDATA_CSOL_VERSION, Love3.versions )
		if self.loginTimerID != 0:
			self.delTimer( self.loginTimerID )
		if self.loginState == Const.ACCOUNT_INITIAL_STATE and not Love3.loginAttemper.canLogin( self ) and self.grade <= 0:
			self.statusMessage( csstatus.ACCOUNT_LOGIN_BUSY )
			self.logoff()
			return

		if self.loginState == Const.ACCOUNT_INITIAL_STATE or self.isLogOnAttempt:	# 只有初始化或者挤别人的时候才去检查账号是否合法
			self.customData.load( self.onCustomDataAready )
		else:																		# 返回选择的时候直接进入角色界面
			self.onBeginLogAccount()

		if Language.LANG == Language.LANG_BIG5 and self.activated_time <= 0:
			self.activated_time = int( time.time() )

	def onCustomDataAready( self ):
		"""
		检测如果是GM托管登陆，就无需检测矩阵卡和封号。
		"""
		if self.isDestroyed:
			return
		gmtimelimit = self.customData.query( "gmtimelimit")				# 记录当前矩阵卡值
		if not gmtimelimit or gmtimelimit < time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()):
			self.loginTimerID = self.addTimer( 2, 0, ACCOUNT_CHECK_TIMER )			# 初始化账号的时候将账号注册到列表中
		else:
			self.onBeginLogAccount()
		Love3.g_baseApp.registerAccount( self )										# 注册账号到激活账号列表中

	def onLogOnAttempt( self, ip, port ):
		"""
		这个回调似乎只有在失败的时候才会被调用，而当正常的时候似乎并没有调用，
		初步估计可能是当正常的判断认为不允许登录的时候调用此方法用来强制进行登录？
		"""
		if Love3.g_baseApp.runState != 0:
			self.statusMessage( csstatus.ACCOUNT_SERVER_SHUT_DOWN )
			return BigWorld.LOG_ON_REJECT
		INFO_MSG( "previous client ip addr: %s:%i, currently client ip addr: %s:%i" %
				( ipToStr( self.lastClientIpAddr ), self.lastClientPort, ipToStr( ip ), port ) )
		try:
			g_logger.accountLogonLog( self.playerName, self.lastClientIpAddr, cschannel_msgs.ACCOUNT_NOTICE_3 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

		if self.avatar is not None:
			if not self.avatar.isDestroyed:
				self.avatar.statusMessage( csstatus.ACCOUNT_STATE_FORCE_LOGOUT )	# do something in here
		else:
			self.statusMessage( csstatus.ACCOUNT_STATE_FORCE_LOGOUT )	# do something in here
		self.isClientLogin = False
		self.isLogOnAttempt = True
		if ip == self.lastClientIpAddr :
			self.isLogOnAttemptWarning = False
		else :
			self.isLogOnAttemptWarning = True
		return BigWorld.LOG_ON_ACCEPT

	def onClientDeath( self ):
		INFO_MSG( "%s(%i): I lost client." % ( self.playerName, self.id ) )
		self.logoff()

	# -------------------------------------------------
	def onAvatarDeath( self ):
		self.avatar = None
		if not self.hasClient:
			INFO_MSG( "%s: Avatar is destroyed, I will destroy self also." % self.playerName )
			try:
				g_logger.accountLogoutLog( self.playerName, self.lastClientIpAddr, cschannel_msgs.ACCOUNT_NOTICE_4 )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			Love3.g_baseApp.deregisterAccount( self )
			self.destroy()


	def onTimer( self, id, userArg ):
		if userArg == ACCOUNT_CHECK_TIMER:								# 检测账号的TIMER
			self.loginTimerID = 0
			self.getChecker().checkAccount()	# 检测账号是否能够登陆
		elif userArg == ACCOUNT_KICK_TIMER:
			self.loginTimeOutTimerID = 0
			self.statusMessage( csstatus.ACCOUNT_LOGIN_TIME_OUT_KICK )
			self.logoff()
		#self.giveClientTo( None )

	def onLoseCell( self ):
		if not self.__destroySelf :
			self.__destroySelf = True
			return
		if self.avatar is not None:
			self.avatar.accountEntity = None	# 设置为None，使其不再通知account
			self.avatar.destroySelf()
		try:
			g_logger.accountLogoutLog( self.playerName, self.lastClientIpAddr,cschannel_msgs.ACCOUNT_NOTICE_5 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		Love3.g_baseApp.deregisterAccount( self )
		self.destroy()

	def onWriteToDB( self, cellData ):
		"""
		see also api_python/python_base.chm
		"""
		# 先存储accountEntity的AccoutMD5字段 by 姜毅
		self.setPropertyMD5()

	# ----------------------------------------------------------------
	# define methods
	# ----------------------------------------------------------------
	def requestEnterGame( self ):
		"""
		Exposed method.
		客户端选择好角色，请求进入游戏，服务器开始验证，验证通过则设置通过标记通知客户端登录。
		"""
		DEBUG_MSG( "entity( id: %s ) request enter game." % self.id )
		if BigWorld.globalData["AntiRobotVerify_rate"] > 0:
			if self.antiRobotCount >= len( csconst.IMAGE_VERIFY_TIME_MAP ):	# 限制客户端的请求
				self.logoff()
				return
			self.triggerAntiRobot()	# 玩家每一次登陆角色都会触发反外挂图片验证
		else:
			self.verifySuccess = True	# 设置验证成功
			self.antiRobotCount = 0
			self.client.verifySuccess()

	def login( self, databaseID, loginTo ):
		"""
		Exposed method.
		player login by databaseID

		@param databaseID: indicate which role exist in Role table want to login
		@type  databaseID: INT64
		@return: none
		"""
		if not self.verifySuccess:
			return
		if self.loginState == Const.ACCOUNT_INITIAL_STATE or self.loginState == Const.ACCOUNT_WAITTING_STATE:
			HACK_MSG( "Account( %s ) is not ready." % self.playerName )
			return
		self.verifySuccess = False

		#初始化客户端时间同步
		#delay = ( self.latencyHi + self.latencyLo ) / 2.0
		delay = self.timeSinceHeardFromClient
		self.client.timeSynchronization( struct.pack( "=d", time.time() - delay ) )

		if self.__isLogin:
			self.statusMessage( csstatus.ACCOUNT_STATE_ID_ALREADY_LOGIN )
			return

		if (self.avatar is not None) and (not self.avatar.isDestroyed):
			self.statusMessage( csstatus.ACCOUNT_STATE_ROLE_ALREADY_LOGIN )
			return
		if databaseID not in self.__roleInfoDict:
			ERROR_MSG( "%s: you have no that role(dbid = %i)." % ( self.playerName, databaseID ) )
			self.statusMessage( csstatus.ACCOUNT_STATE_ROLE_NOT_EXIST )
			return

		self.__isLogin = True
		self.__tmpLoginTo = loginTo

		INFO_MSG( "%s: create role by databaseID %i" % (self.playerName, databaseID) )
		BigWorld.createBaseFromDBID( "Role", databaseID, self.onLoadedAvatar )

	def logoff( self ):
		"""
		玩家下线。
		"""
		INFO_MSG( "%s(%i): logoff." % (self.playerName, self.id) )
		self.firstLogIn = True					# 下线后第一次登录的记号 标为true
		Love3.loginAttemper.onAccountLogoff( self )
		if self.avatar is not None:
			self.avatar.accountEntity = None	# 设置为None，使其不再通知account
			self.avatar.destroySelf()
		Love3.g_baseApp.deregisterAccount( self )
		self.destroy()
		try:
			g_logger.accountLogoutLog( self.playerName, self.lastClientIpAddr,cschannel_msgs.ACCOUNT_NOTICE_6 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	# -------------------------------------------------
	def createRole( self, raceclass, playerName, hairNum, faceNum, headTextureID ):
		"""
		defined method.
		create new role to Role.
		"""
		if self.loginState == Const.ACCOUNT_INITIAL_STATE or self.loginState == Const.ACCOUNT_WAITTING_STATE:
			HACK_MSG( "Account( %s ) is not ready." % self.playerName )
			return

		if not self.__rolesLoaded:
			self.statusMessage( csstatus.ACCOUNT_STATE_ROLE_LIST_NOT_READY )
			ERROR_MSG( "roles list not ready, ignore request." )
			return
		if len( self.__roleInfoDict ) >= csconst.LOGIN_ROLE_UPPER_LIMIT:
			self.statusMessage( csstatus.ACCOUNT_STATE_CREATE_FULL )
			return
		INFO_MSG( "%s: create new role to %s, %i" % ( self.playerName, playerName, raceclass ) )

		statusID = self.checkPlayerName( playerName )
		if statusID != csstatus.ACCOUNT_CAN_USE_NAME:
			self.statusMessage( statusID )
			return

		if headTextureID is None:
			headTextureID = 0

		# check validity of raceClasses
		gender = raceclass & csdefine.RCMASK_GENDER
		profession = raceclass & csdefine.RCMASK_CLASS
		if gender not in csconst.ALL_GENDERS or profession not in csconst.ALL_PROFESSIONS :
			self.statusMessage( csstatus.ACCOUNT_STATE_CREATE_ERROR_RACE )
			return

		classStr = csconst.g_en_class[profession]
		maxHP = Const.calcHPMax( profession, 1 )
		maxMP = Const.calcMPMax( profession, 1 )

		# create new role now
		roleCamp = ( raceclass & csdefine.RCMASK_CAMP ) >> 20
		combatCamp = roleCamp
		paramDict = { "playerName":playerName, "parentDBID":self.databaseID, "raceclass":raceclass, "hairNumber" : hairNum, "faceNumber" : faceNum, "headTextureID" : headTextureID, "combatCamp": combatCamp }
		roleClass = raceclass & csdefine.RCMASK_CLASS
		# 设置出生点坐标
		paramDict["position"] = csconst.g_default_spawn_site[ roleClass ][ roleCamp ][0]
		paramDict["direction"] = csconst.g_default_spawn_site[ roleClass ][ roleCamp ][1]
		paramDict["spaceType"] = csconst.g_default_spawn_city[ raceclass & csdefine.RCMASK_RACE ][ roleCamp ][roleClass]
		# 设置复活点信息
		paramDict["reviveSpace"] = paramDict["spaceType"]
		paramDict["revivePosition"] = paramDict["position"]
		paramDict["reviveDirection"] = paramDict["direction"]
		paramDict["HP"] = maxHP
		paramDict["MP"] = maxMP
		paramDict["role_activated_time"] = int(time.time())
		paramDict["reg_ip"] = self.clientAddr[0]
		#paramDict["prestige"] = g_faction.getPrestigeData()

		#INFO_MSG( "create new role for", paramDict )
		avatar = BigWorld.createBaseLocally( "Role", paramDict )
		self.__initKitbag( avatar )
		self.__initBankBag( avatar )
		self.__initGold( avatar )
		self.__initSilver( avatar )

		#增加功能：创建一个角色时默认赠送一个冒险者行囊并且放在背包包裹栏第一个位置，且状态为已绑定 spf
		kits = avatar.cellData["kitbags"]
		INFO_MSG( "init default extra kitbag." )
		#取消赠送给玩家冒险者行囊 2008-08-13 spf
		#kitbag = g_items.createDynamicItem( 70101005 )
		#kits[csdefine.KB_EXCONE_ID] = kitbag
		#kitbag.setBindType( ItemTypeEnum.CBT_EQUIP, avatar )

		# init Item or Skill or else
		RoleBorn.generateAll( avatar )

		# 记录玩家第一次创建角色的时间
		if self.firstCreateRoleTime == 0:
			self.firstCreateRoleTime = int( time.time() )
			self.writeToDB()

		avatar.writeToDB( self.onWriteRoleToDBRollback )

	def deleteRole( self, databaseID, roleName ):
		"""
		define method.
		remove role by databaseID
		"""
		if not self.loginState:
			HACK_MSG( "Account( %s ) is not ready." % self.playerName )
			return

		if not self.__rolesLoaded:
			self.statusMessage( csstatus.ACCOUNT_STATE_ROLE_LIST_NOT_READY )
			ERROR_MSG( "roles list not ready, ignore request." )
			return
		if self.deleteDBID is not None:
			ERROR_MSG( "%s: I am busy, try it later." % self.playerName )
			self.statusMessage( csstatus.ACCOUNT_STATE_SERVER_BUSY )
			return
		if databaseID not in self.__roleInfoDict:
			ERROR_MSG( "%s: you have no that role(dbid = %i)." % ( self.playerName, databaseID ) )
			self.statusMessage( csstatus.ACCOUNT_STATE_ROLE_NOT_EXIST )
			return

		def deleteResult( result, rows, errstr ):
			if errstr is None :
				self.client.deleteRoleCB( self.deleteDBID )
				del self.__roleInfoDict[self.deleteDBID]
			else:
				ERROR_MSG( "delete role fail!" )
			self.deleteDBID = None

		self.deleteDBID = databaseID
		try:
			g_logger.accountRoleDelLog( self.playerName, self.deleteDBID, roleName )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		deleteRole( databaseID, deleteResult )

	def testAddGold( self, value ):
		"""
		尝试增加金元宝，判断是否超出上限

		@param value : 元宝的变化值
		@type value : INT64
		"""
		return self.gold + value < csconst.ROLE_GOLD_UPPER_LIMIT

	def addGold( self, value, reason ):
		"""
		Define method.
		玩家金元宝值变化

		@param value : 元宝的变化值
		@type value : INT64
		"""
		if self.gold + value > csconst.ROLE_GOLD_UPPER_LIMIT:
			return
		DEBUG_MSG( "-->>>player account( %s )'s gold in present:( %i ),increase value( %i )." % ( self.playerName, self.gold, value ) )
		self.gold += value
		if self.avatar is not None:
			self.avatar.updateGold( self.gold )
			
		try:
			g_logger.goldChangeLog( self.getName(), self.avatar.databaseID, self.avatar.getName(), value, self.gold, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def testAddSilver( self, value ):
		"""
		尝试增加银元宝，判断是否超出上限

		@param value : 元宝的变化值
		@type value : INT64
		"""
		return self.silver + value < csconst.ROLE_SILVER_UPPER_LIMIT

	def addSilver( self, value, reason ):
		"""
		Define method.
		玩家银元宝值变化

		@param value : 银元宝的变化值
		@type value : INT64
		"""
		if self.silver + value > csconst.ROLE_SILVER_UPPER_LIMIT:
			return
		DEBUG_MSG( "-->>>player account( %s )'s silver in present:( %i ),increase value( %i )." % ( self.playerName, self.silver, value ) )
		self.silver += value
		if self.avatar is not None:
			self.avatar.updateSilver( self.silver )
		try:
			g_logger.silverChangeLog( self.getName(), self.avatar.databaseID, self.avatar.getName(), value, self.silver, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def getNameAndID( self ):
		return self.playerName + "(%s)" % self.databaseID

	#--------------------------------------------------
	# 账号登陆检测器相关
	#--------------------------------------------------
	def getChecker( self ):
		"""
		获取当前的账号检测器
		"""
		return self.checker

	def check_passwdProMatrixValue( self, value ):
		"""
		检测矩阵卡密保值是否匹配
		@exposed method
		@type  value : UINT32
		@param value : 玩家给出的密报的答案
		"""
		checker = self.getChecker().getCurrentChecker()
		if not checker:
			ERROR_MSG( "can not get checker" )
			return
		if checker.__class__.__name__ != "PasswdProtect_Matrix":
			ERROR_MSG( "get a wrong checker, name = %s" % checker.__class__.__name__ )
			return
		checker.check_passwdProMatrixValue( value )

	def recheck_passwdProMatrixValue( self ):
		"""
		请求服务器重新生成矩阵密保的坐标和值
		@exposed method
		"""
		checker = self.getChecker().getCurrentChecker()
		if not checker:
			ERROR_MSG( "can not get checker" )
			return
		if checker.__class__.__name__ != "PasswdProtect_Matrix":
			ERROR_MSG( "get a wrong checker, name = %s" % checker.__class__.__name__ )
			return
		checker.reCheck()

	def calcPropertyMD5Code( self ):
		"""
		根据Account属性获得基于Account字段的MD5码 by 姜毅
		"""
		sumlist = [ self.grade, self.gold, self.silver, self.jackarooCard, self.jackarooCardState ]
		MD5_str = str( sumlist )
		return _md5.new( MD5_str ).hexdigest()

	def setPropertyMD5( self ):
		"""
		根据Account属性设置Account表字段的MD5码 by 姜毅
		"""
		if not self.validMD5Check: return
		self.baseSectionMD5Code = self.calcPropertyMD5Code()

	def checkPropertyMD5( self ):
		"""
		根据Account属性检测Account表字段的MD5码 by 姜毅
		"""
		if not Const.MD5Checker_Switcher: return True
		if self.baseSectionMD5Code == self.calcPropertyMD5Code():
			self.validMD5Check = True
		else:
			self.validMD5Check = False
		return self.validMD5Check

	def getName( self ):
		return self.playerName

	def triggerAntiRobot( self ):
		"""
		触发反外挂验证
		"""
		self.antiRobotCount += 1	# 验证了一次
		Love3.g_antiRobotVerify.triggerVerify( self, self.antiRobotCallback )

	def antiRobotCallback( self, result ):
		"""
		反外挂验证问答结果回调

		@param result : True or False，True表示验证成功，False表示验证失败
		"""
		if self.isDestroyed:
			return
		if result:
			self.client.verifySuccess()
			self.verifySuccess = True
			self.antiRobotCount = 0
		else:
			# 根据self.antiRobotCount的次数继续进行验证
			if self.antiRobotCount < len( csconst.IMAGE_VERIFY_TIME_MAP ):
				self.antiRobotCount += 1
				Love3.g_antiRobotVerify.triggerVerify( self, self.antiRobotCallback )
			else:
				# 踢人
				self.statusMessage( csstatus.ANTI_ROBOT_LOGIN_VERIFY_ERROR )
				self.logoff()

	def answerRobotVerify( self, answer ):
		"""
		Exposed method.
		客户端回答验证问题

		@param answer: 鼠标点击图片的坐标点( x, y )
		"""
		Love3.g_antiRobotVerify.verify( self.id, answer )

	def cancelAnswer(self):
		"""
		取消回答验证add by wuxo 2011-10-24
		"""
		Love3.g_antiRobotVerify.cancelVerify( self.id )
		self.antiRobotCount -= 1
		if self.antiRobotCount < 0:
			self.antiRobotCount = 0

	
	def changeName( self, roleDBID, newName ):
		"""
		Exposed method.
		更改角色名字

		@param roleDBID : 目标角色的dbid
		@type roleDBID : DATABASE_ID
		@param newName : 玩家新名字
		@type newName : STRING
		"""
		if roleDBID not in self.__roleInfoDict:
			ERROR_MSG( "%s: you have no that role(dbid = %i)." % ( self.playerName, roleDBID ) )
			self.statusMessage( csstatus.ACCOUNT_STATE_ROLE_NOT_EXIST )
			return
		playerName = self.__roleInfoDict[roleDBID]
		if playerName == newName:
			HACK_MSG( "old name( %s ) is the same with new name( %s )." % ( playerName, newName ) )
			return
		statusID = self.checkPlayerName( newName )
		if statusID != csstatus.ACCOUNT_CAN_USE_NAME:
			self.statusMessage( statusID )
			return
		if "_" not in playerName:
			HACK_MSG( "account( %s )'s role name( %s ) can not be changed." % ( self.playerName, playerName ) )
			return
		ChangeRoleName.changeName( self, roleDBID, playerName, newName )
		
	def changeRoleNameSuccess( self, roleDBID, newName ):
		"""
		角色改名成功
		"""
		#DEBUG_MSG( "---->>>roleDBID, newName", roleDBID, newName )
		self.__roleInfoDict[roleDBID] = newName
		self.client.changeRoleNameSuccess( roleDBID, newName )
		self.__checkRoleInfo( roleDBID, newName ) # 通知所在家族和帮会更新信息(如果有的话)

	def checkPlayerName( self, playerName ):
		"""
		验证玩家名字格式是否正确
		"""
		if playerName == "" :
			return csstatus.ACCOUNT_STATE_NAME_NONE
		if len( playerName ) > 14:
			return csstatus.ACCOUNT_STATE_NAME_TOOFAR
		if not chatProfanity.isPureString( playerName ):
			return csstatus.ACCOUNT_STATE_NAME_FIALCHAR
		if  chatProfanity.searchNameProfanity( playerName ) != None:
			return csstatus.ACCOUNT_STATE_NAME_FIALCHAR
		return csstatus.ACCOUNT_CAN_USE_NAME


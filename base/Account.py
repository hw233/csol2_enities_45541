# -*- coding: gb18030 -*-
# $Id: Account.py,v 1.74 2008-09-02 06:54:56 phw Exp $
#
"""
�ʺŹ���
����˼�룺�ڽ�ɫentity��.def�м���"parentDBID"���ԣ����ڼ�¼�ý�ɫ�������ʺţ�
���û���¼������Account entity������(queryRoles)����"parentDBID"�����Լ���databaseID�Ľ�ɫ�����͸�client��
client�����ڵ�¼����Խ�ɫ��������(createRole)��ɾ��(deleteRole)����ѡ��һ��ɫ���е�¼(login)��
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
from ChatProfanity import chatProfanity		# �������дʻ㼰����
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

socket.setdefaulttimeout(5.0)	#���ó�ʱʱ��

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
	s = [str( id ) + "," for id in ids]					# ��֤2L������"2L",���Ǳ��"2"
	s.append( str(last) )
	query = "select parentID, sm_value from `tbl_Role_equipModel` where parentID in (%s)" % "".join(s)
	INFO_MSG( query )
	BigWorld.executeRawDatabaseCommand( query, callback )

def deleteRole( roleID, callback ):
	"""
	����ɫ�Ӹ���־����ʾɾ��
	"""
	deleteTime = int(time.time())
	sql_sentence = "UPDATE tbl_Role SET sm_roleState = 1,sm_deleteTime = %s where id = %s" %(deleteTime,roleID)
	INFO_MSG( sql_sentence )
	BigWorld.executeRawDatabaseCommand( sql_sentence, callback )

def queryAdultInfo( account ):
	"""
	��ѯ�Ƿ����
	"""
	#ʾ���ӿ�: "http://verify.gyyx.cn:81/User/GameAdultService.ashx?" 
	
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
	��ѯ�Ƿ�������߳�
	"""
	def __init__( self, accountEntityID ):
		"""
		"""
		self.accountEntityID = accountEntityID
		BackgroundTask.BackgroundTask.__init__( self )


	def doBackgroundTask( self, mgr ):
		#��ȡ��ҳ�ַ�
		#��Ч->�ر���ҳ�ַ�
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

g_threadMgr = BackgroundTask.Manager()				#�̹߳�����
g_threadMgr.startThreads( 5 )						#ͬʱ��5���̣߳�ֻ�Ǳ������ͬʱ���ߵ�����

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

		# ���û����ǣ����ڱ����ڲ�ѯ���н�ɫ��һ��Ϊ���֮ǰ�����½�ɫ��
		# ��ֵΪTrueʱ���ʾ���Խ��ܿͻ�������Ĵ�����ɾ����ɫ����Ϊ��
		# ��������������ƵĲ�������
		self.__rolesLoaded = False

		self.__isLogin = False			# ��ʾ�Ƿ��Ѿ���һ��login��������ִ��
		self.__destroySelf = True		# �����ѡ���ɫ�������磬��ñ�������Ϊ False
		self.__roleInfoDict = {}			# ��¼��ǰ�Ľ�ɫ����Ϣ{roleDBID1:roleName1, roleDBID2:roleName2, ...}
		self.__tmpLoginTo = ""			# ��ʱ��¼��¼���ĸ�����
		self.__tmpRoles = []			# ��ʱ��¼���еĽ�ɫ�б�,�ȴ���ý�ɫ��װ����һ����

		self.loginState = Const.ACCOUNT_INITIAL_STATE
		self.isClientLogin = False				# �ͻ����Ƿ��¼��
		self.isLogOnAttempt = False				# �Ƿ�������Ŀͻ����ظ���½
		self.isLogOnAttemptWarning = False		# ��������Ŀͻ����ظ���¼ʱ���Ƿ���Ҫ����
		self.loginTimerID = 0					# ��¼timerID
		self.loginTimeOutTimerID = 0			# ��¼�ȴ�ʱ���������ұ������ߵ�timer
		self.firstLogIn	= True					# �Ƿ��һ�ε�¼��Ϸ(���ڼ�¼��ҵ�һ�ε�¼��Ϸ��ʱ�䡣)
		self.customData = CustomAccountData( self.playerName, self.databaseID )	#	���ع������˺�����
		self.checker = Checker( self.id )		# �˺ŵ�½ǰ���˺ż���� ���� ����Ƿ��� �Ƿ����� �ܱ�����...

		# �������֤���ݣ�16:04 2009-11-12��wsf
		self.antiRobotCount = 0		# �ڼ�����֤
		self.verifySuccess = False	# ��֤�Ƿ�ɹ�



	def __del__(self):
		# phwע���ڴ˴�����self.xxx���Ի�������������µľ��棬�����µ�INFO_MSG()���þͲ���������������ľ��档
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
		for roleInfo in roles:		# �������н�ɫ���ڵ�¼��ɾ������ʱ��֤
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

		# ������п��ܷ���
		if self.isDestroyed:
			return

		self.client.initRolesCB( self.__tmpRoles )
		if not self.isClientLogin:
			self.isClientLogin = True
			self.client.onAccountLogin()
		self.__rolesLoaded = True	# ������role��

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
			avatar.accountName = self.playerName       # ��¼��ɫ���˺���
			INFO_MSG("now avatar %s is ready..............."  % avatar.playerName )
			avatar.roleLogonMessage()                  # д��������ߵ���־
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
		# �����ϣ�����������Զ���ᴥ��
		#assert wasActive is False, "%s(%i): the target entity was active, I can't do it." % (self.playerName, self.id)
		# ����ʵ�ʵ����н����������ĳЩ���������£�wasActive �������п���ΪTrue
		# ��ʵ����û�������ף���ʲô����״���»��ý�ɫû��Account��
		# ����Ǹ�������baseapp�Ľ�ɫ��Account������ţ���ô��Ҳ����ܻ��¼����ǰbaseapp��
		# �Ƿ��п����������������ʱAccount��Role��ͬʱdestroy����Account��Ҫ�洢����������С��
		# ������destroyed�ˣ�Ȼ������ں̵ܶ�ʱ�������µ�¼��ѡ���˸û�û��destroy��ϵĽ�ɫ
		# ���е�¼���Ӷ������������
		# ��ʲô�����˺ͻ������ܴﵽ����ٶȣ��Ͼ���ɫ�Ӵ洢��destroy��̫���ܻ�Ҫ��ô����ʱ�䡣
		# ������Σ���ǰ���������wasActive����ΪTrue����ô�Ҿͳ�����Ŀ��entity���ߣ��Ա�֤
		# �´μ��ص���ȷ�ԡ�
		# ���ڲ�֪���Ѿ����ص�entity��basemailbox��ʲô״������������ֱ�ӰѾɵ�baseRef������ȥ��

		if wasActive:
			ERROR_MSG( "%s(%i): the target entity was active, I can't do it." % (self.playerName, self.id) )
			baseRef.logout()
			return

		if self.isDestroyed:
			# �����ԣ���ĳЩ�����ȷʵ�ᷢ�������⡣
			ERROR_MSG( "%s(%i): Failed to load Avatar '%i' for player, because account entity is destroyed." % (self.playerName, self.id, databaseID), baseRef )
			if baseRef is not None:
				baseRef.destroySelf()
			return

		if baseRef is not None:
			# ������־����������������ȷʵ�����˴�������baseRef����һ��entity
			if baseRef.__class__.__name__ != "Role":
				# ������Ĵ�����Ϊ�˽����п��ܻ�ȥ�������assert������ʵ�����в��Ե�֪��
				# ����assert��������ǻᷢ���ġ�
				# �������ɳ��������������ԭ�����������ط���ϵͳ��Ϊ��������Role entity��
				# �պ���ʱ������ߡ���ʵ���ϵ�ǰ��û�еط��д���Ϊ��
				entity = BigWorld.entities.get( baseRef.id )
				if entity is None:
					# �������������־��������ˣ���������ײ���bug����ΪwasActive��baseRef��ƥ��
					# ���û�г��֣��Ǻܿ�����<shouldResolveMailBoxes>������ΪTrue��������⡣
					# ���ƺ���̫���ܣ���Ϊ�������ֻ��żȻ������
					# ��Ȼ�����ﻹ��һ��������Ǿ���baseapp���Զ�backup���Ƹ���������⡣
					# ������������Ƕ��ѽ�ɫ���߳�ȥ��ϣ�����´����µ�¼ʱ��������
					ERROR_MSG( "%s(%i): Failed to load Avatar '%i' for player, it's already loaded in other server. mailbox detail: %s" % ( self.playerName, self.id, databaseID, str( baseRef ) ) )
					baseRef.logout()	# �����Ե���Ŀ��entity�˳�
					self.logoff()		# ���԰�����߳���������Լ����������������½�����⡣
					return
				else:
					baseRef = entity

			INFO_MSG( baseRef.cellData["playerName"], ": lifetime =", baseRef.lifetime, "city =", self.__tmpLoginTo )
			self.__initKitbag( baseRef )		# check avatar's kitbags
			self.__initBankBag( baseRef )		# ���Ǯׯ
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

			# �ڴ�����ɫ�Ĺ����У�����п����Ѿ��˳�������
			# ����п��ܻ�����쳣���Ӷ����¸�entityû��destroyed��
			# Ȼ������onLoadedAvatar()�����µ�¼��ѡ���û��destroyed
			# ��entity����Ϸʱʧ��(assert)��
			# ��Ϊ��ʱ��Account entity������˸մ�����avatar����ͬһ��baseapp�С�
			if not self.isDestroyed:
				# �������ڵĵ��ó��������ڡ�TypeError: Method addRoleCB, argument 1: Expected PyFixedDictDataInstance, dict found���Ĵ���
				# ��ʾ�����loginRole�ֵ���alias.xml�ﶨ���FixedDict������������ƥ�䡣
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
		��ʼ��һ��role entity��kitbags����
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
		��ʼ��һ��role entity��bankBags����
		"""
		if not entity.bankNameList:
			entity.bankNameList.append( "" )

	def __initGold( self, entity ):
		"""
		��ʼ��role Entity��gold����
		"""
		entity.gold = self.gold

	def __initSilver( self, entity ):
		"""
		��ʼ��role entity��silver����
		"""
		entity.silver = self.silver

	def __checkRoleInfo( self, roleDBID, newName ):
		"""
		���ҽ�ɫ��Ϣ
		"""
		query = "SELECT sm_tong_dbID FROM tbl_Role WHERE id = %i" % roleDBID
		INFO_MSG( query )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__noticeOfChangeName, roleDBID, newName ) )

	def __noticeOfChangeName( self, roleDBID, newName, result, dummy, errstr ):
		"""
		����֪ͨ
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
		��ȡ�������ĵ�ǰʱ��
		"""
		return time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))

	def onAccountlockedNotify( self, lockTime ) :
		"""
		�˺���סʱ������
		"""
		self.client.onAccountlockedNotify( lockTime )

	def onBeginLogAccount( self ):
		"""
		��ʼ��½�˺�
		"""
		if self.avatar is not None:
			if not self.avatar.isDestroyed:
				INFO_MSG( "avatar '%s(entityID=%i, databaseID = %i)' already logon, logout it now." % ( self.avatar.getName(), self.avatar.id, self.avatar.databaseID ) )
				self.avatar.logout()	# �Ѿɽ�ɫע��
				#self.avatar.statusMessage( csstatus.ACCOUNT_STATE_FORCE_LOGOUT )	# do something in here
			else:
				self.avatar = None

		self.lastClientIpAddr = self.clientAddr[0]		# ��¼���ǽ�����IP��ַ�������ʺ��ص�¼�ж�
		self.lastClientPort = self.clientAddr[1]

		if self.isLogOnAttempt:							# ����Ǽ�����Ŀͻ��˵�¼
			self.isLogOnAttempt = False
			if self.isLogOnAttemptWarning :
				self.isLogOnAttemptWarning = False
				self.statusMessage( csstatus.ACCOUNT_STATE_FORCE_KICK )
			Love3.loginAttemper.loginAttempt( self )
			self.firstLogIn = True						# ����Ǳ�������ô����Ϊ��һ���µĵ�¼
		else:
			if self.loginState ==  Const.ACCOUNT_INITIAL_STATE:
				if self.grade > 0:
					self.changeLoginState( Const.ACCOUNT_LOGIN_STATE )
				else:
					self.changeLoginState( Const.ACCOUNT_WAITTING_STATE )
			else:
				self.queryRoles()

		if self.firstLogIn:								# ������µ�һ�ε�¼
			self.last_login = int( time.time())			# ��¼ʱ��
			self.firstLogIn = False						# ����Ѿ���½(���ⷵ��ѡ���ʱ�򸲸ǵ����ֵ)
			r = self.customData.query( "adult" )
			if r is None or r == "0":
				INFO_MSG("account %s query adult info!"%( self.playerName ) )
				g_threadMgr.addBackgroundTask( QueryAdultInfoThread( self.id ) )
				

	def queryRoles( self ):
		"""
		�����˻��Ľ�ɫ��Ϣ
		"""
		try:
			g_logger.accountLogonLog( self.playerName, self.lastClientIpAddr, cschannel_msgs.ACCOUNT_NOTICE_1 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		queryRoles( self.databaseID, self.onQueryRoles )

	def onAvatarClientGetCell( self ):
		"""
		�ʺŽ�ɫ��¼���
		"""
		self.changeLoginState( Const.ACCOUNT_GAMMING_STATE )
		if self.firstLoginTime == 0:				# ��¼��ɫ�����ʺź��һ�ε�½��������ʱ��
			self.firstLoginTime = int( time.time())
			self.writeToDB()

	def isLoginState( self, state ):
		"""
		�Ƿ���state״̬
		"""
		return self.loginState == state

	def changeLoginState( self, state ):
		"""
		�ı��¼״̬
		"""
		if self.loginState == state:
			return

		if self.loginState == Const.ACCOUNT_LOGIN_STATE:	# �뿪�˵�¼״̬����ôɾ����¼timer
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
			self.loginTimeOutTimerID = self.addTimer( 600.0, 0, ACCOUNT_KICK_TIMER )	# 10���Ӻ󲻵�¼��������
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

		# �κ�ʱ��������ҵ�¼������һ���ʺ��ѵ�¼��
		# ��������ʹ����ͬ���ʺŵ�¼ʱ���ǰ���ѵ�¼�Ŀͻ����߳���Ϸ��
		self.addProxyData( csdefine.PROXYDATA_CSOL_VERSION, Love3.versions )
		if self.loginTimerID != 0:
			self.delTimer( self.loginTimerID )
		if self.loginState == Const.ACCOUNT_INITIAL_STATE and not Love3.loginAttemper.canLogin( self ) and self.grade <= 0:
			self.statusMessage( csstatus.ACCOUNT_LOGIN_BUSY )
			self.logoff()
			return

		if self.loginState == Const.ACCOUNT_INITIAL_STATE or self.isLogOnAttempt:	# ֻ�г�ʼ�����߼����˵�ʱ���ȥ����˺��Ƿ�Ϸ�
			self.customData.load( self.onCustomDataAready )
		else:																		# ����ѡ���ʱ��ֱ�ӽ����ɫ����
			self.onBeginLogAccount()

		if Language.LANG == Language.LANG_BIG5 and self.activated_time <= 0:
			self.activated_time = int( time.time() )

	def onCustomDataAready( self ):
		"""
		��������GM�йܵ�½������������󿨺ͷ�š�
		"""
		if self.isDestroyed:
			return
		gmtimelimit = self.customData.query( "gmtimelimit")				# ��¼��ǰ����ֵ
		if not gmtimelimit or gmtimelimit < time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()):
			self.loginTimerID = self.addTimer( 2, 0, ACCOUNT_CHECK_TIMER )			# ��ʼ���˺ŵ�ʱ���˺�ע�ᵽ�б���
		else:
			self.onBeginLogAccount()
		Love3.g_baseApp.registerAccount( self )										# ע���˺ŵ������˺��б���

	def onLogOnAttempt( self, ip, port ):
		"""
		����ص��ƺ�ֻ����ʧ�ܵ�ʱ��Żᱻ���ã�����������ʱ���ƺ���û�е��ã�
		�������ƿ����ǵ��������ж���Ϊ�������¼��ʱ����ô˷�������ǿ�ƽ��е�¼��
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
		if userArg == ACCOUNT_CHECK_TIMER:								# ����˺ŵ�TIMER
			self.loginTimerID = 0
			self.getChecker().checkAccount()	# ����˺��Ƿ��ܹ���½
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
			self.avatar.accountEntity = None	# ����ΪNone��ʹ�䲻��֪ͨaccount
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
		# �ȴ洢accountEntity��AccoutMD5�ֶ� by ����
		self.setPropertyMD5()

	# ----------------------------------------------------------------
	# define methods
	# ----------------------------------------------------------------
	def requestEnterGame( self ):
		"""
		Exposed method.
		�ͻ���ѡ��ý�ɫ�����������Ϸ����������ʼ��֤����֤ͨ��������ͨ�����֪ͨ�ͻ��˵�¼��
		"""
		DEBUG_MSG( "entity( id: %s ) request enter game." % self.id )
		if BigWorld.globalData["AntiRobotVerify_rate"] > 0:
			if self.antiRobotCount >= len( csconst.IMAGE_VERIFY_TIME_MAP ):	# ���ƿͻ��˵�����
				self.logoff()
				return
			self.triggerAntiRobot()	# ���ÿһ�ε�½��ɫ���ᴥ�������ͼƬ��֤
		else:
			self.verifySuccess = True	# ������֤�ɹ�
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

		#��ʼ���ͻ���ʱ��ͬ��
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
		������ߡ�
		"""
		INFO_MSG( "%s(%i): logoff." % (self.playerName, self.id) )
		self.firstLogIn = True					# ���ߺ��һ�ε�¼�ļǺ� ��Ϊtrue
		Love3.loginAttemper.onAccountLogoff( self )
		if self.avatar is not None:
			self.avatar.accountEntity = None	# ����ΪNone��ʹ�䲻��֪ͨaccount
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
		# ���ó���������
		paramDict["position"] = csconst.g_default_spawn_site[ roleClass ][ roleCamp ][0]
		paramDict["direction"] = csconst.g_default_spawn_site[ roleClass ][ roleCamp ][1]
		paramDict["spaceType"] = csconst.g_default_spawn_city[ raceclass & csdefine.RCMASK_RACE ][ roleCamp ][roleClass]
		# ���ø������Ϣ
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

		#���ӹ��ܣ�����һ����ɫʱĬ������һ��ð�������Ҳ��ҷ��ڱ�����������һ��λ�ã���״̬Ϊ�Ѱ� spf
		kits = avatar.cellData["kitbags"]
		INFO_MSG( "init default extra kitbag." )
		#ȡ�����͸����ð�������� 2008-08-13 spf
		#kitbag = g_items.createDynamicItem( 70101005 )
		#kits[csdefine.KB_EXCONE_ID] = kitbag
		#kitbag.setBindType( ItemTypeEnum.CBT_EQUIP, avatar )

		# init Item or Skill or else
		RoleBorn.generateAll( avatar )

		# ��¼��ҵ�һ�δ�����ɫ��ʱ��
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
		�������ӽ�Ԫ�����ж��Ƿ񳬳�����

		@param value : Ԫ���ı仯ֵ
		@type value : INT64
		"""
		return self.gold + value < csconst.ROLE_GOLD_UPPER_LIMIT

	def addGold( self, value, reason ):
		"""
		Define method.
		��ҽ�Ԫ��ֵ�仯

		@param value : Ԫ���ı仯ֵ
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
		����������Ԫ�����ж��Ƿ񳬳�����

		@param value : Ԫ���ı仯ֵ
		@type value : INT64
		"""
		return self.silver + value < csconst.ROLE_SILVER_UPPER_LIMIT

	def addSilver( self, value, reason ):
		"""
		Define method.
		�����Ԫ��ֵ�仯

		@param value : ��Ԫ���ı仯ֵ
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
	# �˺ŵ�½��������
	#--------------------------------------------------
	def getChecker( self ):
		"""
		��ȡ��ǰ���˺ż����
		"""
		return self.checker

	def check_passwdProMatrixValue( self, value ):
		"""
		�������ܱ�ֵ�Ƿ�ƥ��
		@exposed method
		@type  value : UINT32
		@param value : ��Ҹ������ܱ��Ĵ�
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
		����������������ɾ����ܱ��������ֵ
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
		����Account���Ի�û���Account�ֶε�MD5�� by ����
		"""
		sumlist = [ self.grade, self.gold, self.silver, self.jackarooCard, self.jackarooCardState ]
		MD5_str = str( sumlist )
		return _md5.new( MD5_str ).hexdigest()

	def setPropertyMD5( self ):
		"""
		����Account��������Account���ֶε�MD5�� by ����
		"""
		if not self.validMD5Check: return
		self.baseSectionMD5Code = self.calcPropertyMD5Code()

	def checkPropertyMD5( self ):
		"""
		����Account���Լ��Account���ֶε�MD5�� by ����
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
		�����������֤
		"""
		self.antiRobotCount += 1	# ��֤��һ��
		Love3.g_antiRobotVerify.triggerVerify( self, self.antiRobotCallback )

	def antiRobotCallback( self, result ):
		"""
		�������֤�ʴ����ص�

		@param result : True or False��True��ʾ��֤�ɹ���False��ʾ��֤ʧ��
		"""
		if self.isDestroyed:
			return
		if result:
			self.client.verifySuccess()
			self.verifySuccess = True
			self.antiRobotCount = 0
		else:
			# ����self.antiRobotCount�Ĵ�������������֤
			if self.antiRobotCount < len( csconst.IMAGE_VERIFY_TIME_MAP ):
				self.antiRobotCount += 1
				Love3.g_antiRobotVerify.triggerVerify( self, self.antiRobotCallback )
			else:
				# ����
				self.statusMessage( csstatus.ANTI_ROBOT_LOGIN_VERIFY_ERROR )
				self.logoff()

	def answerRobotVerify( self, answer ):
		"""
		Exposed method.
		�ͻ��˻ش���֤����

		@param answer: �����ͼƬ�������( x, y )
		"""
		Love3.g_antiRobotVerify.verify( self.id, answer )

	def cancelAnswer(self):
		"""
		ȡ���ش���֤add by wuxo 2011-10-24
		"""
		Love3.g_antiRobotVerify.cancelVerify( self.id )
		self.antiRobotCount -= 1
		if self.antiRobotCount < 0:
			self.antiRobotCount = 0

	
	def changeName( self, roleDBID, newName ):
		"""
		Exposed method.
		���Ľ�ɫ����

		@param roleDBID : Ŀ���ɫ��dbid
		@type roleDBID : DATABASE_ID
		@param newName : ���������
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
		��ɫ�����ɹ�
		"""
		#DEBUG_MSG( "---->>>roleDBID, newName", roleDBID, newName )
		self.__roleInfoDict[roleDBID] = newName
		self.client.changeRoleNameSuccess( roleDBID, newName )
		self.__checkRoleInfo( roleDBID, newName ) # ֪ͨ���ڼ���Ͱ�������Ϣ(����еĻ�)

	def checkPlayerName( self, playerName ):
		"""
		��֤������ָ�ʽ�Ƿ���ȷ
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


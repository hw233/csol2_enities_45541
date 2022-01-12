# -*- coding: gb18030 -*-

# $Id: BaseappEntity.py,v 1.8 2008-08-30 09:02:43 huangyongwei Exp $
"""
Ŀ�ģ�ϣ��ÿ��baseapp����֪��������baseapp���Ա�㲥һЩ����
���������Ҫ��ÿ��baseapp�ϲ���һ��BaseEntity������ע���ΪglobalBase��
�Դ�����ʶÿһ��baseapp����ô�����ǾͿ���ͨ�����baseEntity�㲥һЩ���ݵ����е�baseapp�ϣ�
�磺ȫ������

����ȫ������������꿴CS_OL.MDL

��ΪĿǰ��_localPlayers������б����������������߽�ɫ��entity��
�������ڵ�����㲥(_localBroadcast()����)�в���Ҫ�ٱ�������BigWorld.entities���Ӷ������Ч�ʡ�
"""

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csconst
import csstatus
from bwdebug import *
from Role import Role
from Love3 import loginAttemper
import Const
from MsgLogger import g_logger


TIMER_LOOKUP_ROLE_BASE = 123
TIMER_SHUTDOWN_SERVER = 124
TIMER_DELAY_SHUTDOWN = 125


class ShutdownTimer:
	"""
	��CSOL-6602����Ҫ���ӷ������ػ�����ʱ��15���ӿ�ʼ����ʱ��ǰ10����ÿ����ϵͳ��ʾһ����ң���5����30��һ��ϵͳ��ʾ�ط�ʱ�䡣
	"""
	def __init__( self, baseappEntity, delay ):
		"""
		@param parent: instance of baseapp entity
		@param delay: �ӳٶ೤ʱ��ִ��shutdown��Ϊ����λ����
		"""
		self.baseappEntity = baseappEntity
		self.delay = int( delay )

		self.__call__()

	def __call__( self ):
		"""
		"""
		if self.delay <= 0:
			self.baseappEntity.shutdownAll( 0 )
			self.baseappEntity = None
			return

		d = self.delay
		if d <= 30:
			msg = cschannel_msgs.BASEAPPENTITY_NOTICE_0 % d
		elif d <= 300:
			m = d % 60
			if m:
				msg = cschannel_msgs.BASEAPPENTITY_NOTICE_1 % ( d / 60, m )
			else:
				msg = cschannel_msgs.BASEAPPENTITY_NOTICE_2 % ( d / 60 )
			d = 30	# ���5����ÿ30����ʾһ��
		else:
			msg = cschannel_msgs.BASEAPPENTITY_NOTICE_3 % ( d / 60 )
			d = 60	# ǰ���ÿ������ʾһ��
		self.delay -= d
		self.baseappEntity.anonymityBroadcast( msg, [] )
		self.baseappEntity.addTimer( d, 0, TIMER_DELAY_SHUTDOWN )

class BaseappEntity( BigWorld.Base ):
	"""
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )

		# ��¼���к��Լ�ͬһ���͵�����baseApp mailbox
		# ����ÿ�ι㲥��ʱ��Ϳ���ֱ��ʹ�ã�������Ҫ�ٴε�BigWorld.globalBases��ȥ��ѯ�Ƚ�
		self.globalData = {}

		# entity������ȫ��ֵΪ����ı���spaceEntity��
		# ��һ��Ϊ��ǰ���ڴ�����space�����һ��Ϊ�������space���Դ�����
		self.spawnQueue = []

		# ʹ���Լ���entityID����ǰ׺�γ�Ψһ������
		# GBAE is global baseApp Entity, don't use "GBAE*" on other globalBases Key
		self.globalName = "%s%i" % ( csconst.C_PREFIX_GBAE, self.id )
		self.registerGlobally( self.globalName, self.registerCallback )

		# ͨ���ڴ�baseapp���ߵ���ҵ�������entityʵ���Ķ�Ӧ��
		# { "�������" : instance of entity which live in BigWorld.entities, ... }
		self._localPlayers = {}
		self._localCampPlayers = {}

		# ��ʱ�б�����ʵ��lookupRoleBaseByName()�Ļص�����
		# { ��ʱΨһID : [ Ԥ�ڻظ�����, ��ʱʱ��, callback ], ...}
		# ��Ԥ�ڻظ���������ָ���ǵ�ǰ�򼸸�baseapp����������ÿ�յ�һ���ظ�����ֵ����һ
		# ����ʱʱ�䡱����λ���롱��float��ÿ����һ�Σ������ʱ���жϲ��ص�֪ͨĿ��δ�ҵ���������������ԭ��ܿ��������й�����ĳ̨baseapp������
		# callback: function���ɵ������ṩ�Ļص�����
		self._tmpSearchCache = {}
		self._tmpSearchCurrentID = 0	# ���ڼ�¼���һ�η����IDֵ��ֵ 0 ���ڱ�ʾû�л�ʧ�ܣ���˲���Ϊ����ID����
		self._searchTimerID = 0			# ���ڼ��ĳ��lookupRoleBaseByName()�����Ƿ���ڵ�timer

		self._shutdownTimerID = 0		# ���ڼ�¼��ǰ�Ƿ��Ѵ���shutdown�����У��Ա����ظ�ִ��
		# ����״̬��
		#   0 �������У�
		#   1 ��������״̬�У�
		#   2 ���ڱ��������������״̬�У�
		#   3 �������ݴ�����ϣ�׼���رշ�������״̬�У�
		#   4 Ӧ�ÿ��Թرշ�������
		self.runState = 0

		# RelationMgr����baseApp�����uid�б���ʣ��uid����10��ʱ������RelationMgr��������100��uid
		# �µ�uid�б�������Ҫһ��tick��ʱ�䣬��һ��tick֮���д���10����ҵĽ�Ϊ��ϵ��������ô����һ����ʱ���������ִ��0.1����һ��timer
		self.maxRelationUID = 0
		self.currentRelationUID = 0

		# �˺��б�����������ǰ��¼���˺�,��Ԫ����ֵ�������á�
		self._localAccounts = {}

	def registerCallback( self, status ):
		if not status:
			raise "I can't register %s into BigWorld.globalBases." % self.globalName

		BigWorld.globalData[ self.globalName ] = self		# ͬʱע�ᵽBigWorld.globalData��
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ] = self			# ע��һ��û BaseappEntity��cell ���������ǽ�ɫ entity �㲥��Ϣ
															# ע�⣺����дû��globalData ��ֻ�����һ�� BaseappEntity ����
															# ��˲��³�� hyw--2009.06.30
		# ��ѭһ��BigWorld.globalBases�Բ������е�ͬ������
		for k, v in BigWorld.globalBases.items():
			if not isinstance( k, str ) or not k.startswith( csconst.C_PREFIX_GBAE ):
				continue
			self.globalData[k] = v					# �����ڲ�����
			v.addRef( self.globalName, self )		# ֪ͨ����baseapp entity��������

		# 15:11 2009-10-8��wsf
		# ������ҹ�ϵUID��Դ�����RelationMgr��ûע��ã�
		# ��ô��RelationMgrע���ʱ��������UID��Դ���͹�����
		try:
			BigWorld.globalBases["RelationMgr"].requestRelationUID( self )
		except KeyError:
			INFO_MSG( "RelationMgr has not been ready yet." )

	def addRef( self, globalName, baseMailbox ):
		"""
		defined method.
		֪ͨ��������

		@param globalName: ȫ��base��ʶ��
		@type  globalName: STRING
		@param baseMailbox: �������ߵ�mailbox
		@type  baseMailbox: MAILBOX
		@return: һ�������˵ķ�����û�з���ֵ
		"""
		self.globalData[globalName] = baseMailbox

	def removeRef( self, globalName ):
		"""
		defined method.
		֪ͨɾ������

		@param baseMailbox: �������ߵ�mailbox
		@type  baseMailbox: MAILBOX
		@return: һ�������˵ķ�����û�з���ֵ
		"""
		try:
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ] = self				# globalData �б�����ǹҵ��� base������������
																	# globalData[C_PREFIX_GBAE] (hyw--2009.06.30)
			del self.globalData[globalName]
		except KeyError:
			WARNING_MSG( "no global base entity %s." % globalName )
			pass

	def loginAttemperTrigger( self ):
		"""
		Define method.
		��¼����״̬�ı���
		"""
		loginAttemper.loginAttemperTrigger()

	def getBaseAppCount( self ):
		"""
		�����Ϸ��ǰ��baseApp����
		"""
		return len( self.globalData )

	def getPlayerCount( self ):
		"""
		��õ�ǰbaseApp��Ϸ�е���Ҹ���
		"""
		return len( self._localPlayers )

	# -----------------------------------------------------------------
	# ������ҵ�¼���
	# -----------------------------------------------------------------
	def registerPlayer( self, entity ):
		"""
		�Ǽ�һ����ҵ�entity�����б��Ǽǵ���Ҷ�����Ϊ�����ߵ�
		"""
		self._localPlayers[entity.getName()] = entity
		
		camp = entity.getCamp()
		if self._localCampPlayers.has_key( camp ):
			self._localCampPlayers[ camp ].append( entity )
		else:
			self._localCampPlayers[ camp ] = [ entity ]
			
		BigWorld.baseAppData[ loginAttemper.playerCountKey ] += 1

	def deregisterPlayer( self, entity ):
		"""
		ȡ����һ�����entity�ĵǼ�
		"""
		del self._localPlayers[entity.getName()]
		camp = entity.getCamp()
		for index, e in enumerate( self._localCampPlayers[ camp ] ):
			if e.id == entity.id:
				del self._localCampPlayers[ camp ][ index ]
				break
				
		BigWorld.baseAppData[ loginAttemper.playerCountKey ] -= 1
		loginAttemper.loginAttemperTrigger()
		

	def iterOnlinePlayers( self ):
		"""
		��ȡһ��������ҵ�iterator

		@return: iterator
		"""
		return self._localPlayers.itervalues()

	# -----------------------------------------------------------------
	# ������Ϣ�㲥���
	# -----------------------------------------------------------------
	def _localBroadcast( self, chid, spkID, spkName, msg, blobArgs ):
		"""
		Define method.
		�㲥��ҵķ������ݵ���ǰBaseApp������ client
		@param				chid	: �㲥Ƶ�� ID
		@type				chid	: INT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: ������ entityID
		@param				spkName : Դ˵��������
		@type				spkName : STRING
		@param				msg		: ��Ϣ����
		@type				msg		: STRING
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: ��Ϣ�����б�
		@return						: һ�������˵ķ�����û�з���ֵ
		"""
		for e in self._localPlayers.itervalues():							# �㲥��ÿ�����ߵ� client
			# ��ֹĳ��baseApp������㲥��Ϣʧ�ܣ������쳣
			try:
				e.client.chat_onChannelMessage( chid, spkID, spkName, msg, blobArgs )
			except:
				EXCEHOOK_MSG( "check role's validity error" )

	def globalChat( self, chid, spkID, spkName, msg, blobArgs ):
		"""
		Define method.
		�㲥��ҵķ������ݵ����е�BaseApp( ֪ͨÿ��baseApp, �����Լ� )
		@param				chid	: �㲥Ƶ�� ID
		@type				chid	: UINT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: ������ entityID
		@param				spkName : Դ˵��������
		@type				spkName : STRING
		@param				msg		: ��Ϣ����
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: ��Ϣ�����б�
		@type				msg		: STRING
		@return						: һ�������˵ķ�����û�з���ֵ
		"""
		for e in self.globalData.itervalues():
			e._localBroadcast( chid, spkID, spkName, msg, blobArgs )
	
	def campChat( self, campID, chid, spkID, spkName, msg, blobArgs ):
		"""
		Define method.
		��Ӫ����
		@param				campID	: ��ӪID
		@type				chid	: UINT8
		@param				chid	: �㲥Ƶ�� ID
		@type				chid	: UINT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: ������ entityID
		@param				spkName : Դ˵��������
		@type				spkName : STRING
		@param				msg		: ��Ϣ����
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: ��Ϣ�����б�
		@type				msg		: STRING
		@return						: һ�������˵ķ�����û�з���ֵ
		"""
		for e in self.globalData.itervalues():
			e.campChatLocal( campID, chid, spkID, spkName, msg, blobArgs )
	
	def campChatLocal( self, campID, chid, spkID, spkName, msg, blobArgs ):
		"""
		Define method.
		�㲥��ҵķ������ݵ���ǰͬ��ӪBaseApp������ client
		@param				chid	: �㲥Ƶ�� ID
		@type				chid	: INT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: ������ entityID
		@param				spkName : Դ˵��������
		@type				spkName : STRING
		@param				msg		: ��Ϣ����
		@type				msg		: STRING
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: ��Ϣ�����б�
		@return						: һ�������˵ķ�����û�з���ֵ
		"""
		chatList = self._localCampPlayers.get( campID, [] )
		for e in chatList:
			try:
				e.client.chat_onChannelMessage( chid, spkID, spkName, msg, blobArgs )
			except:
				EXCEHOOK_MSG( "check role's validity error" )

	def anonymityBroadcast( self, msg, blobArgs ) :
		"""
		defined method
		�����㲥
		ע�⣺�㲥��Ƶ���ǣ�csdefine.CHAT_CHANNEL_SYSBROADCAST
		hyw--2009.09.15
		@param					msg : ��Ϣ����
		@type					msg : STRING
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: ��Ϣ�����б�
		"""
		for e in self.globalData.itervalues():
			e._localBroadcast( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msg, blobArgs )
			
	def campActivity_broadcast( self, msgDict, blobArgs ):
		"""
		define method
		��Ӫ��㲥
		"""
		self.campChatLocal( csdefine.ENTITY_CAMP_TAOISM, csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msgDict.get( csdefine.ENTITY_CAMP_TAOISM ), blobArgs )
		self.campChatLocal( csdefine.ENTITY_CAMP_DEMON, csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msgDict.get( csdefine.ENTITY_CAMP_DEMON ), blobArgs )
		
	# ----------------------------------------------------------------
	# �����ԣ�hyw--2010.06.10��
	# ----------------------------------------------------------------
	def _localWallowNotify( self, accInfos ) :
		"""
		�����Ա��ط�����֪ͨ
		@type				accInfos : list
		@param				accInfos : a list of :
			{
				aname  : STRING: �˺���
				state  : MACRO DEFINATION: ����״̬���� csdefine �ж��壺WALLOW_XXX
				olTime : INT64: ����ʱ��
			}
		"""
		dInfos = {}
		for accInfo in accInfos :
			dInfos[accInfo['accName']] = ( accInfo["olState"], accInfo["olTime"] )
		for e in self._localPlayers.itervalues() :
			eAccount = getattr( e, "accountEntity", None )
			if not eAccount : continue
			info = dInfos.pop( eAccount.playerName, None )
			if info :
				e.wallow_onWallowNotify( *info )
			if len( dInfos ) == 0 :
				break

	def wallowNotify( self, accInfos ) :
		"""
		����֪ͨ
		@type				accInfos : list
		@param				accInfos : a list of :
			{
				aname  : STRING: �˺���
				state  : MACRO DEFINATION: ����״̬���� csdefine �ж��壺WALLOW_XXX
				olTime : INT64: ����ʱ��
			}
		"""
		for e in self.globalData.itervalues() :
			e._localWallowNotify( accInfos )


	# ----------------------------------------------------------------
	# Զ�̵��÷�װ
	# ----------------------------------------------------------------
	def globalRemoteCallClient( self, methodName ):
		"""
		����������ҵ�clientԶ�̷������������޲����ķ�����16:40 2009-4-11��wsf

		@param methodName : Զ�̷�����
		@type methodName : STRING
		"""
		for e in self.globalData.itervalues():
			e.remoteCallPlayerClient( methodName )

	def remoteCallPlayerClient( self, methodName ):
		"""
		Define method.
		ͨ��mailbox���õ�ǰbaseapp������ҵ�Զ�̷��������������в�����16:51 2009-4-11��wsf

		@param methodName : Զ�̷�����
		@type methodName : STRING
		"""
		for e in self._localPlayers.itervalues():
			if not isinstance( e, Role ) or not hasattr( e, "client" ): continue
			try:
				method = getattr( e.client, methodName )
			except AttributeError, errstr:
				ERROR_MSG( "player's mailbox has no this attribut( %s ).%s" % ( methodName, errstr ) )
				return
			method()
	
	def globalRemoteCallCampClient( self, camp, methodName, args ):
		"""
		����ĳ��Ӫ��ҵ�clientԶ�̷���
		
		@param camp : ��Ӫ
		@type camp : UINT8
		@param methodName : Զ�̷�����
		@type methodName : STRING
		@param args :  ����
		@type args : PY_ARGS
		"""
		for e in self.globalData.itervalues():
			e.remoteCallCampPlayerClient( camp, methodName, args )
	
	def remoteCallCampPlayerClient( self, camp, methodName, args ):
		"""
		Define method.
		ͨ��mailbox���õ�ǰbaseappĳ��Ӫ������ҵ�clientԶ�̷������������Դ�������

		@param camp : ��Ӫ
		@type camp : UINT8
		@param methodName : Զ�̷�����
		@type methodName : STRING
		@param args :  ����
		@type args : PY_ARGS
		"""
		for e in self._localCampPlayers.get( camp, [] ):
			if not isinstance( e, Role ) or not hasattr( e, "client" ): continue
			try:
				method = getattr( e.client, methodName )
			except AttributeError, errstr:
				ERROR_MSG( "player's mailbox has no this attribut( %s ).%s" % ( methodName, errstr ) )
				return
			method( *args )
	
	def globalRemoteCallCampCell( self, camp, methodName, args ):
		"""
		����ĳ��Ӫ��ҵ�cellԶ�̷���
		
		@param camp : ��Ӫ
		@type camp : UINT8
		@param methodName : Զ�̷�����
		@type methodName : STRING
		@param args :  ����
		@type args : PY_ARGS
		"""
		for e in self.globalData.itervalues():
			e.remoteCallCampPlayerCell( camp, methodName, args )
	
	def remoteCallCampPlayerCell( self, camp, methodName, args ):
		"""
		Define method.
		ͨ��mailbox���õ�ǰbaseappĳ��Ӫ������ҵ�Զ��cell������������������

		@param camp : ��Ӫ
		@type camp : UINT8
		@param methodName : Զ�̷�����
		@type methodName : STRING
		@param args :  ����
		@type args : PY_ARGS
		"""
		for e in self._localCampPlayers.get( camp, [] ):
			if not isinstance( e, Role ) or not hasattr( e, "cell" ): continue
			try:
				method = getattr( e.cell, methodName )
			except AttributeError, errstr:
				ERROR_MSG( "player's mailbox has no this attribut( %s ).%s" % ( methodName, errstr ) )
				return
			method( *args )
	
	def globalCallEntityCellMothod( self, roleID, methodName, args ):
		"""
		Define mthod.
		ͨ����ҵ�ID����ָ��entity��cell�ķ���
		@ roleID ��role id 
		@ methodName ��Զ��Cell������ STRING
		@ args ������ PY_DICT
		"""
		if BigWorld.entities.has_key( roleID ):
			self.remoteCallEntityCellMothod( roleID, methodName, args )
		else:
			for e in self.globalData.itervalues():
				e.remoteCallEntityCellMothod( roleID, methodName, args )
	
	def remoteCallEntityCellMothod( self, roleID, methodName, args ):
		"""
		Define mthod.
		ͨ��mailbox���õ�ǰĳentity��cell����
		"""
		if BigWorld.entities.has_key( roleID ):
			roleBase = BigWorld.entities[ roleID ]
			if hasattr( roleBase, "cell" ):
				if hasattr( roleBase.cell, methodName ):
					method = getattr( roleBase.cell, methodName )
					method( *args )
			else:
				INFO_MSG( "Can't find Entity by id %i, maybe it had been destroyed or in other baseapp!" % roleID )

	def queryAllPlayerAmount( self, queryerMB, params ):
		"""
		��ѯ���������
		"""
		for e in self.globalData.itervalues():
			e.queryLocalPlayerAmount( queryerMB, params )

	def queryLocalPlayerAmount( self, queryerMB, params ):
		"""
		define method
		��ѯ��BASSAPP����
		"""
		queryerMB.client.onStatusMessage( csstatus.BASEAPP_ROLE_AMOUNT, str(( len(self._localPlayers), )) )


	def queryAllPlayerName( self, queryerMB, params ):
		"""
		��ѯ�������
		"""
		for e in self.globalData.itervalues():
			e.queryLocalPlayersName( queryerMB, params )

	def queryLocalPlayersName( self, queryerMB, params ):
		"""
		define method
		��ѯ��BASSAPP�������
		"""
		info = ""
		for i in self._localPlayers:
			info += i + ", "
		queryerMB.client.onStatusMessage( csstatus.BASEAPP_ROLE_NAME, str(( info, )) )


	# -----------------------------------------------------------------
	# timer
	# -----------------------------------------------------------------
	def onTimer( self, timerID, userData ):
		"""
		"""
		# �꿴lookupRoleBaseByName()����õ�addTimer()
		# ����ʱ������
		if userData == TIMER_LOOKUP_ROLE_BASE:
			time = BigWorld.time()
			for k, v in self._tmpSearchCache.items():	# ʹ��items()��ֱ�Ӹ����б�������ѭ�������ֱ��ɾ���ֵ����ݣ��˷���ֻ�������������ݵĵط�
				if time >= v[1]:
					del self._tmpSearchCache[k]
					v[2]( None )

			# ���û�����������ˣ�����ֹͣtimer
			if len( self._tmpSearchCache ) == 0:
				self.delTimer( self._searchTimerID )
				self._searchTimerID = 0
		elif userData == TIMER_SHUTDOWN_SERVER:
			self.shutdown()
		elif userData == TIMER_DELAY_SHUTDOWN:
			self.delayShutdownTimer()
		else:
			assert False, "unknow timer, timerID = %s, userData = %s" % ( timerID, userData )

	# -----------------------------------------------------------------
	# about lookupRoleBaseByName() mechanism
	# -----------------------------------------------------------------
	def lookupRoleBaseByName( self, name, callback ):
		"""
		�������ֲ����������ǵ�base mailbox
		@param name: string; Ҫ���ҵ��������ǵ����֡�
		@param callback: function; �ûص�����������һ�����������ڸ��ص����ṩ���ҵ����������ǵ�base mailbox�����δ�ҵ������ֵΪNone��
		@return: None
		"""
		resultID = self._getLookupResultID()
		self._tmpSearchCache[resultID] = [ len( self.globalData ), BigWorld.time() + 2, callback ]	# [ Ԥ�ڻظ�����, ��ʱʱ��д��2��, callback ]
		for v in self.globalData.itervalues():
			v._broadcastLookupRoleBaseByName( self, resultID, name )

		if self._searchTimerID == 0:
			self._searchTimerID = self.addTimer( 1, 1, TIMER_LOOKUP_ROLE_BASE )

	def _broadcastLookupRoleBaseByName( self, resultBase, resultID, name ):
		"""
		defined method.
		����BaseappEntity�ڲ����ã�����ʵ��lookupRoleBaseByName()�Ļص�����

		@param resultBase: BASE MAILBOX
		@param resultID: int32
		@param name: string
		"""
		resultBase._broadcastLookupRoleBaseByNameCB( resultID, self._localPlayers.get( name ) )

	def _broadcastLookupRoleBaseByNameCB( self, resultID, baseMailbox ):
		"""
		defined method.
		����BaseappEntity�ڲ����ã�����ʵ��lookupRoleBaseByName()�Ļص�����
		���baseMailbox��ΪNone�����ʾ�ҵ�����_tmpSearchCache����������ص���
		���baseMailboxΪNone�������е�baseapp�ѻظ�����ʾû���ҵ�����_tmpSearchCache����������ص���
		���baseMailboxΪNone���һظ���baseapp��û��ȫ���ظ���baseapp�Ļظ�����һ��ֱ�ӷ���

		@param baseMailbox: ���ҵ���Ŀ��entity base mailbox
		"""
		if resultID not in self._tmpSearchCache: return		# δ�ҵ���ʾ�Ѿ����ظ��ˣ�����������
		r, time, callback = self._tmpSearchCache[resultID]
		r -= 1
		if baseMailbox is None and r > 0:	# ����������δ�ظ����ı��������ֱ�ӷ���
			self._tmpSearchCache[resultID][0] = r
			return

		del self._tmpSearchCache[resultID]
		# ���û�����������ˣ�����ֹͣtimer
		if len( self._tmpSearchCache ) == 0:
			self.delTimer( self._searchTimerID )
			self._searchTimerID = 0

		# �ص�
		callback( baseMailbox )

	def _getLookupResultID( self ):
		"""
		���һ�����ڹ㲥lookupRoleBaseByName()��Ψһ��idֵ
		@return: INT32
		"""
		self._tmpSearchCurrentID += 1
		if self._tmpSearchCurrentID >= 0x7FFFFFFF:
			self._tmpSearchCurrentID = 1

		# ѭ���жϲ���ȡһ������_tmpSearchCache�д��ڵ�IDֵ
		while self._tmpSearchCurrentID in self._tmpSearchCache:
			self._tmpSearchCurrentID += 1
			if self._tmpSearchCurrentID >= 0x7FFFFFFF:
				self._tmpSearchCurrentID = 1
		return self._tmpSearchCurrentID

	# --------------------------------------------------------------------------
	# �������ر�ǰ��������
	# ֮�����������������Ϊbigworld�ķ������رջ��ƻ������ƣ�
	# �ڴ��������¶��п��ܵ�����һص���
	# --------------------------------------------------------------------------
	def kickoutPlayer( self, amount ):
		"""
		Ŀ�꣺�߳���ǰbaseapp���е���ҽ�ɫ���ʺš�

		@param amount: ������ദ����ٸ����ﵽ����������ٴ���
		@return: ����ʵ�ʴ����entity������
		"""
		INFO_MSG( "%s: begin kickout player. target amount = %i." % ( self.globalName, amount ) )
		i = 0
		for e in BigWorld.entities.values():
			if e.isDestroyed:
				continue
			name = e.__class__.__name__
			if name == "Role":
				# ����ֻ����Role entity
				try:
					e.logoff()
				except:
					# ����д����־�������κδ���
					EXCEHOOK_MSG( "kickout role error" )
			elif name == "Account" and e.avatar is None:
				# �����not e.isDestroyed�����жϣ���Ϊ���Roleֻ��baseʱ��ֱ�Ӱ�����AccountҲdestroy()��
				# ��ʱ�ٵ�������ValueError���쳣��
				# ��Ϊ�����BigWorld.entities.values()�Ѿ����������;destroyed��entity�����ˡ�

				# ����ֻ����avatar����ΪNone��Account entity��
				# ����avatar��ΪNone��Account entity����Role entity�����˳���Ϊ
				try:
					e.logoff()
				except:
					# ����д����־�������κδ���
					EXCEHOOK_MSG( "kickout account error" )
			else:
				continue

			i += 1
			# ÿ�����ر��߳�һ�����Ľ�ɫ���Ա��⸺�ع��߶���ǿ��kill��
			if i >= amount: break
		return i

	def saveManagersBeforeShutdown( self ):
		"""
		��shutdown��ǰbaseapp֮ǰ������Щ��Ҫ�洢�����ݵĹ�������
		"""
		INFO_MSG( "%s: save other datas before shutdown" % self.globalName )
		# ��serverͣ��֮ǰ��������̳�����
		if BigWorld.globalBases.has_key( "SpecialShopMgr" ):
			entity = BigWorld.entities.get( BigWorld.globalBases[ "SpecialShopMgr" ].id )
			entity and entity.save()

		# ������Լ������Ĺػ�ǰ����
		if BigWorld.globalData.has_key( "TongManager" ):
			BigWorld.globalData[ "TongManager" ].save()

	def shutdown( self ):
		"""
		defined method.
		�رշ�������ǰ�ú����������ǰbaseapp���̵����н�ɫ��������Ҫд�����ݿ�����ݡ�
		�˺������ڹرշ�����ǰ������Ĺ��ߵ��á�һ�㱻shutdownAll()����
		�˽ӿڴ���������Ϊ��
		1.�߳���baseapp���е�¼����ң�
		2.�������б�baseapp��������Ҫ��������ݼ�entity����
		"""
		# ���û����timer����һ����һ����һ��
		# ע�⣺addTimer()��ļ������̫�̣������
		# ����һ����ɫ���ʺű��߶�ε����⡣
		# ���run state��Ϊ0���Ǳ�ʾ��ǰ�������Ѵ��ڱ��ر�״̬��
		# ��Ӧ�ü��������ˡ�
		if self._shutdownTimerID == 0 and self.runState == 0:
			# timer�ļ������̫С��̫С�������ظ�logout entity�����⡣
			self._shutdownTimerID = self.addTimer( 0.5, 0.5, TIMER_SHUTDOWN_SERVER )
			INFO_MSG( "%s: shutdown server now." % self.globalName )
			self.runState = 1

		if self.runState == 1:		# ���������״̬
			# һ��ֻ��һ���������ˣ��Ա��������ݷ籩����ĸ����ģ��Ӷ����·�������ǿ��kill����
			# ��������߳���������һ���������ʾ��baseapp������ң����Ҫ��ʼִ����һ���ۡ�
			if self.kickoutPlayer( 50 ) < 50:
				self.runState = 2
				INFO_MSG( "%s: kickout player over." % self.globalName )

		elif self.runState == 2:	# ���ڴ���������Ҫ���������״̬
			self.saveManagersBeforeShutdown()

			# ��Ȼ��ǰ����һ�����������������Ҫ��������ݣ�
			# ����������Ȼ��ȴ�һ��timer�Ĵ�����
			# ��ȷ����Ҫд�����ݿ������ȫ����д�롣
			self.runState = 3
		elif self.runState == 3:
			self.runState = 4
			self.delTimer( self._shutdownTimerID )
			self._shutdownTimerID = 0

			# ������Ժ�̨���ͷ������ر���Ϣ��2010.06.09����hyw��
			if BigWorld.globalBases.has_key( "AntiWallowBridge" ) :
				BigWorld.globalBases["AntiWallowBridge"].onServerShutdown()

			INFO_MSG( "%s: server was shutdown." % self.globalName )
		else:
			assert False, "Here has bug. shutdownTimerID = %i, run state = %i." % ( self._shutdownTimerID, self.runState )

	def shutdownAll( self, delay ):
		"""
		defined method.
		�رշ�������ǰ�ú����������ǰbaseapp���̵����н�ɫ��������Ҫд�����ݿ�����ݡ�
		�˺������ڹرշ�����ǰ������Ĺ��ߵ��ã����߱�GMָ����á�
		���磺bigworld/tools/server/runscript�����˽ӿڴ���������Ϊ��

		1.�߳����е�¼����ң�
		2.����������Ҫ��������ݼ�entity����

		@param delay: ��ʱ�೤ʱ���رգ�0 == �����ر�
		"""
		if delay <= 0:
			INFO_MSG( "%s: shutdown all server now." % self.globalName )
			for e in self.globalData.itervalues():
				e.shutdown()
		else:
			self.delayShutdownTimer = ShutdownTimer( self, delay )

	# ----------------------------------------------------------------
	# ϵͳԶ�̸�һ��Ŀ��ʩ��ĳ������
	# ----------------------------------------------------------------
	def castSpellBroadcast( self, targetEntityID, skillID ) :
		"""
		defined method.
		@param	targetEntityID		: entity ��id
		@type	targetEntityID		: int32
		@param	skillID				: ����ID
		@type	skillID				: int64
		@return			None
		"""
		for e in self.globalData.itervalues() :
			e.remoteCastSpell( targetEntityID, skillID )

	def remoteCastSpell( self, targetEntityID, skillID ) :
		"""
		defined method.
		��Ӵ˷�����ԭ��
			��ɫ��һ����ͼ������һ����ͼʱ��ϵͳ���Ȱѽ�ɫ�ӵ�ǰ��ͼ���٣�����˿�
			�պ�Ҫ�Ը����ʩ��ĳ�����ܣ���cell�ϻ�����Ҳ�����ҵ���������������
			��ͨ������ϵͳʩ�ŵģ�����Ҫĳ��ʵ�ڵ�entity����Ȼʵ�����Ǵ�ĳ��entity
			����������Ϊ�������༼��ʵ���ϲ�����ҪԴĿ�꣬���ֹPK���ܣ�����˰�ʩ
			�ż��ܵ���Ϊͨ��base�ҵ�����ʩչĿ���cell�ټ���ʩ�Ŷ�����
		@param	targetEntityID		: entity ��id
		@type	targetEntityID		: int32
		@param	skillID				: ����ID
		@type	skillID				: int64
		@return			None
		"""
		target = BigWorld.entities.get( targetEntityID, None )
		if hasattr( target, "cell" ) :
			if hasattr( target.cell, "systemCastSpell" ) :
				target.cell.systemCastSpell( skillID )
		else :
			INFO_MSG( "Can't find target by id %i, maybe it had been destroyed or in other baseapp!" % targetEntityID )

	def getRelationUID( self ):
		"""
		������ҹ�ϵuid
		"""
		uid = self.currentRelationUID
		if uid == self.maxRelationUID:
			uid = -1
		else:
			self.currentRelationUID += 1
		if self.maxRelationUID - self.currentRelationUID < 10:	# relationUID����С��10ʱ��uidFactory�����µ�uid��Դ
			BigWorld.globalBases["RelationMgr"].requestRelationUID( self )
		return uid

	def receiveRelationUID( self, startUID ):
		"""
		Define method.
		������ҹ�ϵuid

		uid��ʼ�ı�ţ�����Const.RELATION_UID_SAND_MAX_COUNT��
		"""
		self.currentRelationUID = startUID
		self.maxRelationUID = startUID + Const.RELATION_UID_SAND_MAX_COUNT

	# ----------------------------------------------------------------
	# ��������˺ż�¼
	# ----------------------------------------------------------------
	def registerAccount( self, account ):
		"""
		�Ǽ�һ�������˵��˺�
		"""
		self._localAccounts[account.playerName] = account


	def deregisterAccount( self, account ):
		"""
		ȡ����һ���˺ŵĵǼ�
		"""
		try:
			self._localAccounts.pop(account.playerName)
		except:
			EXCEHOOK_MSG()

	def fetchGold( self, accountName ):
		"""
		��ȡԪ��
		"""
		try:
			account = self._localAccounts[accountName]
			if not account.isDestroyed:
				if account.avatar is not None:
					account.avatar.pcu_takeThings( csconst.PCU_TAKECHARGE, 0 )
		except:
			return

	def kickoutAccount( self, accountName ):
		"""
		�߳�ָ���˺�
		"""
		try:
			account = self._localAccounts[accountName]
			if not account.isDestroyed:
				account.logoff()
		except:
			return

	def addAllBasePlayerCountLogs( self, pType, aType, action, param1, param2, param3, param4, param5 ):
		"""
		define method
		��¼��ǰ���������־��
		"""
		for e in self.globalData.itervalues():
			e.addPlayerCountLog(  pType, aType, action, param1, param2, param3, param4, param5 )
	
	
	def addPlayerCountLog( self, pType, aType, action, param1, param2, param3, param4, param5 ):
		"""
		define method
		��¼��ǰ���������־��
		"""
		try:
			g_logger.countOnlineAccountLog( len( self._localAccounts ), param1, param2, param3, param4, param5 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	# ----------------------------------------------------------------
	# ��ѯ���װ��
	# ----------------------------------------------------------------
	def queryRoleEquipItems( self, playerMB, queryName ):
		for e in self.globalData.itervalues():
			e.remoteQueryRoleEquipItems( playerMB, queryName )

	def remoteQueryRoleEquipItems( self, playerMB, queryName ):
		"""
		define method.
		"""
		if self._localPlayers.get( queryName ):
			self._localPlayers.get( queryName ).cell.onQueryRoleEquipItems( playerMB )

# BaseappEntity

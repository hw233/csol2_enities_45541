# -*- coding: gb18030 -*-
#

# $Id: DartManager.py,v 1.1 2008-09-05 03:41:04 zhangyuxing Exp $

import BigWorld
from bwdebug import *
from Function import Functor
import csstatus
import csconst
import time
import Love3
import csdefine
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

SUB_PRESTIGE = 1									#��������
SET_PRESTIGE = 2									#��������
QUERY_PLAYER = 3									#��ѯ���

DistanceTime = 60 * 60 * 2400   #һ���ʱ��
DestoryDartRelationTime = 1			   	#ȥ���ڳ�����ҹ�ϵ����ѭʱ��
QUERYPLAYERTIME			= 2				#ÿ��3���ѯ���һ��

class DartManager( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "DartManager", self._onRegisterManager )
		self.addTimer( DistanceTime, 2, SUB_PRESTIGE )
		self.newPlayerMsg = {}						#�ڳ�����ҷ�����Ϣ	{ "�������"�� msgID, ... }
		self.savePlayMsg = {}						#��Ҫ������ڳ�����ҷ�����Ϣ	{ "�������"�� msgID, ... }
		self.dartFailed = []						#����ʧ�ܴ����б�  itme: �������
		self.dartRelation = {}						#������Һ��ڳ��Ĺ��� {"�������":(�ڳ�baseMailBox,�ڳ�������ͼ��), ... }
		self.addTimer( QUERYPLAYERTIME, QUERYPLAYERTIME, QUERY_PLAYER )


	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register DartManager Fail!" )
			# again
			self.registerGlobally( "DartManager", self._onRegisterManager )
		else:
			BigWorld.globalData["DartManager"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("DartManager Create Complete!")

			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
					  	"DartActivity_start" : "onStart",
					  	"DartActivity_end" : "onEnd",
					  	"DartActivity_start_notice": "onStartNotice",
					  	"DartActivity_end_notice": "onEndNotice",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "DartActivity_start", self, "onStart" )


	def onStartNotice( self ):
		"""
		define method
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_YB_PREPARE_NOTIRY, [] )

	def onEndNotice( self ):
		"""
		define method
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_YB_SHOULD_END_NOTIFY, [] )


	def onStart( self ):
		"""
		define method
		"""
		if BigWorld.globalData.has_key( "Dart_Activity" ):
			curTime = time.localtime()
			ERROR_MSG( "���˻���ڽ��У�%i��%i����ͼ�ٴο�ʼ���˻��"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_YB_BEGIN_NOTIFY, [] )
		BigWorld.globalData['Dart_Activity'] = True


	def onEnd( self ):
		"""
		define method.
		�����
		"""
		# ��ֹ�������ڻ��ʼʱ��֮������ ���Ҳ����ñ��
		if not BigWorld.globalData.has_key( "Dart_Activity" ):
			curTime = time.localtime()
			ERROR_MSG( "���˻�Ѿ�������%i��%i����ͼ�ٴν������ˡ�"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_YB_END_NOTIFY, [] )
		if BigWorld.globalData.has_key( "Dart_Activity" ):
			del BigWorld.globalData['Dart_Activity']



	def add( self, playerName, key, value ):
		"""
		define method
		����key�ж�Ӧ����ֵ
		"""
		query = "select %s from custom_DartTable where sm_playerName = \'%s\'" \
				 % ( key, BigWorld.escape_string( playerName ) )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._addCB, playerName, key, value ) )


	def _addCB( self, playerName, key, value, resultSet, rows, errstr ):
		"""
		����key�ж�Ӧ����ֵ�ص�
		"""

		tempTuble = None
		if key == "sm_dartCreditXinglong":
			tempTuble = ( playerName, value, 0, 0, 0 )
		elif key == "sm_dartCreditChangping":
			tempTuble = ( playerName, 0, value, 0, 0 )
		elif key == "sm_dartNotoriousXinglong":
			tempTuble = ( playerName, 0, 0, value, 0 )
		elif key == "sm_dartNotoriousChangping":
			tempTuble = ( playerName, 0, 0, 0, value )
		else:
			return

		if errstr:		# ��ѯ����,�޴���
			INFO_MSG( errstr )
			return
		if resultSet == []:	# û�в鵽�κ�����
			query = "insert into custom_DartTable ( sm_playerName, sm_dartCreditXinglong, sm_dartCreditChangping, sm_dartNotoriousXinglong, sm_dartNotoriousChangping) value ( \'%s\', %i, %i, %i, %i );" \
						% tempTuble
			BigWorld.executeRawDatabaseCommand( query, Functor( self._UpdateDartManagerCB, "create", key, BigWorld.escape_string( playerName ), value ) )
			return

		credit = int(resultSet[0][0]) + value

		query = "update custom_DartTable set %s = %i where sm_playerName = \'%s\'" %( key, credit, BigWorld.escape_string( playerName ) )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._UpdateDartManagerCB, "update", key, playerName, value ) )


	def _UpdateDartManagerCB( self, action, key, playerName, value, result, dummy, errstr ):
		"""
		"""
		if errstr:
			INFO_MSG( "error: DartManager, Action: %s, Key: %s failure ! Player: %s, value: %i "% ( action, key, playerName, value ) )
			return



	def query( self, key, len, dartNpcCellMailBox ):
		"""
		define method
		��ѯ
		"""
		query = "select sm_playerName, %s from custom_DartTable order by %s DESC limit %i" %( key, key, len )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryCB, key, len, dartNpcCellMailBox ) )


	def _queryCB( self, key, len, dartNpcCellMailBox, resultSet, rows, errstr ):
		"""
		��ѯ�ص�
		"""
		if errstr:		# ��ѯ����,�޴���
			INFO_MSG( errstr )
			return

		if len(resultSet[0]) == 0:
			return

		dartMessages = []

		for i in resultSet:
			dartMessages.append( i[0] )
			dartMessages.append( i[1] )

		dartNpcCellMailBox.refreshDartMessage( key, dartMessages )


	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == SUB_PRESTIGE:
			self.subAllPrestige("sm_dartCreditXinglong", 5)
			self.subAllPrestige("sm_dartCreditChangping", 5)
			self.subAllPrestige("sm_dartNotoriousXinglong", 5)
			self.subAllPrestige("sm_dartNotoriousChangping", 5)
			self.addTimer( DistanceTime, 2, SUB_PRESTIGE )

		if userArg == QUERY_PLAYER:
			for iPlayerName in self.newPlayerMsg:
				BigWorld.lookUpBaseByName( 'Role', iPlayerName,  Functor( self._handleDartMsgCB, iPlayerName, self.newPlayerMsg[iPlayerName] ) )
			self.newPlayerMsg = {}

	def subAllPrestige( self, key, value ):
		"""
		"""
		query = "select sm_playerName, %s from custom_DartTable" %( BigWorld.escape_string( key ) )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._subAllPrestigeCB, key, value ) )

	def _subAllPrestigeCB( self, key, value, resultSet, rows, errstr ):
		"""
		"""
		if errstr:		# ��ѯ����,�޴���
			INFO_MSG( errstr )
			return

		dartMessages = []

		for i in resultSet:
			if int(i[1]) >= value:
				i[1] = int(i[1]) - value
			if int(i[1]) <= -value:
				i[1] = int(i[1]) + value
			query = "update custom_DartTable set '%s' = %i where sm_playerName = '%s'" %( BigWorld.escape_string( key ), i[1], BigWorld.escape_string( i[0] ) )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._UpdateDartManagerCB, "update", key, i[0], value ) )


	def requestPlayerDartPrestige( self, playerName, playerBaseMailBox ):
		"""
		define method
		"""
		self.queryForPlayer( playerName, playerBaseMailBox )



	def queryForPlayer( self, playerName, playerBaseMailBox ):
		"""
		define method
		��ѯ
		"""
		query = "select sm_dartCreditXinglong,sm_dartCreditChangping from custom_DartTable where sm_playerName = '%s'" % BigWorld.escape_string( playerName )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryForPlayerCB, playerName, playerBaseMailBox ) )


	def _queryForPlayerCB( self, playerName, playerBaseMailBox, resultSet, rows, errstr ):
		"""
		��ѯ�ص�
		"""
		if errstr:		# ��ѯ����,�޴���
			INFO_MSG( errstr )
			return

		dartMessages = []

		for i in resultSet:
			dartMessages.append( i[0] )
			dartMessages.append( i[1] )

		if len(dartMessages) == 0:
			return
		playerBaseMailBox.cell.updateDartPrestige( int(dartMessages[0]), int(dartMessages[1]) )


	def addDartMessage( self, playerName, msg, isSave ):
		"""
		define method
		�ڳ��Ҳ�����ң���������Ƿ����߶���Ҫ��ҽ��յ�����Ϣ
		"""
		if isSave:
			self.savePlayMsg[playerName] = msg
		self.newPlayerMsg[playerName] = msg
		if msg == csstatus.ROLE_QUEST_DART_NPC_DIE:
			self.dartFailed.append(playerName)
			BigWorld.lookUpBaseByName( 'Role', playerName, Functor( self._handleDartFailedCB, playerName ) )

	def _handleDartFailedCB( self, playerName, callResult ):
		"""
		��������ʧ��
		"""
		if not isinstance( callResult, bool ):
			if hasattr( callResult, "cell" ):
				callResult.cell.handleDartFailed()
				self.dartFailed.remove( playerName )

	def _handleDartMsgCB( self, playerName, msg, callResult ):
		"""
		�����ڳ���Ϣ�����
		"""
		if not isinstance( callResult, bool ):
			if hasattr( callResult, "cell" ):
				callResult.cell.handleDartMsg( msg )
				if self.newPlayerMsg.has_key( playerName ):
					del self.newPlayerMsg[playerName]
				if self.savePlayMsg.has_key( playerName ):
					del self.savePlayMsg[playerName]

	def queryAboutDart( self, playerName, playerMailBox ):
		"""
		define method
		������߲�ѯ�������
		"""
		if playerName in self.dartFailed:
			self.dartFailed.remove( playerName )
			playerMailBox.cell.handleDartFailed()

		if self.savePlayMsg.has_key( playerName ):
			playerMailBox.cell.handleDartMsg( self.savePlayMsg[playerName] )
			del self.savePlayMsg[playerName]
		
		if self.dartRelation.has_key( playerName ):
			dartNPCBase = self.dartRelation[playerName][0]
			dartNPCBase.cell.updateOwnerBaseMailbox( playerMailBox )
			playerMailBox.cell.setTemp( "dart_id", dartNPCBase.id )


	def buildDartRelation( self, playerName, spaceName, dartMailBox, factionID ):
		"""
		define method
		������Һ��ڳ���ϵ
		
		@param factionID : �����ھ�����id��csdefine.FACTION_XINGLONG or csdefine.FACTION_CHANGPING
		"""
		self.dartRelation[playerName] = ( dartMailBox, spaceName, factionID )


	def requestToDestoryDartRelation( self, playerName ):
		"""
		define method
		�����ƻ���Һ��ڳ���ϵ
		"""
		if self.dartRelation.has_key( playerName ):
			self.dartRelation[playerName][0].cell.destoryDartEntity()
			del self.dartRelation[playerName]


	def onReceiveDestoryCommand( self, playerName ):
		"""
		define method
		�õ��ƻ�ȷ��
		"""
		if self.dartRelation.has_key( playerName ):
			del self.dartRelation[playerName]


	def sendOwnerToDart( self, playerName, baseMailbox ):
		"""
		�����ڳ����˵��ڳ�
		"""
		dartInfo = self.dartRelation.get( playerName )
		if dartInfo:
			dartInfo[0].cell.sendOwnerToSelf( baseMailbox )
		else:
			baseMailbox.client.onStatusMessage( csstatus.ROLE_QUEST_DART_HAS_DIED, "" )


	def findOwnerByName( self, playerName ):
		"""
		define method
		�����ڳ�����
		"""
		BigWorld.lookUpBaseByName( "Role", playerName, Functor( self.onFindOwnerByName, playerName ) )


	def onFindOwnerByName( playerName, callResult ):
		"""
		��������ʧ��
		"""
		if not isinstance( callResult, bool ):
			self.dartRelation[playerName][0].cell.updateOwnerID( callResult.id )
			
	def querySpaceDartInfo( self, playerBase, spaceLabel, factionID ):
		"""
		Define method.
		��ѯ��ǰ��ͼ���ڳ�������Ϣ
		
		@param playerBase : �����ѯ�����base
		@type playerBase : mailbox
		@param spaceLabel : ��ͼ��,����fengming
		@type spaceLabel : STRING
		@param factionID : npc��������id
		@type factionID : UINT16
		"""
		count = 0
		targetFactionID = factionID == csdefine.FACTION_CHANGPING and csdefine.FACTION_XINGLONG or csdefine.FACTION_CHANGPING
		for dartInfo in self.dartRelation.itervalues():
			if dartInfo[1] == spaceLabel and dartInfo[2] == targetFactionID:
				count += 1
		playerBase.cell.dart_spaceDartCountResult( count )

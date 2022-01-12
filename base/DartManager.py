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

SUB_PRESTIGE = 1									#减少声望
SET_PRESTIGE = 2									#设置声望
QUERY_PLAYER = 3									#查询玩家

DistanceTime = 60 * 60 * 2400   #一天的时间
DestoryDartRelationTime = 1			   	#去掉镖车和玩家关系的轮循时间
QUERYPLAYERTIME			= 2				#每隔3秒查询玩家一次

class DartManager( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		# 把自己注册为globalData全局实体
		self.registerGlobally( "DartManager", self._onRegisterManager )
		self.addTimer( DistanceTime, 2, SUB_PRESTIGE )
		self.newPlayerMsg = {}						#镖车向玩家发送信息	{ "玩家名字"： msgID, ... }
		self.savePlayMsg = {}						#需要保存的镖车向玩家发送信息	{ "玩家名字"： msgID, ... }
		self.dartFailed = []						#运镖失败处理列表  itme: 玩家名字
		self.dartRelation = {}						#运镖玩家和镖车的关联 {"玩家名字":(镖车baseMailBox,镖车出生地图名), ... }
		self.addTimer( QUERYPLAYERTIME, QUERYPLAYERTIME, QUERY_PLAYER )


	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register DartManager Fail!" )
			# again
			self.registerGlobally( "DartManager", self._onRegisterManager )
		else:
			BigWorld.globalData["DartManager"] = self		# 注册到所有的服务器中
			INFO_MSG("DartManager Create Complete!")

			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
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
			ERROR_MSG( "国运活动正在进行，%i点%i分试图再次开始国运活动。"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_YB_BEGIN_NOTIFY, [] )
		BigWorld.globalData['Dart_Activity'] = True


	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		# 防止服务器在活动开始时间之后启动 则找不到该标记
		if not BigWorld.globalData.has_key( "Dart_Activity" ):
			curTime = time.localtime()
			ERROR_MSG( "国运活动已经结束，%i点%i分试图再次结束国运。"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_YB_END_NOTIFY, [] )
		if BigWorld.globalData.has_key( "Dart_Activity" ):
			del BigWorld.globalData['Dart_Activity']



	def add( self, playerName, key, value ):
		"""
		define method
		增加key中对应的数值
		"""
		query = "select %s from custom_DartTable where sm_playerName = \'%s\'" \
				 % ( key, BigWorld.escape_string( playerName ) )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._addCB, playerName, key, value ) )


	def _addCB( self, playerName, key, value, resultSet, rows, errstr ):
		"""
		增加key中对应的数值回调
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

		if errstr:		# 查询出错,无处理
			INFO_MSG( errstr )
			return
		if resultSet == []:	# 没有查到任何数据
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
		查询
		"""
		query = "select sm_playerName, %s from custom_DartTable order by %s DESC limit %i" %( key, key, len )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryCB, key, len, dartNpcCellMailBox ) )


	def _queryCB( self, key, len, dartNpcCellMailBox, resultSet, rows, errstr ):
		"""
		查询回调
		"""
		if errstr:		# 查询出错,无处理
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
		if errstr:		# 查询出错,无处理
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
		查询
		"""
		query = "select sm_dartCreditXinglong,sm_dartCreditChangping from custom_DartTable where sm_playerName = '%s'" % BigWorld.escape_string( playerName )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryForPlayerCB, playerName, playerBaseMailBox ) )


	def _queryForPlayerCB( self, playerName, playerBaseMailBox, resultSet, rows, errstr ):
		"""
		查询回调
		"""
		if errstr:		# 查询出错,无处理
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
		镖车找不到玩家，不管玩家是否在线都需要玩家接收到的信息
		"""
		if isSave:
			self.savePlayMsg[playerName] = msg
		self.newPlayerMsg[playerName] = msg
		if msg == csstatus.ROLE_QUEST_DART_NPC_DIE:
			self.dartFailed.append(playerName)
			BigWorld.lookUpBaseByName( 'Role', playerName, Functor( self._handleDartFailedCB, playerName ) )

	def _handleDartFailedCB( self, playerName, callResult ):
		"""
		处理运镖失败
		"""
		if not isinstance( callResult, bool ):
			if hasattr( callResult, "cell" ):
				callResult.cell.handleDartFailed()
				self.dartFailed.remove( playerName )

	def _handleDartMsgCB( self, playerName, msg, callResult ):
		"""
		发送镖车信息给玩家
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
		玩家上线查询运镖情况
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
		建立玩家和镖车关系
		
		@param factionID : 所属镖局势力id，csdefine.FACTION_XINGLONG or csdefine.FACTION_CHANGPING
		"""
		self.dartRelation[playerName] = ( dartMailBox, spaceName, factionID )


	def requestToDestoryDartRelation( self, playerName ):
		"""
		define method
		请求破坏玩家和镖车关系
		"""
		if self.dartRelation.has_key( playerName ):
			self.dartRelation[playerName][0].cell.destoryDartEntity()
			del self.dartRelation[playerName]


	def onReceiveDestoryCommand( self, playerName ):
		"""
		define method
		得到破坏确认
		"""
		if self.dartRelation.has_key( playerName ):
			del self.dartRelation[playerName]


	def sendOwnerToDart( self, playerName, baseMailbox ):
		"""
		传送镖车主人到镖车
		"""
		dartInfo = self.dartRelation.get( playerName )
		if dartInfo:
			dartInfo[0].cell.sendOwnerToSelf( baseMailbox )
		else:
			baseMailbox.client.onStatusMessage( csstatus.ROLE_QUEST_DART_HAS_DIED, "" )


	def findOwnerByName( self, playerName ):
		"""
		define method
		查找镖车主人
		"""
		BigWorld.lookUpBaseByName( "Role", playerName, Functor( self.onFindOwnerByName, playerName ) )


	def onFindOwnerByName( playerName, callResult ):
		"""
		处理运镖失败
		"""
		if not isinstance( callResult, bool ):
			self.dartRelation[playerName][0].cell.updateOwnerID( callResult.id )
			
	def querySpaceDartInfo( self, playerBase, spaceLabel, factionID ):
		"""
		Define method.
		查询当前地图的镖车数量信息
		
		@param playerBase : 请求查询的玩家base
		@type playerBase : mailbox
		@param spaceLabel : 地图名,例如fengming
		@type spaceLabel : STRING
		@param factionID : npc所在势力id
		@type factionID : UINT16
		"""
		count = 0
		targetFactionID = factionID == csdefine.FACTION_CHANGPING and csdefine.FACTION_XINGLONG or csdefine.FACTION_CHANGPING
		for dartInfo in self.dartRelation.itervalues():
			if dartInfo[1] == spaceLabel and dartInfo[2] == targetFactionID:
				count += 1
		playerBase.cell.dart_spaceDartCountResult( count )

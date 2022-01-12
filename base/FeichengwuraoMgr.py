# -*- coding: gb18030 -*-


import BigWorld
import cPickle
import csconst
import csstatus
import csdefine
import cschannel_msgs
from LoveMsg import LoveMsg
from LoveMsg import FcwrResult
from LoveMsg import VoteInstance
from bwdebug import *
from Function import Functor
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import items
g_items = items.instance()

LOAD_DATA_CBID	= 12334



REWARD_LOVE_MSG_CONFIG	= {
				 csdefine.FCWR_VOTE_ALL	 		: cschannel_msgs.FCWR_ACTIVITY_RESULT_WAN_ZHONG_ZHU_MU,
				 csdefine.FCWR_VOTE_KAN_HAO		: cschannel_msgs.FCWR_ACTIVITY_RESULT_FU_QI_XIANG, 
				 csdefine.FCWR_VOTE_QING_DI		: cschannel_msgs.FCWR_ACTIVITY_RESULT_DA_ZHONG_QING_SHENG,
				 csdefine.FCWR_VOTE_SHI_LIAN	: cschannel_msgs.FCWR_ACTIVITY_RESULT_MENG_ZHONG_QING_REN,
				 } #	告白奖励
REWARD_VOTE_CONFIG	= { 
				csdefine.FCWR_MAX_COUNT_VOTER_1 : cschannel_msgs.FCWR_ACTIVITY_RESULT_VOTE_1,
				csdefine.FCWR_MAX_COUNT_VOTER_2 : cschannel_msgs.FCWR_ACTIVITY_RESULT_VOTE_2,
				csdefine.FCWR_MAX_COUNT_VOTER_3 : cschannel_msgs.FCWR_ACTIVITY_RESULT_VOTE_3,
				}	#投票奖励





class FCWR_DB:
	"""
	"""
	def __init__( self, mgr ):
		"""
		"""
		self.fcwrMgr = mgr
		self.createTableCount = 0
	
	def createTable( self ):
		"""
		"""
		query = """CREATE TABLE IF NOT EXISTS `custom_FeichengwuraoMsgTable` (
				`id`					BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_index` 				INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_roleDBID` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_receiveTime` 		INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_senderName`	 		VARCHAR(255),
				`sm_receiverName`		VARCHAR(255),
				`sm_msg`				VARCHAR(255),
				`sm_isAnonymity` 		INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_vote_1` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_vote_2` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_vote_3` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_vote_4` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_vote_5` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_vote_6` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_lastVoteTime` 		INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_senderRaceclass`	INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_receiverRaceclass`	INTEGER UNSIGNED NOT NULL DEFAULT 0,
				KEY  ( `sm_index` ),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

		query = """CREATE TABLE IF NOT EXISTS `custom_FeichengwuraoResultTable` (
				`id`					BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_key` 				VARCHAR(255),
				`sm_rewardReason`	 	INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_takenTime`			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_hasTaken`			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_param01`				VARCHAR(255),
				`sm_param02`				VARCHAR(255),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

		query = """CREATE TABLE IF NOT EXISTS `custom_FeichengwuraoVoteTable` (
				`id`					BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_roleName` 			VARCHAR(255),
				`sm_voteStr`			text,
				`sm_voteCount` 			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_voteTime`			INTEGER UNSIGNED NOT NULL DEFAULT 0,
				UNIQUE KEY `sm_roleDBID` (`sm_roleDBID`,`sm_roleName`( 255 )),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )



	def __createTableCB( self, result, rows, errstr ):
		"""
		生成数据库表格回调函数

		param tableName:	生成的表格名字
		type tableName:		STRING
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Create custom_FeichengwuraoMsgTable or custom_FeichengwuraoResultTable or custom_FeichengwuraoVoteTable fault! %s"%errstr  )
			return
		
		self.createTableCount += 1
		if self.createTableCount >= 3:
			self.fcwrMgr.onTableCreate()


	def loadMsgDatas( self ):
		"""
		加载数据
		"""
		query = "select sm_index, sm_roleDBID, sm_receiveTime, sm_senderName, sm_receiverName, sm_msg, sm_isAnonymity, sm_vote_1, sm_vote_2, sm_vote_3, sm_vote_4, sm_vote_5, sm_vote_6, sm_lastVoteTime, sm_senderRaceclass, sm_receiverRaceclass from custom_FeichengwuraoMsgTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onLoadMsgDatas )
		INFO_MSG( "FeichengwuraoDB: Load Feichengwurao Info!" )

	def __onLoadMsgDatas( self, result, rows, errstr ):
		"""
		"""
		if result is None:
			return
		msgInss = []
		for i in result:
			msgIns = LoveMsg()
			msgIns.init( int( i[0] ), int( i[1] ), int( i[2] ), i[3], i[4], i[5], int( i[6] ), int( i[7] ), int( i[8] ), int( i[9] ), int( i[10]), int( i[11] ), int( i[12] ), int( i[13] ), int( i[14] ), int( i[15] ) )
			msgInss.append( msgIns )
		
		self.fcwrMgr.initMsgDatas( msgInss )

	def addLoveMsgToDB( self, msgIns ):
		"""
		把信息写入数据库
		"""
		query = "insert into custom_FeichengwuraoMsgTable ( sm_index, sm_roleDBID, sm_receiveTime, sm_senderName, sm_receiverName, sm_msg, sm_isAnonymity ) value ( %i, %i, %i, \'%s\', \'%s\', \'%s\', %i);"
		BigWorld.executeRawDatabaseCommand( query%(msgIns.index, msgIns.roleDBID, msgIns.receiveTime, BigWorld.escape_string( msgIns.senderName ), BigWorld.escape_string( msgIns.receiverName ), BigWorld.escape_string( msgIns.msg ), msgIns.isAnonymity), self.__onAddLoveMsgToDB )

	def __onAddLoveMsgToDB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Add loveMsg fault! %s"%errstr  )
			return

	def queryRaceclassFromDB( self, msgIns  ):
		"""
		"""
		query = "select sm_playerName, sm_raceclass from tbl_Role where sm_playerName in ( \'%s\', \'%s\' )"
		print query%( BigWorld.escape_string( msgIns.senderName ), BigWorld.escape_string( msgIns.receiverName ) )
		BigWorld.executeRawDatabaseCommand( query%( msgIns.senderName, msgIns.receiverName ), Functor( self.__onQueryRaceclassFromDB, msgIns.index ) )
	
	
	def __onQueryRaceclassFromDB( self, index, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Query loveMsg raceclass Info fault! %s"%errstr  )
			return
		if result is None:
			ERROR_MSG( "FeichengwuraoDB: Query loveMsg raceclass Info! Not find any raceclass info!")
			return
		
		if len( result ) < 2:
			ERROR_MSG( "FeichengwuraoDB: Query loveMsg raceclass Info! Not find enough raceclass info!")
			return
		self.fcwrMgr.updateMsgInfoRaceclassInfo( index, result[0][0], int( result[0][1] ), result[1][0], int( result[1][1] ) )
		


	def updateLoveMsgRaceClassInfoToDB( self, msgIns ):
		"""
		"""
		query = "update custom_FeichengwuraoMsgTable set sm_senderRaceclass= %i, sm_receiverRaceclass= %i where sm_index = %i"
		BigWorld.executeRawDatabaseCommand( query%(msgIns.senderRaceclass, msgIns.receiverRaceclass, msgIns.index), self.__onUpdateLoveMsgRaceClassInfoToDB )


	def __onUpdateLoveMsgRaceClassInfoToDB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Update loveMsg raceclass Info fault! %s"%errstr  )
			return

	def loadVoteDatas( self ):
		"""
		"""
		query = "select sm_roleDBID, sm_roleName, sm_voteTime, sm_voteStr from custom_FeichengwuraoVoteTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onLoadVoteDatas )
	
	def __onLoadVoteDatas(  self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Query FeichengwuraoResult Info fault! %s"%errstr  )
			return
		
		if result is None:
			return
		
		voteInss = []
		for i in result:
			voteIns = VoteInstance()
			try:
				voteIns.init( int( i[0] ), i[1], int( i[2] ), i[3] )
				voteInss.append( voteIns )
			except:
				ERROR_MSG( "voteMsg error: %s"%(i[0]) )
		
		self.fcwrMgr.initVoteDatas( voteInss )

	def updateLoveMsgVoteInfoToDB( self, msgIns ):
		"""
		"""
		query = "update custom_FeichengwuraoMsgTable set sm_vote_1= %i, sm_vote_2= %i, sm_vote_3= %i, sm_vote_4= %i, sm_vote_5= %i, sm_vote_6= %i, sm_lastVoteTime = %i where sm_index = %i"
		BigWorld.executeRawDatabaseCommand( query%(msgIns.vote_1, msgIns.vote_2, msgIns.vote_3, msgIns.vote_4, msgIns.vote_5, msgIns.vote_6, msgIns.lastVoteTime, msgIns.index), self.__onUpdateLoveMsgVoteInfoToDB )


	def __onUpdateLoveMsgVoteInfoToDB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Update loveMsg vote Info fault! %s"%errstr  )
			return


	def loadResultDatas( self ):
		"""
		"""
		query = "select sm_key, sm_rewardReason, sm_takenTime, sm_hasTaken, sm_param01, sm_param02 from custom_FeichengwuraoResultTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onLoadResultDatas )
	
	def __onLoadResultDatas(  self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Query FeichengwuraoResult Info fault! %s"%errstr  )
			return
		
		if result is None:
			return
		
		resultInss = []
		for i in result:
			resultIns = FcwrResult()
			resultIns.init( i[0], int( i[1] ), int( i[2] ), int( i[3] ), i[4], i[5] )
			resultInss.append( resultIns )
		
		self.fcwrMgr.initActivityResult( resultInss )

	def addVoteResultToDB( self, resultIns ):
		"""
		"""
		query = "insert into custom_FeichengwuraoResultTable ( sm_key, sm_rewardReason, sm_takenTime, sm_hasTaken, sm_param01, sm_param02 ) value ( \'%s\', %i, %i, %i, \'%s\', \'%s\');"
		BigWorld.executeRawDatabaseCommand( query%(resultIns.key, resultIns.rewardReason, resultIns.takenTime, resultIns.hasTaken, resultIns.param01, resultIns.param02 ), self.__onAddVoteResultToDB )

	def __onAddVoteResultToDB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Add FeichengwuraoResult fault! %s"%errstr  )
			return

	def updateVoteDataToDB( self, voteIns ):
		"""
		"""
		query = "REPLACE into custom_FeichengwuraoVoteTable ( sm_roleDBID, sm_roleName, sm_voteStr, sm_voteTime, sm_voteCount ) values ( %i, \'%s\', \'%s\', %i, %i );"
		BigWorld.executeRawDatabaseCommand( query%( voteIns.roleDBID, BigWorld.escape_string( voteIns.roleName ), voteIns.makeVoteStr(), voteIns.voteTime, voteIns.getVoteCount() ), self.__onUpdateVoteDataToDB )

	def __onUpdateVoteDataToDB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: Update vote info fault! %s"%errstr  )
			return

	def cleanAllDatasInDB( self ):
		"""
		"""
		query01 = "delete from custom_FeichengwuraoMsgTable"
		query02 = "delete from custom_FeichengwuraoResultTable"
		query03 = "delete from custom_FeichengwuraoVoteTable"
		BigWorld.executeRawDatabaseCommand( query01, self.__onCleanALLDatasInDB )
		BigWorld.executeRawDatabaseCommand( query02, self.__onCleanALLDatasInDB )
		BigWorld.executeRawDatabaseCommand( query03, self.__onCleanALLDatasInDB )
	
	def __onCleanALLDatasInDB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "FeichengwuraoDB: clean all datas fault! %s"%errstr  )
			return



class FeichengwuraoMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.msgDatas 			= {}			# { index01: LoveMsg(), index02 : LoveMsg(),  ...}
		self.resultDatas 		= []			# [ FcwrResult(),FcwrResult(), ...]
		self.voteDatas			= {}			# {	roleDBID: VoteInstance(), ...}
		self.senderMsgGroup 	= {}			# { roleName: [index01, index02], ...}
		self.receiverMsgGroup 	= {}			# { roleName: [index01, index02], ...}
		self.resultDess			= {}			# 奖励描述
		self.fcwrDB = FCWR_DB( self )
		self.registerGlobally( "FeichengwuraoMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register FeichengwuraoMgr Fail!" )
			# again
			self.registerGlobally( "FeichengwuraoMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["FeichengwuraoMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("FeichengwuraoMgr Create Complete!")

		self.registerCrond()
		self.fcwrDB.createTable()

	def onTableCreate( self ):
		"""
		"""
		self.fcwrDB.loadMsgDatas()
		self.fcwrDB.loadVoteDatas()
		self.fcwrDB.loadResultDatas()
		

	def initMsgDatas( self, msgInss ):
		"""
		初始化告白数据
		"""
		for i in msgInss:
			self.msgDatas[i.index] = i
			if not i.receiverName in self.receiverMsgGroup:
				self.receiverMsgGroup[i.receiverName] = set([])
			self.receiverMsgGroup[i.receiverName].add( i.index )

			if not i.senderName in self.senderMsgGroup:
				self.senderMsgGroup[i.senderName] = set([])
			self.senderMsgGroup[i.senderName].add( i.index )


	def initVoteDatas( self, voteInss ):
		"""
		初始化告白数据
		"""
		for i in voteInss:
			self.voteDatas[i.roleDBID] = i

	def initActivityResult( self, resultInss ):
		"""
		初始化活动结束数据
		"""
		
		self.resultDatas.extend( resultInss )

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"feichengwurao_Start" : "onStart",
						"feichengwurao_End" :	"onEnd",
						"feichengwurao_handle_result"	: "onHandle_result",
					  }

		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )


		crond.addAutoStartScheme( "feichengwurao_Start", self, "onStart" )
		crond.addAutoStartScheme( "feichengwurao_handle_result", self, "onHandle_result" )


	def queryLoveMsgByIndex( self, playerBase, index ):
		"""
		define method
		查询一条告白信息
		"""
		if not index in self.msgDatas:
			return
		
		playerBase.client.receiveLoveMsgs( self.msgDatas[index] )

	def queryLoveMsgsByRange( self, playerBase, rangeIndex ):
		"""
		define method
		查询一组告白信息
		"""
		beginIndex 	= rangeIndex * csconst.FCWR_MSGS_LENGTH
		endIndex 	= rangeIndex * csconst.FCWR_MSGS_LENGTH + csconst.FCWR_MSGS_LENGTH
		
		if not endIndex in self.msgDatas:
			endIndex = len( self.msgDatas )
		
		for i in xrange( beginIndex, endIndex ):
			playerBase.client.receiveLoveMsgs( self.msgDatas[i] )

	def queryLoveMsgsByReceiverName( self, playerBase, roleName ):
		"""
		define method
		查询某个接收玩家信息
		"""
		if not roleName in self.receiverMsgGroup:
			return
		for index in self.receiverMsgGroup[roleName]:
			playerBase.client.receiveLoveMsgs( self.msgDatas[index] )

	def queryLoveMsgsBySenderName( self, playerBase, roleName ):
		"""
		define method
		查询某个接收玩家信息
		"""
		if not roleName in self.senderMsgGroup:
			return
		for index in self.senderMsgGroup[roleName]:
			playerBase.client.receiveLoveMsgs( self.msgDatas[index] )



	def addLoveMsg( self, msgIns ):
		"""
		define method
		"""
		index = len(self.msgDatas)
		msgIns.index = index
		self.msgDatas[index] = msgIns
		if not msgIns.receiverName in self.receiverMsgGroup:
			self.receiverMsgGroup[msgIns.receiverName] = set([])
		
		self.receiverMsgGroup[msgIns.receiverName].add( index )

		if not msgIns.senderName in self.senderMsgGroup:
			self.senderMsgGroup[msgIns.senderName] = set([])
		
		self.senderMsgGroup[msgIns.senderName].add( index )
		
		self.fcwrDB.addLoveMsgToDB( msgIns )
		self.fcwrDB.queryRaceclassFromDB( msgIns )

	def updateMsgInfoRaceclassInfo( self, index, roleName01, raceclass01, roleName02, raceclass02 ):
		"""
		"""
		if not index in self.msgDatas:
			ERROR_MSG( "FeichengwuraoMgr: update raceclass fault! not finded the index(%i)!" % index )
			return
		msgIns = self.msgDatas[index]
		if msgIns.senderName == roleName01:
			msgIns.senderRaceclass 		= raceclass01
			msgIns.receiverRaceclass 	= raceclass02
		elif msgIns.senderName == roleName02:
			msgIns.senderRaceclass 		= raceclass02
			msgIns.receiverRaceclass 	= raceclass01
		else:
			ERROR_MSG( "FeichengwuraoMgr: update raceclass fault! not finded the senderName(%s), index(%i)!" % roleName01, index )
			return
		
		self.fcwrDB.updateLoveMsgRaceClassInfoToDB( msgIns )


	def addVoteResult( self, resultIns ):
		"""
		define method
		"""
		self.resultDatas.append( resultIns )

		self.fcwrDB.addVoteResultToDB( resultIns )
		
		itemDatas = []
		for i in csconst.FCWR_REWARDS[resultIns.rewardReason]:
			item = g_items.createDynamicItem( i, 1 )
			if item is None:
				ERROR_MSG( "非诚勿扰奖励物品（id:%i）不存在（策划没有配置！）。"%i )
				continue
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]
			itemData = cPickle.dumps( tempDict, 0 )
			itemDatas.append( itemData )
			
		msg = ""
		if resultIns.rewardReason in REWARD_LOVE_MSG_CONFIG:
			msgIns = self.msgDatas[ int( resultIns.key ) ]
			msg = REWARD_LOVE_MSG_CONFIG[resultIns.rewardReason]%( resultIns.param01, msgIns.msg, int( resultIns.param02 )  )

		if resultIns.rewardReason in REWARD_VOTE_CONFIG:
			voteIns = self.voteDatas[ int( resultIns.key ) ]
			msg = REWARD_VOTE_CONFIG[resultIns.rewardReason]%( resultIns.param01, voteIns.getVoteCount() )

		if resultIns.rewardReason == csdefine.FCWR_VOTE_KAN_HAO:
			msgIns = self.msgDatas[ int( resultIns.key ) ]
			BigWorld.globalData["MailMgr"].send( None, msgIns.senderName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.FCWR_MAIL_REWARD_TITLE, msg, 0, itemDatas )
			BigWorld.globalData["MailMgr"].send( None, msgIns.receiverName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.FCWR_MAIL_REWARD_TITLE, msg, 0, itemDatas )
		else:
			BigWorld.globalData["MailMgr"].send( None, resultIns.param01, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.FCWR_MAIL_REWARD_TITLE, msg, 0, itemDatas )


	def voteLoveMsg( self, playerBase, roleDBID, roleName, index, chooseSubject ):
		"""
		define method
		"""
		if not index in self.msgDatas:
			return
		
		if roleDBID in self.voteDatas:
			if time.time() - self.voteDatas[roleDBID].voteTime < csconst.FCWR_VOTE_SPEED:
				if playerBase is not None:
					playerBase.client.onStatusMessage( csstatus.FCWR_VOTE_SPEED_HANDLE, "" )
				return
			if index in self.voteDatas[roleDBID].voteList:
				if playerBase is not None:
					playerBase.client.onStatusMessage( csstatus.FCWR_HAS_ALREADY_VOTE_BEFORE, "" )
				return
		else:
			voteIns = VoteInstance()
			voteIns.init( roleDBID, roleName, int( time.time() ) )
			self.voteDatas[roleDBID] = voteIns
		
		if self.msgDatas[index].vote( chooseSubject ):
			self.fcwrDB.updateLoveMsgVoteInfoToDB( self.msgDatas[index] )
			self.voteDatas[roleDBID].voteTime = int( time.time() )
			self.voteDatas[roleDBID].voteList.append( index )
			self.fcwrDB.updateVoteDataToDB( self.voteDatas[roleDBID] )
			if playerBase is not None:
				playerBase.client.onVoteLoveMsgSuccessful( self.msgDatas[index] )

	def onStart( self ):
		"""
		define method
		"""
		if BigWorld.globalData.has_key( "AS_Feichengwurao" ):
			curTime = time.localtime()
			ERROR_MSG( "非诚勿扰活动正在进行，%i点%i分试图再次开始非诚勿扰活动。"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "AS_Feichengwurao" ] = True

	def onEnd( self ):
		"""
		define method.
		"""
		if BigWorld.globalData.has_key( "AS_Feichengwurao" ):
			del BigWorld.globalData[ "AS_Feichengwurao" ]

	def onHandle_result( self ):
		"""
		define method
		"""
		if BigWorld.globalData.has_key( "AS_Feichengwurao" ):
			del BigWorld.globalData[ "AS_Feichengwurao" ]
		
		if len( self.resultDatas ) == 0:
			
			#---------------------计算告白获得的奖励-------------------------------
			#获得投票-总票-数目最多的告白，投票者获得“万众瞩目”称号
			#获得投票-看好-数目最多的告白，投票者获得“万众瞩目”称号
			#获得投票-遇到情敌-数目最多的告白，投票者获得“万众瞩目”称号
			#获得投票-失恋-数目最多的告白，投票者获得“万众瞩目”称号
			maxVoteCount 		= 0
			maxVoteLastTime 	= 0
			maxVoteIndex 		= -1
			
			maxVote1Count 		= 0
			maxVote1LastTime 	= 0
			maxVote1Index 		= -1
			
			maxVote2Count 		= 0
			maxVote2LastTime 	= 0
			maxVote2Index 		= -1
			
			maxVote3Count 		= 0
			maxVote3LastTime 	= 0
			maxVote3Index 		= -1
			
			for i, iMsgIns in self.msgDatas.iteritems():
				voteCount = iMsgIns.getVoteCount()
				if  voteCount > maxVoteCount:
					maxVoteCount 		= voteCount
					maxVoteLastTime		= iMsgIns.lastVoteTime
					maxVoteIndex		= iMsgIns.index
				if  voteCount == maxVoteCount:
					if maxVoteLastTime < iMsgIns.lastVoteTime:
						maxVoteCount 		= voteCount
						maxVoteLastTime		= iMsgIns.lastVoteTime
						maxVoteIndex		= iMsgIns.index
				
				if iMsgIns.vote_1 > maxVote1Count:
					maxVote1Count 		= iMsgIns.vote_1
					maxVote1LastTime 	= iMsgIns.lastVoteTime
					maxVote1Index 		= iMsgIns.index
				elif iMsgIns.vote_1 == maxVote1Count:
					if maxVote1LastTime < iMsgIns.lastVoteTime:
						maxVote1Count 		= iMsgIns.vote_1
						maxVote1LastTime 	= iMsgIns.lastVoteTime
						maxVote1Index 		= iMsgIns.index

				if iMsgIns.vote_2 > maxVote2Count:
					maxVote2Count 		= iMsgIns.vote_2
					maxVote2LastTime 	= iMsgIns.lastVoteTime
					maxVote2Index 		= iMsgIns.index
				elif iMsgIns.vote_2 == maxVote2Count:
					if maxVote2LastTime < iMsgIns.lastVoteTime:
						maxVote2Count 		= iMsgIns.vote_2
						maxVote2LastTime 	= iMsgIns.lastVoteTime
						maxVote2Index 		= iMsgIns.index

				if iMsgIns.vote_3 > maxVote3Count:
					maxVote3Count 		= iMsgIns.vote_3
					maxVote3LastTime 	= iMsgIns.lastVoteTime
					maxVote3Index 		= iMsgIns.index
				elif iMsgIns.vote_3 == maxVote3Count:
					if maxVote3LastTime < iMsgIns.lastVoteTime:
						maxVote3Count 		= iMsgIns.vote_3
						maxVote3LastTime 	= iMsgIns.lastVoteTime
						maxVote3Index 		= iMsgIns.index
			if maxVoteIndex != -1:
				msgIns = self.msgDatas[maxVoteIndex]
				resultIns = FcwrResult()
				resultIns.init( str( maxVoteIndex ), csdefine.FCWR_VOTE_ALL, 0, 0, str( msgIns.receiverName ), str(maxVoteCount) )
				self.addVoteResult( resultIns )
			if maxVote1Index != -1:
				msgIns = self.msgDatas[maxVote1Index]
				resultIns = FcwrResult()
				resultIns.init( str( maxVote1Index ), csdefine.FCWR_VOTE_KAN_HAO, 0, 0, str( msgIns.receiverName ), str(maxVote1Count) )
				self.addVoteResult( resultIns )
			
			if maxVote2Index != -1:
				msgIns = self.msgDatas[maxVote2Index]
				resultIns = FcwrResult()
				resultIns.init( str( maxVote2Index ), csdefine.FCWR_VOTE_QING_DI, 0, 0, str( msgIns.receiverName ), str(maxVote2Count) )
				self.addVoteResult( resultIns )

			if maxVote3Index != -1:
				msgIns = self.msgDatas[maxVote3Index]
				resultIns = FcwrResult()
				resultIns.init( str( maxVote3Index ), csdefine.FCWR_VOTE_SHI_LIAN, 0, 0, str( msgIns.senderName ), str(maxVote3Count) )
				self.addVoteResult( resultIns )
			
			#---------------------计算投票获得的奖励-------------------------------
			#投票数目第一名，获得“羡慕嫉妒恨”称号，获得150元宝
			#投票数目第二名，获得100元宝
			#投票数目第三名，获得50元宝
			
			vote_1_count 	= 0
			vote_1_roleDBID = -1
			
			vote_2_count 	= 0
			vote_2_roleDBID = -1
			
			vote_3_count 	= 0
			vote_3_roleDBID = -1
			
			for iDBID,iValue in self.voteDatas.iteritems():
				count = iValue.getVoteCount()
				
				if count > vote_1_count:
					vote_3_count 	= vote_2_count
					vote_3_roleDBID = vote_2_roleDBID
					
					vote_2_count 	= vote_1_count
					vote_2_roleDBID = vote_1_roleDBID
				
					vote_1_count 	= count
					vote_1_roleDBID = iDBID
				elif count > vote_2_count:
					vote_3_count 	= vote_2_count
					vote_3_roleDBID = vote_2_roleDBID
				
					vote_2_count 	= count
					vote_2_roleDBID = iDBID
				elif count > vote_3_count:
					vote_3_count 	= count
					vote_3_roleDBID = iDBID
			
			if vote_1_roleDBID != -1:
				voteIns = self.voteDatas[vote_1_roleDBID]
				resultIns = FcwrResult()
				resultIns.init( str( vote_1_roleDBID ), csdefine.FCWR_MAX_COUNT_VOTER_1, 0, 0, voteIns.roleName )
				self.addVoteResult( resultIns )

			if vote_2_roleDBID != -1:
				voteIns = self.voteDatas[vote_2_roleDBID]
				resultIns = FcwrResult()
				resultIns.init( str( vote_2_roleDBID ), csdefine.FCWR_MAX_COUNT_VOTER_2, 0, 0, voteIns.roleName )
				self.addVoteResult( resultIns )

			if vote_3_roleDBID != -1:
				voteIns = self.voteDatas[vote_3_roleDBID]
				resultIns = FcwrResult()
				resultIns.init( str( vote_3_roleDBID ), csdefine.FCWR_MAX_COUNT_VOTER_3, 0, 0, voteIns.roleName )
				self.addVoteResult( resultIns )

	def cleanAllDatas( self ):
		"""
		define method
		"""
		self.msgDatas 			= {}
		self.resultDatas 		= []
		self.voteDatas			= {}
		self.senderMsgGroup 	= {}
		self.receiverMsgGroup 	= {}
		self.resultDess			= {}

		self.fcwrDB.cleanAllDatasInDB()
	
	def queryLoveMsgsResult( self, playerBase ):
		"""
		define method
		"""
		if len( self.resultDess ) == 0:
			self._makeResultDes()
		playerBase.client.receiveLoveMsgsResult( self.resultDess )
	
	
	def _makeResultDes( self ):
		"""
		"""
		for iResult in self.resultDatas:
			if iResult.rewardReason in REWARD_LOVE_MSG_CONFIG:
				msgIns = self.msgDatas[ int( iResult.key ) ]
				self.resultDess[iResult.rewardReason] = REWARD_LOVE_MSG_CONFIG[iResult.rewardReason]%( iResult.param01, msgIns.msg, int( iResult.param02 )  )
		
			if iResult.rewardReason in REWARD_VOTE_CONFIG:
				voteIns = self.voteDatas[ int( iResult.key ) ]
				self.resultDess[iResult.rewardReason] = REWARD_VOTE_CONFIG[iResult.rewardReason]%( iResult.param01, voteIns.getVoteCount() )
		

import random

class testClass:
	"""
	"""
	def __init__( self ):
		BigWorld.globalData[ "AS_Feichengwurao" ] = True
		self.fm = BigWorld.entities[BigWorld.globalData["FeichengwuraoMgr"].id]
		self.playersInfos = []
		query = "select id, sm_playerName from tbl_Role"
		BigWorld.executeRawDatabaseCommand( query, self.__onLoadPlayerNames )

	def __onLoadPlayerNames( self, result, rows, errstr ):
		"""
		"""
		for i in result:
			self.playersInfos.append( ( int(i[0]), i[1] ) )
		print "玩家名字数量：", len( result )


	def addMsgs( self, count ):
		"""
		增加告白数量
		"""
		for i in xrange( 0, count ):
			msgIns = LoveMsg()
			senderInfo = random.choice( self.playersInfos )
			receiverInfo = random.choice( self.playersInfos )
			if senderInfo == receiverInfo:
				return
			msgIns.init( 0, senderInfo[0], int(time.time()) + random.randint( 0, 10000 ), senderInfo[1], receiverInfo[1], "i love you%i"%i, random.randint(0,1) )
			BigWorld.globalData["FeichengwuraoMgr"].addLoveMsg( msgIns )

	def voteMsgs( self, count ):
		"""
		投票数量
		"""
		for i in xrange( 0 , count ):
			playerInfo = random.choice(self.playersInfos)
			if playerInfo[0] in self.fm.voteDatas:
				self.fm.voteDatas[playerInfo[0]].voteTime = 0
			self.fm.voteLoveMsg( None, playerInfo[0], playerInfo[1], random.choice( self.fm.msgDatas.keys() ), random.randint(1, 6) )
	
	
	def handleResult( self ):
		"""
		"""
		BigWorld.globalData["FeichengwuraoMgr"].onHandle_result()
	
	
	def printResultData( self ):
		"""
		"""
		for i in self.fm.resultDatas:
			print "活动结果数据"
			print self.key
			print self.roleDBID
			print self.roleName
			print self.rewardReason
			print self.takenTime
			print self.hasTaken
			print self.param
	
	def printResultDes( self ):
		"""
		"""
		if len( self.fm.resultDess ) == 0:
			self.fm._makeResultDes()

		for i in self.fm.resultDess.values():
			print i
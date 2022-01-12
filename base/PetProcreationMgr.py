# -*- coding: gb18030 -*-


import BigWorld
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
from PetFormulas import formulas
import time
import csstatus
import csconst
import csdefine
from Function import Functor
from MsgLogger import g_logger

class PetProcreationMgr( BigWorld.Base ):
	"""
	宠物繁殖管理器
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )

		self.tempProcreationData = {}	# { playerDBID1:( ( playerDBID1, petDBID1 ), ( playerDBID2, petDBID2 ) ) }
		self.tempProRecords = {}	# {petDBID:{petData},...}
		# 玩家繁殖数据{ playerDBID : { ( playerDBID1, playerDBID2 ) : [ 玩家dbid1, 玩家名字1, 玩家宠物dbid1, 玩家dbid2, 玩家名字2, 玩家宠物dbid2, 繁殖状态 ] }, ... }
		# 约定：playerDBID1 < playerDBID2
		self.petProcreationDict = {}

		self.registerGlobally( "PetProcreationMgr", self._registerGloballyCB )
		self.createDatabaseTable()

	def _registerGloballyCB( self, succeeded ):
		"""
		把自身注册全局变量
		"""
		if not succeeded:
			self.registerGlobally( "PetProcreationMgr", self._registerGloballyCB )
		else:
			BigWorld.globalData["PetProcreationMgr"] = self

	def createDatabaseTable( self ):
		"""
		创建数据库表

		sm_playerDBID1 : 申请繁殖玩家的dbid1
		sm_playerDBID2 : 申请繁殖玩家的dbid2
		sm_petDBID1 : 参与繁殖的宠物dbid
		sm_petDBID2 : 参与繁殖的宠物dbid
		sm_endTime : 繁殖结束时间,INT32
		"""
		sqlSentence = """
			CREATE TABLE IF NOT EXISTS `custom_PetProcreation`
			( `id` BIGINT NOT NULL auto_increment,
			`sm_playerDBID1` BIGINT NOT NULL,
			`sm_playerName1` TEXT NOT NULL,
			`sm_petDBID1` BIGINT NOT NULL,
			`sm_playerDBID2` BIGINT NOT NULL,
			`sm_playerName2`TEXT NOT NULL,
			`sm_petDBID2` BIGINT NOT NULL,
			`sm_endTime` INT( 32 ) NOT NULL,
			PRIMARY KEY ( `id` )
			)
			ENGINE = InnoDB;
			"""
		BigWorld.executeRawDatabaseCommand( sqlSentence, self._createDatabaseTableCB )

	def _createDatabaseTableCB( self, result, rows, errstr ):
		"""
		创建宠物繁殖信息表的回调
		"""
		if errstr:
			ERROR_MSG( errstr )
			return

		self.initialize()		# 初始化

	def addProcreationRecord( self, petInfo ):
		"""
		增加一条繁殖记录
		@param petInfo : [ playerDBID1, playerName1, petDBID1, playerDBID2, playerName2, petDBID2, endTime ]
			playerDBID1 : 申请繁殖的玩家dbid1
			playerName1 : 申请繁殖的玩家名字1
			petDBID1 : 参与繁殖的宠物dbid1
			playerDBID2 : 申请繁殖的玩家dbid2
			playerName2 : 申请繁殖玩家的名字2
			petDBID2 : 参与繁殖的宠物dbid2
			endTime : 繁殖结束时间,INT32
		"""
		sqlSentence = "insert into `custom_PetProcreation` ( sm_playerDBID1, sm_playerName1, sm_petDBID1, sm_playerDBID2, sm_playerName2, sm_petDBID2, sm_endTime ) value ( %i, \'%s\', %i, %i, \'%s\', %i, %i )" \
			% ( petInfo[0], petInfo[1], petInfo[2], petInfo[3], petInfo[4], petInfo[5], petInfo[6] )
		BigWorld.executeRawDatabaseCommand( sqlSentence, Functor( self.addProcreationRecordCB, petInfo ) )

	def addProcreationRecordCB( self, petInfo, result, rows, errstr ):
		"""
		往db增加繁殖记录的回调
		"""
		if errstr:
			ERROR_MSG( errstr )
			return
		# 制作宠物繁殖的写入数据库日志
		petDBID1 = petInfo[2]
		petDBID2 = petInfo[5]
		if (not petDBID1 in self.tempProRecords) or (not petDBID2 in self.tempProRecords):
			ERROR_MSG( "pet procreation log failed, because pet(%d) or pet(%d) temp data record not found."%( petDBID1, petDBID2 ) )
			return
		playerNameAndID1 = "%s(%d)"%(petInfo[1], petInfo[0])
		playerNameAndID2 = "%s(%d)"%(petInfo[4], petInfo[3])
		petData1 = self.tempProRecords.pop(petDBID1)
		petData2 = self.tempProRecords.pop(petDBID2)
		try:
			g_logger.petBreedLog( petInfo[0], petData1, petInfo[3], petData2 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def delProcreationRecord( self, playerDBID1, playerDBID2 ):
		"""
		删除繁殖记录
		"""
		# 目前一个玩家只能产生一条繁殖记录
		sqlSentence = "delete from `custom_PetProcreation` where sm_playerDBID1 = %i or sm_playerDBID2 = %i" % ( playerDBID1, playerDBID1 )
		BigWorld.executeRawDatabaseCommand( sqlSentence, self.delProcreationRecordCB )

	def delProcreationRecordCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( errstr )

	def initialize( self ):
		"""
		初始化
		"""
		BigWorld.executeRawDatabaseCommand( "select * from `custom_PetProcreation`", self.initializeCB )

	def initializeCB( self, result, rows, errstr ):
		"""
		初始化回调
		"""
		if errstr:
			ERROR_MSG( errstr )
			return

		for record in result:
			playerDBID1 = int( record[1] )
			playerDBID2 = int( record[4] )
			petInfo = [ playerDBID1, record[2], int( record[3] ), playerDBID2, record[5], int( record[6] ), int( record[7] ) ]
			procreationKey = ( playerDBID1, playerDBID2 )
			if playerDBID1 > playerDBID2:
				procreationKey = ( playerDBID2, playerDBID1 )
			self.petProcreationDict[playerDBID1] = { procreationKey:petInfo }
			self.petProcreationDict[playerDBID2] = { procreationKey:petInfo }

	def procreatePet( self, playerDBID1, playerName1, playerDBID2, petDBID, endTime ):
		"""
		Define method.
		玩家提交繁殖宠物。
		两个玩家分别提交，需等后者提交的数据到达才能把繁殖数据写入数据库。
		不考虑一个玩家提交成功而另外一个玩家提交出现异常的问题，以后可增加一个纠错timer，
		每隔一定时间检测一下tempProcreationData数据，若发现仅有一个玩家提交成功情况则进行纠错处理，把宠物还给相关玩家。

		@param playerDBID1 : 申请繁殖的玩家dbid
		@param playerDBID2 : 申请繁殖的玩家dbid
		@param petDBID : 参与繁殖的宠物dbid
		@param endTime : 繁殖结束时间,INT32
		"""
		petInfoKey = ( playerDBID1, playerDBID2 )
		if playerDBID1 > playerDBID2:
			petInfoKey = ( playerDBID2, playerDBID1 )

		if petInfoKey in self.tempProcreationData:
			petInfo = self.tempProcreationData[petInfoKey]
			# [ 玩家dbid1, 玩家名字1, 玩家宠物dbid1, 玩家dbid2, 玩家名字2, 玩家宠物dbid2, 繁殖状态 ]
			petInfo = [ playerDBID2, petInfo[1], petInfo[2], playerDBID1, playerName1, petDBID, petInfo[3] ]
			del self.tempProcreationData[petInfoKey]
			self.petProcreationDict[playerDBID2] = { petInfoKey:petInfo }
			self.petProcreationDict[playerDBID1] = { petInfoKey:petInfo }
			self.addProcreationRecord( petInfo )
		else:
			self.tempProcreationData[petInfoKey] = [ playerDBID1, playerName1, petDBID, endTime ]
			
	def procreatePetRecord( self, petDBID, petDataStr ):
		"""
		Define method.
		宠物繁殖日志数据记录 by 姜毅
		"""
		self.tempProRecords[petDBID] = petDataStr

	def requestProcreatedPet( self, playerDBID1, playerDBID2, playerBase1, playerBase2 ):
		"""
		Define method.
		玩家组队领取宠物。
		必须保证双方玩家都能正确领取宠物，那么需要保证在玩家加入宠物数据之前不被销毁。
		若条件合格，须将繁殖的宠物数据发给申请者的cell，在cell检测申请者和其队友是否还符合条件，
		其一个重要的检测是，队友entity是否isDestroyed，条件合法的话，通知双方加入繁殖宠物数据，
		通知管理器去除繁殖数据。

		@param playerDBID1 : 申请领取的玩家dbid
		@param playerDBID2 : 申请领取的玩家dbid
		@param playerBase1 : 申请领取宠物的玩家base mailbox
		@param playerBase2 : 申请领取宠物的玩家base mailbox
		"""
		if not self.petProcreationDict.has_key( playerDBID1 ):
			playerBase1.client.onStatusMessage( csstatus.PET_PROCREATE_GET_NOT_EXIST, "" )
			playerBase2.client.onStatusMessage( csstatus.PET_PROCREATE_GET_NOT_EXIST, "" )
			return
		try:
			petInfoKey = ( playerDBID1, playerDBID2 )
			if playerDBID1 > playerDBID2:
				petInfoKey = ( playerDBID2, playerDBID1 )
			petInfo = self.petProcreationDict[playerDBID1][petInfoKey]
		except KeyError:
			playerBase1.client.onStatusMessage( csstatus.PET_PROCREATE_NOT_OWNER, "" )
			playerBase2.client.onStatusMessage( csstatus.PET_PROCREATE_NOT_OWNER, "" )
			ERROR_MSG( "pet miss? player:%i and player:%i." % ( playerDBID1, playerDBID2 ) )
			return

		if petInfo[0] == playerDBID1:
			petDBID1 = petInfo[2]
			petDBID2 = petInfo[5]
			targetDBID = petInfo[3]
		else:
			petDBID1 = petInfo[5]
			petDBID2 = petInfo[2]
			targetDBID = petInfo[0]

		now = time.time()
		endTime = petInfo[6]
		if now < endTime:
			playerBase1.client.onStatusMessage( csstatus.PET_PROCREATE_NOT_READY, "" )
			playerBase2.client.onStatusMessage( csstatus.PET_PROCREATE_NOT_READY, "" )
			return
		elif now - csconst.PET_PROCREATE_OVERDUE_TIME > endTime:	# 超过48小时没领取，宠物已经被放生
			INFO_MSG( "玩家( playerDBID1:%i, playerDBID2:%i )宠物繁殖完毕超时没领取，丢弃参与繁殖的宠物( petDBID1:%i, petDBID2:%i)。" % ( playerDBID1, playerDBID2, petDBID1, petDBID2 ) )
			self.abandonProcreatePet( petDBID1, petDBID2 )
			playerBase1.client.onStatusMessage( csstatus.PET_PROCREATE_GET_OVERDUE, "" )
			playerBase2.client.onStatusMessage( csstatus.PET_PROCREATE_GET_OVERDUE, "" )
			playerBase1.cell.removeProcreatingFlag()
			playerBase2.cell.removeProcreatingFlag()
			playerBase1.cell.pft_procreatePetFailed( targetDBID, petDBID1, petDBID2 )
			return

		playerBase1.cell.pft_obtainProcreatedPet( targetDBID, petDBID1, petDBID2 )

	def abandonProcreatePet( self, dbid1, dbid2 ) :
		"""
		繁殖完毕超时没领取，丢弃参与繁殖的宠物
		"""
		def onAbandonPet( count, dbid, success ):
			if success :
				pass
			elif count < 2 :
				BigWorld.deleteBaseByDBID( "Pet", dbid, Functor( onAbandonPet, count + 1, dbid ) )
			else :
				ERROR_MSG( "abandon pet %i fail!" % dbid )

		BigWorld.deleteBaseByDBID( "Pet", dbid1, Functor( onAbandonPet, 0, dbid1 ) )
		BigWorld.deleteBaseByDBID( "Pet", dbid2, Functor( onAbandonPet, 0, dbid2 ) )

	def obtainPetSuccess( self, playerDBID1, playerDBID2 ):
		"""
		Define method.
		玩家领取宠物成功的通知，删除繁殖数据

		@param playerDBID1 : 申请领取的玩家dbid
		@param playerDBID2 : 申请领取的玩家dbid
		"""
		self.removePetInfo( playerDBID1, playerDBID2 )

	def removePetInfo( self, playerDBID1, playerDBID2 ):
		"""
		删除对应的宠物繁殖数据
		"""
		petInfoKey = ( playerDBID1, playerDBID2 )
		if playerDBID1 > playerDBID2:
			petInfoKey = ( playerDBID2, playerDBID1 )
		self.delProcreationRecord( playerDBID1, playerDBID2 )
		del self.petProcreationDict[playerDBID1]
		del self.petProcreationDict[playerDBID2]

	def onPlayerGetCell( self, playerDBID, playerBase ):
		"""
		Define method.
		玩家登陆查询是否有宠物繁殖
		"""
		if self.petProcreationDict.has_key( playerDBID ):
			now = time.time()
			for key, value in self.petProcreationDict[playerDBID].iteritems():
				dstPlayerDBID = key[0] == playerDBID and key[1] or key[0]
				playerBase.client.pft_receivePetProcreationInfo( dstPlayerDBID, value[6] )
				playerBase.cell.pft_setProcreating()

	def updateProcreateState( self, playerDBID1, playerDBID2, playerBase ):
		"""
		Define method.
		请求更新宠物繁殖状态

		@param playerDBID1 : 繁殖玩家dbid
		@param playerDBID2 : 繁殖玩家dbid
		@param playerBase : 请求更新玩家的base mailbox
		"""
		tupleKey = ( playerDBID1, playerDBID2 )
		if playerDBID1 > playerDBID2:
			tupleKey = ( playerDBID2, playerDBID1 )
		try:
			petInfo = self.petProcreationDict[playerDBID1][tupleKey]
		except KeyError:
			DEBUG_MSG( "cannot find pet infomation,playerDBID1( %i ), playerDBID2( %i )." % ( playerDBID1, playerDBID2 ) )
			return
		now = time.time()
		endTime = petInfo[6]
		if now - csconst.PET_PROCREATE_OVERDUE_TIME > endTime:	# 必须清除数据，否则玩家不能再申请繁殖宠物
			self.removePetInfo( playerDBID1, playerDBID2 )
			playerBase.cell.removeProcreatingFlag()
			return
		if now > endTime:
			title = cschannel_msgs.PETPROCREATIONMGR_VOICE_1
			content = cschannel_msgs.PETPROCREATIONMGR_VOICE_2
			senderName = cschannel_msgs.FAMILY_INFO_2
			mailManager = BigWorld.globalData["MailMgr"]
			mailManager.send( None, petInfo[4], csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, senderName, title, content, 0, [] )
			mailManager.send( None, petInfo[1], csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, senderName, title, content, 0, [] )

	def setProcreated( self, playerDBID ):
		"""
		Define method.
		直接设置dbid为playerDBID的玩家的相关繁殖完成，提供给GM使用的调试方法
		"""
		try:
			petInfos = self.petProcreationDict[playerDBID]
		except KeyError:
			DEBUG_MSG( "cannot find pet infomation,playerDBID( %i )" % playerDBID )
			return
		for petInfo in petInfos.itervalues():
			petInfo[6] = time.time() - 1
			self.updateProcreateState( petInfo[0], petInfo[3], None )
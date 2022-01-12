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
	���ﷱֳ������
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )

		self.tempProcreationData = {}	# { playerDBID1:( ( playerDBID1, petDBID1 ), ( playerDBID2, petDBID2 ) ) }
		self.tempProRecords = {}	# {petDBID:{petData},...}
		# ��ҷ�ֳ����{ playerDBID : { ( playerDBID1, playerDBID2 ) : [ ���dbid1, �������1, ��ҳ���dbid1, ���dbid2, �������2, ��ҳ���dbid2, ��ֳ״̬ ] }, ... }
		# Լ����playerDBID1 < playerDBID2
		self.petProcreationDict = {}

		self.registerGlobally( "PetProcreationMgr", self._registerGloballyCB )
		self.createDatabaseTable()

	def _registerGloballyCB( self, succeeded ):
		"""
		������ע��ȫ�ֱ���
		"""
		if not succeeded:
			self.registerGlobally( "PetProcreationMgr", self._registerGloballyCB )
		else:
			BigWorld.globalData["PetProcreationMgr"] = self

	def createDatabaseTable( self ):
		"""
		�������ݿ��

		sm_playerDBID1 : ���뷱ֳ��ҵ�dbid1
		sm_playerDBID2 : ���뷱ֳ��ҵ�dbid2
		sm_petDBID1 : ���뷱ֳ�ĳ���dbid
		sm_petDBID2 : ���뷱ֳ�ĳ���dbid
		sm_endTime : ��ֳ����ʱ��,INT32
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
		�������ﷱֳ��Ϣ��Ļص�
		"""
		if errstr:
			ERROR_MSG( errstr )
			return

		self.initialize()		# ��ʼ��

	def addProcreationRecord( self, petInfo ):
		"""
		����һ����ֳ��¼
		@param petInfo : [ playerDBID1, playerName1, petDBID1, playerDBID2, playerName2, petDBID2, endTime ]
			playerDBID1 : ���뷱ֳ�����dbid1
			playerName1 : ���뷱ֳ���������1
			petDBID1 : ���뷱ֳ�ĳ���dbid1
			playerDBID2 : ���뷱ֳ�����dbid2
			playerName2 : ���뷱ֳ��ҵ�����2
			petDBID2 : ���뷱ֳ�ĳ���dbid2
			endTime : ��ֳ����ʱ��,INT32
		"""
		sqlSentence = "insert into `custom_PetProcreation` ( sm_playerDBID1, sm_playerName1, sm_petDBID1, sm_playerDBID2, sm_playerName2, sm_petDBID2, sm_endTime ) value ( %i, \'%s\', %i, %i, \'%s\', %i, %i )" \
			% ( petInfo[0], petInfo[1], petInfo[2], petInfo[3], petInfo[4], petInfo[5], petInfo[6] )
		BigWorld.executeRawDatabaseCommand( sqlSentence, Functor( self.addProcreationRecordCB, petInfo ) )

	def addProcreationRecordCB( self, petInfo, result, rows, errstr ):
		"""
		��db���ӷ�ֳ��¼�Ļص�
		"""
		if errstr:
			ERROR_MSG( errstr )
			return
		# �������ﷱֳ��д�����ݿ���־
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
		ɾ����ֳ��¼
		"""
		# Ŀǰһ�����ֻ�ܲ���һ����ֳ��¼
		sqlSentence = "delete from `custom_PetProcreation` where sm_playerDBID1 = %i or sm_playerDBID2 = %i" % ( playerDBID1, playerDBID1 )
		BigWorld.executeRawDatabaseCommand( sqlSentence, self.delProcreationRecordCB )

	def delProcreationRecordCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( errstr )

	def initialize( self ):
		"""
		��ʼ��
		"""
		BigWorld.executeRawDatabaseCommand( "select * from `custom_PetProcreation`", self.initializeCB )

	def initializeCB( self, result, rows, errstr ):
		"""
		��ʼ���ص�
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
		����ύ��ֳ���
		������ҷֱ��ύ����Ⱥ����ύ�����ݵ�����ܰѷ�ֳ����д�����ݿ⡣
		������һ������ύ�ɹ�������һ������ύ�����쳣�����⣬�Ժ������һ������timer��
		ÿ��һ��ʱ����һ��tempProcreationData���ݣ������ֽ���һ������ύ�ɹ��������о������ѳ��ﻹ�������ҡ�

		@param playerDBID1 : ���뷱ֳ�����dbid
		@param playerDBID2 : ���뷱ֳ�����dbid
		@param petDBID : ���뷱ֳ�ĳ���dbid
		@param endTime : ��ֳ����ʱ��,INT32
		"""
		petInfoKey = ( playerDBID1, playerDBID2 )
		if playerDBID1 > playerDBID2:
			petInfoKey = ( playerDBID2, playerDBID1 )

		if petInfoKey in self.tempProcreationData:
			petInfo = self.tempProcreationData[petInfoKey]
			# [ ���dbid1, �������1, ��ҳ���dbid1, ���dbid2, �������2, ��ҳ���dbid2, ��ֳ״̬ ]
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
		���ﷱֳ��־���ݼ�¼ by ����
		"""
		self.tempProRecords[petDBID] = petDataStr

	def requestProcreatedPet( self, playerDBID1, playerDBID2, playerBase1, playerBase2 ):
		"""
		Define method.
		��������ȡ���
		���뱣֤˫����Ҷ�����ȷ��ȡ�����ô��Ҫ��֤����Ҽ����������֮ǰ�������١�
		�������ϸ��뽫��ֳ�ĳ������ݷ��������ߵ�cell����cell��������ߺ�������Ƿ񻹷���������
		��һ����Ҫ�ļ���ǣ�����entity�Ƿ�isDestroyed�������Ϸ��Ļ���֪ͨ˫�����뷱ֳ�������ݣ�
		֪ͨ������ȥ����ֳ���ݡ�

		@param playerDBID1 : ������ȡ�����dbid
		@param playerDBID2 : ������ȡ�����dbid
		@param playerBase1 : ������ȡ��������base mailbox
		@param playerBase2 : ������ȡ��������base mailbox
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
		elif now - csconst.PET_PROCREATE_OVERDUE_TIME > endTime:	# ����48Сʱû��ȡ�������Ѿ�������
			INFO_MSG( "���( playerDBID1:%i, playerDBID2:%i )���ﷱֳ��ϳ�ʱû��ȡ���������뷱ֳ�ĳ���( petDBID1:%i, petDBID2:%i)��" % ( playerDBID1, playerDBID2, petDBID1, petDBID2 ) )
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
		��ֳ��ϳ�ʱû��ȡ���������뷱ֳ�ĳ���
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
		�����ȡ����ɹ���֪ͨ��ɾ����ֳ����

		@param playerDBID1 : ������ȡ�����dbid
		@param playerDBID2 : ������ȡ�����dbid
		"""
		self.removePetInfo( playerDBID1, playerDBID2 )

	def removePetInfo( self, playerDBID1, playerDBID2 ):
		"""
		ɾ����Ӧ�ĳ��ﷱֳ����
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
		��ҵ�½��ѯ�Ƿ��г��ﷱֳ
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
		������³��ﷱֳ״̬

		@param playerDBID1 : ��ֳ���dbid
		@param playerDBID2 : ��ֳ���dbid
		@param playerBase : ���������ҵ�base mailbox
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
		if now - csconst.PET_PROCREATE_OVERDUE_TIME > endTime:	# ����������ݣ�������Ҳ��������뷱ֳ����
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
		ֱ������dbidΪplayerDBID����ҵ���ط�ֳ��ɣ��ṩ��GMʹ�õĵ��Է���
		"""
		try:
			petInfos = self.petProcreationDict[playerDBID]
		except KeyError:
			DEBUG_MSG( "cannot find pet infomation,playerDBID( %i )" % playerDBID )
			return
		for petInfo in petInfos.itervalues():
			petInfo[6] = time.time() - 1
			self.updateProcreateState( petInfo[0], petInfo[3], None )
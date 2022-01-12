# -*- coding: gb18030 -*-


import BigWorld
import time
import csdefine
import csstatus
from bwdebug import *
from Function import Functor
"""
ר�Ŵ���һЩ�������µ���Ϸ��Ϊ��
�����������Ӧ��һ�����ݱ��������������ִ��ĳЩ�������жϡ�
"""

PROCESSING_TIME		= 2					#����������ʱ�䣨��λ���룩

class MessyMgr( BigWorld.Base ):
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "MessyMgr", self._onRegisterManager )
		self.createTable()
		#self.load()

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register MessyMgr Fail!" )
			# again
			self.registerGlobally( "MessyMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["MessyMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("MessyMgr Create Complete!")


	def createTable( self ):
		"""
		"""
		query = """CREATE TABLE IF NOT EXISTS `custom_MessyTable` (
				`id`					BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID` 			BIGINT(10),
				`sm_accountDBID` 		BIGINT(10),
				`sm_messyID` 			BIGINT(10),
				`sm_time` 				timestamp NOT NULL default '0000-00-00 00:00:00',
				`sm_param1`		 		VARCHAR(255),
				`sm_param2`				VARCHAR(255),
				`sm_param3`				VARCHAR(255),
				KEY `sm_roleDBID` (`sm_roleDBID`),
				UNIQUE KEY `uKey` (`sm_roleDBID`,`sm_messyID`),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

	def __createTableCB( self, result, rows, errstr ):
		"""
		�������ݿ���ص�����

		param tableName:	���ɵı������
		type tableName:		STRING
		"""
		if errstr:
			ERROR_MSG( "Create custom_MessyTable fault! %s"%errstr  )
			return

	def requestRoleMessyInfo( self, roleDBID, accountDBID ):
		"""
		define method
		"""
		for i in MESSYS:
			if MESSYS[i].isRoleInit( roleDBID ):
				return
		
		query = "select sm_messyID, sm_roleDBID, sm_accountDBID, sm_param1, sm_param2, sm_param3 from custom_MessyTable where sm_accountDBID = %i"%accountDBID
		BigWorld.executeRawDatabaseCommand( query, self.__onRequestRoleMessyInfo )
		INFO_MSG( "Request role(DBID:%i) messy info!" % roleDBID )
	
	def __onRequestRoleMessyInfo( self, result, rows, errstr ):
		"""
		"""
		if result is None:
			return
		for i in result:
			messyID = int( i[0] )
			if messyID in MESSYS:
				MESSYS[messyID].load( int(i[1]), int(i[2]), i[3], i[4], i[5] )
				INFO_MSG( "Init role(DBID:%i) messy info!" % int(i[1]) )
		
	def writeDB( self, messyID, roleDBID, accountDBID, param1, param2, param3 ):
		"""
		"""
		query = "REPLACE INTO custom_MessyTable(sm_roleDBID, sm_accountDBID, sm_messyID, sm_time, sm_param1, sm_param2, sm_param3) VALUES"
		BigWorld.executeRawDatabaseCommand( query + str( "(%i, %i, %i, now(), '%s','%s','%s')"%( roleDBID, accountDBID, messyID, param1, param2, param3 ) ), Functor( self.__onWriteDB, roleDBID, messyID, param1, param2, param3 ) )

	def __onWriteDB( self, roleDBID, messyID, param1, param2, param3, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "Write info(%i, %i,'%s','%s','%s') to custom_MessyTable fault!"%( roleDBID, messyID, param1, param2, param3 ) )
			return
	
	def do( self, messyID, roleDBID, accountDBID, roleMB, params ):
		"""
		define method
		ִ��һ����Ϊ��������ÿ����ȡ��Ԫ����
		"""
		MESSYS[messyID].do( self, roleDBID, accountDBID, roleMB, params )


	def onMessyFailed( self, messyID, roleDBID ):
		"""
		define method
		ִ��ĳ����Ϊ����ʧ�ܡ����ʧ��������Զ�̵��á�
		���磺 Ҫ�����һ����Ʒ������ұ������ˣ���ô�����cell�Ǳߣ��Ϳ���ͨ�����������������Ϊʧ�ܡ�
		"""
		MESSYS[messyID].onFailed( self, roleDBID )


	def onMessyOver( self, messyID, roleDBID ):
		"""
		define method
		ִ��һ����Ϊ��ɡ��ⲿ���������������֪��Ϊִ��������
		"""
		MESSYS[messyID].onOver( self, roleDBID )


class Messy:
	def __init__( self ):
		"""
		"""
		self.datas = {}
		self.messyID = -1
		self.processings = {}
	
	def load( self, dbid, accountDBID, param1, param2, param3 ):
		"""
		"""
		self.datas[dbid] = { "accountDBID": accountDBID, "param1" : param1, "param2" : param2, "param3" : param3 }

	def add( self, mgr, roleDBID, accountDBID, param1 = "", param2 = "", param3 = "" ):
		"""
		"""
		self.datas[roleDBID] = { "accountDBID" : accountDBID, "param1" : param1, "param2" : param2, "param3" : param3 }
		mgr.writeDB( self.messyID, roleDBID, accountDBID, param1, param2, param3 )

	def isRoleInit( self, roleDBID ):
		"""
		"""
		return roleDBID in self.datas

	def do( self, mgr, roleDBID, accountDBID, roleMB, params ):
		"""
		ִ��һ����Ϊ�����̡�
		1�� ͨ���ж�������һЩ�����ֶΣ����ٵ������ִ����Ϊ�ķ��������Ե�һ���������ٶȡ�
		
		2�� ��Ϊִ�������ж����Ϳ�ִ�У�����ִ����ش���
		
		"""
		if roleDBID in self.processings:
			if time.time() - self.processings[roleDBID]["time"] < PROCESSING_TIME:
				return
		
		self.processings[roleDBID] = { "time" : time.time(), "dbid" : roleDBID, "accountDBID" : accountDBID,"mgr" : mgr, "mailbox" : roleMB, "params" : params }
		
		if self.query( roleDBID, accountDBID, params ):
			self.onDo( mgr, roleDBID, roleMB, params )
		else:
			self.onStop( roleDBID, roleMB, params )
	
	def onDo( self, mgr, roleDBID, roleMB, params ):
		"""
		�����ȷִ�д���
		"""
		pass
	
	def query( self, roleDBID, accountDBID, params ):
		"""
		��Ϊ���������ж���
		"""
		return True

	def onStop( self, roleDBID, roleMB, params ):
		"""
		��Ϊ����ִ�д���
		"""
		self.removeProcessinger( roleDBID )
	
	def onOver( self, mgr, roleDBID ):
		"""
		��Ϊ������ϡ�
		"""
		self.removeProcessinger( roleDBID )

	def onFailed( self, mgr, roleDBID ):
		"""
		��Ϊ����ʧ�ܡ�
		"""
		self.removeProcessinger( roleDBID )

	def removeProcessinger( self, roleDBID ):
		"""
		�Ƴ�һ�����ڴ����ߡ�
		"""
		if roleDBID in self.processings:
			del self.processings[roleDBID]


class SilverTake( Messy ):
	"""
	"""
	silverCount = 200
	def __init__( self ):
		"""
		"""
		Messy.__init__( self )
		self.messyID = csdefine.MESSY_JOB_TAKE_SILVER
	
	def query( self, roleDBID, accountDBID, params ):
		"""
		"""
		if roleDBID in self.datas:
			tupleTime = time.localtime()
			if self.datas[roleDBID]["param1"] == str( tupleTime[0] ) + "-" + str( tupleTime[1] ) + "-" + str( tupleTime[2] ):
				return False
		else:
			for iValue in self.datas.values():
				if iValue["accountDBID"] == accountDBID:
					tupleTime = time.localtime()
					if iValue["param1"] == str( tupleTime[0] ) + "-" + str( tupleTime[1] ) + "-" + str( tupleTime[2] ):
						return False
		return True

	def onDo( self, mgr, roleDBID, roleMB, params ):
		"""
		"""
		roleMB.remoteCall( "addSilver", ( self.silverCount, csdefine.CHANGE_SILVER_MESSY_TAKE ) )
		roleMB.remoteCall( "onMessyRecall", (csdefine.MESSY_JOB_TAKE_SILVER, ))


	def onStop( self, roleDBID, roleMB, params ):
		"""
		"""
		roleMB.client.onStatusMessage( csstatus.MESSY_TAKE_SILVER, "" )
		Messy.onStop( self, roleDBID, roleMB, params )

	def onOver( self, mgr, roleDBID ):
		"""
		"""
		tupleTime = time.localtime()
		param1 = str( tupleTime[0] ) + "-" + str( tupleTime[1] ) + "-" + str( tupleTime[2] )
		self.add( mgr, roleDBID, self.processings[roleDBID]["accountDBID"], param1 )
		Messy.onOver( self, mgr, roleDBID )
		
		INFO_MSG( "Add role(DBID:%i) messy info(messyID: %i , param1: %s, param2: %s, param3: %s, )!" % ( roleDBID, self.messyID, param1, "", "" ) )


MESSYS = {	csdefine.MESSY_JOB_TAKE_SILVER : SilverTake(),
			}
# -*- coding: utf_8 -*-
#

"""
ʵ�ּ�¼�ͱ���ͻ��˲�����¼

2010.03.30: writen by huangyongwei
"""

import BigWorld
import Language
import csdefine
import csconst
import ECBExtend
from bwdebug import *


# --------------------------------------------------------------------
# ģ�����
# --------------------------------------------------------------------
_tableName = "custom_OPRecords"				# ����
_allRecords = {}							# ���м�¼��{ optype : set( [recordid, ...] ) }


# --------------------------------------------------------------------
# ���ߺ���
# --------------------------------------------------------------------
def dropTable() :
	"""
	ɾ����
	ע�������в����ã������ֶ�����ɾ����¼��
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "drop table fail! %s" % errstr )
		else :
			INFO_MSG( "table '%s' has been droped!" % _tableName )
	sql = "DROP TABLE IF EXISTS `%s`;" % _tableName
	BigWorld.executeRawDatabaseCommand( sql, callback )

def collectTable() :
	"""
	���������߻��޸ļ�¼���ͻ��¼ id����ɵ�������¼�������
	ע�������в����ã������ֶ����������¼��
	"""
	existKeys = csconst.OPRECORD_ALL_RECORDS
	if len( existKeys ) > 0 :
		sql = "DELETE FROM `%s` WHERE optype not in %r;" % ( _tableName, existKeys )
	elif len( existKeys ) == 1 :
		sql = "DELETE FROM `%s` WHERE optype = %i;" % ( _tableName, existKeys[0] )
	BigWorld.executeRawDatabaseCommand( sql, lambda x, y, z : z )

	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "query table fail! %s" % errstr )
			return

		records = {}
		for strOptype, strRecordID in result :
			optype = int( strOptype )
			recordid = int( strRecordID )
			if optype not in _allRecords :
				continue
			if recordid in _allRecords[optype] :
				continue

			rds = records.get( optype, None )
			if not rds :
				rds = set()
				records[optype] = rds
			rds.add( recordid )

		for optype, rids in records.iteritems() :
			if len( rids ) > 1 :
				sql = "DELETE FROM `%s` WHERE optype = %i and recordid in %r;" % ( _tableName, optype, tuple( rids ) )
			elif len( rids ) > 0 :
				sql = "DELETE FROM `%s` WHERE optype = %i and recordid = %i;" % ( _tableName, optype, rids[0] )
			BigWorld.executeRawDatabaseCommand( sql, lambda x, y, z : z )

	sql = "SELECT optype, recordid FROM `%s`;" % _tableName
	BigWorld.executeRawDatabaseCommand( sql, callback )


# --------------------------------------------------------------------
# ��ȡ��¼�б�
# --------------------------------------------------------------------
def _loadOPTips() :
	"""
	�������� UI ��ʾ��¼
	"""
	path = "config/client/help/UIOpHelper.xml"
	sect = Language.openConfigSection( path )
	assert sect is not None, "config %r is not exist!" % path
	Language.purgeConfig( path )
	ids = set()
	for ds in sect.values() :
		ids.add( int( ds.readString( "id" ), 16 ) )
	return ids

def _loadPixieRecords() :
	"""
	�������� ������UI ��ʾ��¼
	"""
	path = "config/client/help/PixieHelper.xml"
	sect = Language.openConfigSection( path )
	assert sect is not None, "config %r is not exist!" % path
	Language.purgeConfig( path )
	ids = set()
	for ds in sect.values() :
		ids.add( ds.readInt( "id" ) )
	return ids


# --------------------------------------------------------------------
# �ⲿ����
# --------------------------------------------------------------------
def initialize() :
	"""
	�ͻ��˳�ʼ��������¼������
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "create operation record table fail! %s" % errstr  )

	sql = """CREATE TABLE IF NOT EXISTS `custom_OPRecords` (
		`roleDBID`					INT(64),
		`optype`					INT(8) UNSIGNED,
		`recordid` 					INT(16),
		primary key ( roleDBID, optype, recordid )
		);"""
	BigWorld.executeRawDatabaseCommand( sql, callback )

	# �������м�¼
	loaders = { \
		csdefine.OPRECORD_UI_TIPS : _loadOPTips,
		csdefine.OPRECORD_PIXIE_HELP : _loadPixieRecords,
		}
	for optype, loader in loaders.iteritems() :
		_allRecords[optype] = set( loader() )

# -----------------------------------------------------
def getAllTypeRecords( roleDBID, cb ) :
	"""
	��ȡָ�������µ����м�¼
	@type			roleDBID : INT64
	@param			roleDBID : ��ؽ�ɫ���ݿ� ID
	@type			cb		 : callable object
	@param			cb		 : �ص����ص��������һ����������ʾ��¼�б�: { optype : [recordid, ...] }
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "get opertion record fail: %s" % errstr  )
			cb( {} )
		else :
			records = {}
			for strOptype, strRecordID in result :
				optype = int( strOptype )
				recordid = int( strRecordID )
				rds = records.get( optype, None )
				if not rds :
					rds = set()
					records[optype] = rds
				rds.add( recordid )
			cb( records )

	sql = "SELECT optype, recordid FROM `%s` WHERE roleDBID = %i;" % ( _tableName, roleDBID )
	BigWorld.executeRawDatabaseCommand( sql, callback )

def isRecorded( roleDBID, optype, recordid, cb ) :
	"""
	��ȡ��¼
	��ȡָ�������µ����м�¼
	@type			roleDBID : INT64
	@param			roleDBID : ��ؽ�ɫ���ݿ� ID
	@type			optype	 : INT8: MACRO DEFINATION
	@param			optype	 : ��������
	@type			recordid : INT16
	@param			recordid : ��¼��
	@type			cb		 : callable object
	@param			cb		 : �ص����ص��������һ����������ʾ��¼�Ƿ����
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "read opertion record fail: %s" % errstr  )
			cb( False )
		elif int( result[0][0] ) > 0 :
			cb( True )
		else :
			cb( False )

	sql = "SELECT COUNT( * ) from `%s` WHERE roleDBID = %i AND optype = %i AND recordid = %i;" % ( _tableName, roleDBID, optype, recordid )
	BigWorld.executeRawDatabaseCommand( sql, callback )

# -----------------------------------------------------
def addRecord( roleDBID, optype, recordid, cb = None ) :
	"""
	д���¼
	@type			roleDBID : INT64
	@param			roleDBID : ��ؽ�ɫ���ݿ� ID
	@type			optype	 : INT8: MACRO DEFINATION
	@param			optype	 : ��������
	@type			recordid : INT16
	@param			recordid : ��¼��
	@type			cb		 : callable object
	@param			cb		 : �ص����ص��������һ����������ʾ��¼�Ƿ����
	"""
	def callback( result, rows, errstr ) :
		res = False
		if errstr :
			ERROR_MSG( "write record fail: %s" % errstr )
		elif rows > 0 :
			res = True
		if callable( cb ) :
			cb( res )

	sql = "INSERT INTO `%s` ( roleDBID, optype, recordid ) VALUES( %i, %i, %i );" % ( _tableName, roleDBID, optype, recordid )
	BigWorld.executeRawDatabaseCommand( sql, callback )

def removeRecord( roleDBID, optype, recordid, cb = None ) :
	"""
	�Ƴ���¼
	@type			roleDBID : INT64
	@param			roleDBID : ��ؽ�ɫ���ݿ� ID
	@type			optype	 : INT8: MACRO DEFINATION
	@param			optype	 : ��������
	@type			recordid : INT16
	@param			recordid : ��¼��
	@type			cb		 : callable object
	@param			cb		 : �ص����ص��������һ����������ʾ��¼�Ƿ����
	"""
	def callback( result, rows, errstr ) :
		res = False
		if errstr :
			ERROR_MSG( "remove record fail: %s" % errstr )
		elif rows > 0 :
			res = True
		if callable( cb ) :
			cb( res )

	sql = "DELETE FROM `%s` WHERE roleDBID = %i AND optype = %i AND recordid = %i;" % ( _tableName, roleDBID, optype, recordid )
	BigWorld.executeRawDatabaseCommand( sql, callback )

def removeAllTypeRecords( roleDBID, optype ) :
	"""
	ɾ��ָ����ɫ��ĳ�������ͼ�¼
	@type			roleDBID : INT64
	@param			roleDBID : ��ؽ�ɫ���ݿ� ID
	@type			optype	 : INT8: MACRO DEFINATION
	@param			optype	 : ��������
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "drop table fail! %s" % errstr )
		else :
			INFO_MSG( "all records of '%i: %i' have been removed!" % ( roleDBID, optype ) )
	sql = "DELETE FROM `%s` WHERE roleDBID = %i and optype = %i;" % ( _tableName, roleDBID, optype )
	BigWorld.executeRawDatabaseCommand( sql, callback )


# --------------------------------------------------------------------
# implement OPRecord
# --------------------------------------------------------------------
class OPRecorder( object ) :
	def __init__( self ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addCourseHelpHistory( self, topicID ) :
		"""
		<Exposed/>
		���һ�����̰������⵽��ʷ�б��Ա�ʾ�ð��������Ѿ���ʾ��
		@type				topicID : INT16
		@param				topicID : �������� ID�����Ϊ -1 ���ʾҪ ��/�ر� ������ʾ��
									: courseHelpRecords �б����� -1 ʱ��ʾ�رհ�����ʾ�������ʾ����������ʾ
		"""
		if topicID == -1 :									# ������Ƿ񴥷�������ʾ����1��
			if -1 in self.courseHelpRecords :
				self.courseHelpRecords.remove( -1 )
			else :
				self.courseHelpRecords.append( -1 )
		elif topicID not in self.courseHelpRecords :		# �����������������
			self.courseHelpRecords.append( topicID )		# ����ӵ���ʷ�б�

	def opr_saveRecord( self, optype, recordid ) :
		"""
		<Exposed/>
		�����¼
		"""
		addRecord( self.databaseID, optype, recordid )

	def opr_updateClient( self ) :
		"""
		���¿ͻ���
		"""
		def callback( records ) :
			unrecords = {}
			for optype, rds in _allRecords.iteritems() :
				unrecords[optype] = rds - records.get( optype, set() )
			self.__tmpRecordIter = unrecords.iteritems()
			self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_OPR_CBID )
		getAllTypeRecords( self.databaseID, callback )

	def onTimer_opr_updateClient( self, timerID, cbid ) :
		"""
		���������ͣ��ֿ鷢�Ͳ�����¼���ͻ���
		"""
		try :
			optype, unrecordids = self.__tmpRecordIter.next()
			self.client.opr_onRcvUnRecords( optype, list( unrecordids ) )
		except StopIteration :
			del self.__tmpRecordIter
			self.delTimer( timerID )
			self.client.onInitialized( csdefine.ROLE_INIT_OPRECORDS )

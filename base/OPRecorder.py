# -*- coding: utf_8 -*-
#

"""
实现记录和保存客户端操作记录

2010.03.30: writen by huangyongwei
"""

import BigWorld
import Language
import csdefine
import csconst
import ECBExtend
from bwdebug import *


# --------------------------------------------------------------------
# 模块变量
# --------------------------------------------------------------------
_tableName = "custom_OPRecords"				# 表名
_allRecords = {}							# 所有记录表：{ optype : set( [recordid, ...] ) }


# --------------------------------------------------------------------
# 工具函数
# --------------------------------------------------------------------
def dropTable() :
	"""
	删除表
	注：程序中不会用，可以手动调用删除记录表
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
	整理表，把因策划修改记录类型或记录 id，造成的垃圾记录清楚掉。
	注：程序中不会用，可以手动调用整理记录表
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
# 读取记录列表
# --------------------------------------------------------------------
def _loadOPTips() :
	"""
	加载所有 UI 提示记录
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
	加载所有 随身精灵UI 提示记录
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
# 外部函数
# --------------------------------------------------------------------
def initialize() :
	"""
	客户端初始化操作记录管理器
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

	# 加载所有记录
	loaders = { \
		csdefine.OPRECORD_UI_TIPS : _loadOPTips,
		csdefine.OPRECORD_PIXIE_HELP : _loadPixieRecords,
		}
	for optype, loader in loaders.iteritems() :
		_allRecords[optype] = set( loader() )

# -----------------------------------------------------
def getAllTypeRecords( roleDBID, cb ) :
	"""
	获取指定类型下的所有记录
	@type			roleDBID : INT64
	@param			roleDBID : 相关角色数据库 ID
	@type			cb		 : callable object
	@param			cb		 : 回调，回调必需包含一个参数，表示记录列表: { optype : [recordid, ...] }
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
	读取记录
	获取指定类型下的所有记录
	@type			roleDBID : INT64
	@param			roleDBID : 相关角色数据库 ID
	@type			optype	 : INT8: MACRO DEFINATION
	@param			optype	 : 操作类型
	@type			recordid : INT16
	@param			recordid : 记录号
	@type			cb		 : callable object
	@param			cb		 : 回调，回调必需包含一个参数，表示记录是否存在
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
	写入记录
	@type			roleDBID : INT64
	@param			roleDBID : 相关角色数据库 ID
	@type			optype	 : INT8: MACRO DEFINATION
	@param			optype	 : 操作类型
	@type			recordid : INT16
	@param			recordid : 记录号
	@type			cb		 : callable object
	@param			cb		 : 回调，回调必需包含一个参数，表示记录是否存在
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
	移除记录
	@type			roleDBID : INT64
	@param			roleDBID : 相关角色数据库 ID
	@type			optype	 : INT8: MACRO DEFINATION
	@param			optype	 : 操作类型
	@type			recordid : INT16
	@param			recordid : 记录号
	@type			cb		 : callable object
	@param			cb		 : 回调，回调必需包含一个参数，表示记录是否存在
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
	删除指定角色的某操作类型记录
	@type			roleDBID : INT64
	@param			roleDBID : 相关角色数据库 ID
	@type			optype	 : INT8: MACRO DEFINATION
	@param			optype	 : 操作类型
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
		添加一个过程帮助主题到历史列表，以标示该帮助主题已经提示过
		@type				topicID : INT16
		@param				topicID : 帮助主题 ID（如果为 -1 则标示要 打开/关闭 帮助提示，
									: courseHelpRecords 列表中有 -1 时标示关闭帮助提示，否则标示触发帮助提示
		"""
		if topicID == -1 :									# 如果是是否触发帮助提示（－1）
			if -1 in self.courseHelpRecords :
				self.courseHelpRecords.remove( -1 )
			else :
				self.courseHelpRecords.append( -1 )
		elif topicID not in self.courseHelpRecords :		# 如果是其它帮助主题
			self.courseHelpRecords.append( topicID )		# 则，添加到历史列表

	def opr_saveRecord( self, optype, recordid ) :
		"""
		<Exposed/>
		保存记录
		"""
		addRecord( self.databaseID, optype, recordid )

	def opr_updateClient( self ) :
		"""
		更新客户端
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
		按操作类型，分块发送操作记录到客户端
		"""
		try :
			optype, unrecordids = self.__tmpRecordIter.next()
			self.client.opr_onRcvUnRecords( optype, list( unrecordids ) )
		except StopIteration :
			del self.__tmpRecordIter
			self.delTimer( timerID )
			self.client.onInitialized( csdefine.ROLE_INIT_OPRECORDS )

# -*- coding: gb18030 -*-

# written by gjx 2010-06-01
# 此模块专用于管理好友聊天的离线消息

import BigWorld
import cPickle
from bwdebug import *
_oflMsgTblName = "custom_friendOfflineMsgs"

# -----------------------------------------------------
# 创建数据表
# -----------------------------------------------------
def createOFLMsgTable() :
	"""
	创建用于记录离线聊天消息的数据表
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "create friends offline messages table fail! %s" % errstr  )

	sql = """CREATE TABLE IF NOT EXISTS `%s` (
		`sender`			TEXT NOT NULL,
		`receiver`			TEXT NOT NULL,
		`message` 			TEXT NOT NULL,
		`blobs`				BLOB,
		`date`				DATETIME NOT NULL
		);""" % _oflMsgTblName
	BigWorld.executeRawDatabaseCommand( sql, callback )

# -----------------------------------------------------
# 添加离线记录
# -----------------------------------------------------
def addOFLMessage( sender, receiver, msg, blobArgs, date, cb = None ) :
	"""
	添加一条离线消息到数据表
	@param		sender		: 发送者的名称
	@type		sender		: STRING
	@param		receiver	: 接收者的名称
	@type		receiver	: STRING
	@param		msg			: 消息内容
	@type		msg			: STRING
	@param		blobArgs	: 消息参数列表
	@type		blobArgs	: BLOB_ARRAY
	@param		date		: 表示时间的字符串
	@type		date		: string,一定要是能转为mysql时间的格式，
							  例如2010-06-08 16:19:38或者20100608161938，
	@param		cb			: 回调函数（带一个参数）
	@type		cb			: callable object
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "Add messages fail! %s" % errstr )
		if callable( cb ) :
			cb( rows > 0 )

	receiver = BigWorld.escape_string( receiver )
	sender = BigWorld.escape_string( sender )
	msg = BigWorld.escape_string( msg )
	bBlobArgs = BigWorld.escape_string( cPickle.dumps( blobArgs, 2 ) )
	sql = "INSERT INTO `%s` ( receiver, sender, message, blobs, date ) VALUES( '%s', '%s', '%s', '%s', '%s' );" % ( _oflMsgTblName, receiver, sender, msg, bBlobArgs, date )
	BigWorld.executeRawDatabaseCommand( sql, callback )

# -----------------------------------------------------
# 查询消息条数
# -----------------------------------------------------
def queryMsgsAmount( sender, receiver, cb ) :
	"""
	查询某个发送者与某个接收者之间已记录的消息数量
	@param		sender		: 发送者的名称
	@type		sender		: STRING
	@param		receiver	: 接收者的名称
	@type		receiver	: STRING
	@param		cb			: 回调函数（带一个参数），回调查询结果
	@type		cb			: callable object
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "Query message amount fail! %s" % errstr )
		else :
			cb( int( result[0][0] ) )

	sql = "SELECT COUNT(*) FROM `%s` WHERE receiver = '%s' AND sender = '%s';" % ( _oflMsgTblName, receiver, sender )
	BigWorld.executeRawDatabaseCommand( sql, callback )

# -----------------------------------------------------
# 查询某个发送者与某个接收者之间已记录的消息记录
# -----------------------------------------------------
def queryMsgs( sender, receiver, cb ) :
	"""
	查询某个发送者与某个接收者之间已记录的消息数量
	@param		sender		: 发送者的名称
	@type		sender		: STRING
	@param		receiver	: 接收者的名称
	@type		receiver	: STRING
	@param		cb			: 回调函数（带一个参数），回调查询结果
	@type		cb			: callable object
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "Query message amount fail! %s" % errstr )
		else :
			msgs = [ ( m, cPickle.loads( b ), d ) for m, b, d in result ]
			cb( msgs )

	sql = "SELECT message, blobs, date FROM `%s` WHERE receiver = '%s' AND sender = '%s' ORDER BY date;" % ( _oflMsgTblName, receiver, sender )
	BigWorld.executeRawDatabaseCommand( sql, callback )

# -----------------------------------------------------
# 查询发送给某个玩家的所有消息
# -----------------------------------------------------
def queryMsgsToReceiver( receiver, cb ) :
	"""
	查询发送给某个玩家的所有消息
	@param		receiver	: 接收者的名称
	@type		receiver	: STRING
	@param		cb			: 回调函数（带一个参数），回调查询结果
	@type		cb			: callable object
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "Query message fail! %s" % errstr )
		else :
			msgs = [ ( s, m, cPickle.loads( b ), d ) for s, m, b, d in result ]
			cb( msgs )

	sql = "SELECT sender, message, blobs, date FROM `%s` WHERE receiver = '%s' ORDER BY date;" % ( _oflMsgTblName, receiver )
	BigWorld.executeRawDatabaseCommand( sql, callback )

# -----------------------------------------------------
# 查询某个玩家发送的所有消息
# -----------------------------------------------------
def queryMsgsFromSender( sender, cb ) :
	"""
	查询某个玩家发送的所有消息
	@param		sender		: 发送者的名称
	@type		sender		: STRING
	@param		cb			: 回调函数（带一个参数），回调查询结果
	@type		cb			: callable object
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "Query message fail! %s" % errstr )
		else :
			msgs = [ ( r, m, cPickle.loads( b ), d ) for r, m, b, d in result ]
			cb( msgs )

	sql = "SELECT receiver, message, blobs, date FROM `%s` WHERE sender = '%s' ORDER BY date;" % ( _oflMsgTblName, sender )
	BigWorld.executeRawDatabaseCommand( sql, callback )

# -----------------------------------------------------
# 删除一个玩家发给另一个玩家的离线消息
# -----------------------------------------------------
def removeMsgs( sender, receiver, cb = None ) :
	"""
	删除由sender发送给receiver的离线消息
	@param		sender		: 发送者的名称
	@type		sender		: STRING
	@param		receiver	: 接收者的名称
	@type		receiver	: STRING
	@param		cb			: 回调函数（带一个参数），回调删除数量
	@type		cb			: callable object
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "Query message fail! %s" % errstr )
		else :
			if callable( cb ) :
				cb( rows )
			INFO_MSG( "All offline messages between %s and %s have been deleted!" % ( receiver, sender ) )

	sql = "DELETE FROM `%s` WHERE receiver = '%s' AND sender = '%s';" % ( _oflMsgTblName, receiver, sender )
	BigWorld.executeRawDatabaseCommand( sql, callback )

# -----------------------------------------------------
# 删除发送给某个玩家的离线消息
# -----------------------------------------------------
def removeMsgsToReceiver( receiver, cb = None ) :
	"""
	删除发送给某个玩家的离线消息
	@param		receiver	: 接收者的名称
	@type		receiver	: STRING
	@param		cb			: 回调函数（带一个参数），回调删除数量
	@type		cb			: callable object
	"""
	def callback( result, rows, errstr ) :
		if errstr :
			ERROR_MSG( "Query message fail! %s" % errstr )
		else :
			if callable( cb ) :
				cb( rows )
			INFO_MSG( "All offline messages to %s have been deleted!" % receiver )

	sql = "DELETE FROM `%s` WHERE receiver = '%s';" % ( _oflMsgTblName, receiver )
	BigWorld.executeRawDatabaseCommand( sql, callback )


# -*- coding: gb18030 -*-

# written by gjx 2010-06-01
# ��ģ��ר���ڹ�����������������Ϣ

import BigWorld
import cPickle
from bwdebug import *
_oflMsgTblName = "custom_friendOfflineMsgs"

# -----------------------------------------------------
# �������ݱ�
# -----------------------------------------------------
def createOFLMsgTable() :
	"""
	�������ڼ�¼����������Ϣ�����ݱ�
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
# ������߼�¼
# -----------------------------------------------------
def addOFLMessage( sender, receiver, msg, blobArgs, date, cb = None ) :
	"""
	���һ��������Ϣ�����ݱ�
	@param		sender		: �����ߵ�����
	@type		sender		: STRING
	@param		receiver	: �����ߵ�����
	@type		receiver	: STRING
	@param		msg			: ��Ϣ����
	@type		msg			: STRING
	@param		blobArgs	: ��Ϣ�����б�
	@type		blobArgs	: BLOB_ARRAY
	@param		date		: ��ʾʱ����ַ���
	@type		date		: string,һ��Ҫ����תΪmysqlʱ��ĸ�ʽ��
							  ����2010-06-08 16:19:38����20100608161938��
	@param		cb			: �ص���������һ��������
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
# ��ѯ��Ϣ����
# -----------------------------------------------------
def queryMsgsAmount( sender, receiver, cb ) :
	"""
	��ѯĳ����������ĳ��������֮���Ѽ�¼����Ϣ����
	@param		sender		: �����ߵ�����
	@type		sender		: STRING
	@param		receiver	: �����ߵ�����
	@type		receiver	: STRING
	@param		cb			: �ص���������һ�����������ص���ѯ���
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
# ��ѯĳ����������ĳ��������֮���Ѽ�¼����Ϣ��¼
# -----------------------------------------------------
def queryMsgs( sender, receiver, cb ) :
	"""
	��ѯĳ����������ĳ��������֮���Ѽ�¼����Ϣ����
	@param		sender		: �����ߵ�����
	@type		sender		: STRING
	@param		receiver	: �����ߵ�����
	@type		receiver	: STRING
	@param		cb			: �ص���������һ�����������ص���ѯ���
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
# ��ѯ���͸�ĳ����ҵ�������Ϣ
# -----------------------------------------------------
def queryMsgsToReceiver( receiver, cb ) :
	"""
	��ѯ���͸�ĳ����ҵ�������Ϣ
	@param		receiver	: �����ߵ�����
	@type		receiver	: STRING
	@param		cb			: �ص���������һ�����������ص���ѯ���
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
# ��ѯĳ����ҷ��͵�������Ϣ
# -----------------------------------------------------
def queryMsgsFromSender( sender, cb ) :
	"""
	��ѯĳ����ҷ��͵�������Ϣ
	@param		sender		: �����ߵ�����
	@type		sender		: STRING
	@param		cb			: �ص���������һ�����������ص���ѯ���
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
# ɾ��һ����ҷ�����һ����ҵ�������Ϣ
# -----------------------------------------------------
def removeMsgs( sender, receiver, cb = None ) :
	"""
	ɾ����sender���͸�receiver��������Ϣ
	@param		sender		: �����ߵ�����
	@type		sender		: STRING
	@param		receiver	: �����ߵ�����
	@type		receiver	: STRING
	@param		cb			: �ص���������һ�����������ص�ɾ������
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
# ɾ�����͸�ĳ����ҵ�������Ϣ
# -----------------------------------------------------
def removeMsgsToReceiver( receiver, cb = None ) :
	"""
	ɾ�����͸�ĳ����ҵ�������Ϣ
	@param		receiver	: �����ߵ�����
	@type		receiver	: STRING
	@param		cb			: �ص���������һ�����������ص�ɾ������
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


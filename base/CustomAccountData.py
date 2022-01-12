# -*- coding: gb18030 -*-
# $Id: CustomAccountData.py  hd

import BigWorld
from bwdebug import *
from Function import Functor

# �û��Զ�����˺����ݼ���ģ��

class CustomAccountData:
	def __init__( self, accountName, accountDBID ):
		"""
		"""
		self.__acountDBID = accountDBID
		self.__accountName = accountName
		self.__data = {}

	def load( self, callback ):
		"""
		�����Զ�������
		"""
		sql = """(select `key`,`value` from `custom_AccountData`  where `parentID` = %s)
				union all ( select "gmtimelimit", `gmtimelimit` from bigworldLogOnMapping where `logOnName` =  "%s" )""" % ( self.__acountDBID, BigWorld.escape_string( self.__accountName ) )
		BigWorld.executeRawDatabaseCommand( sql, Functor( self.onGetData, callback) ) # ÿһ�ε�½��ȥ����ȡ�����ݣ��Ա㶯̬����

	def onGetData( self, callback, results, rows, errstr ):
		"""
		��ȡ�����ݿⷵ�ص�����
		"""
		if errstr:
			ERROR_MSG( "get custom_AccountData table datas fault! %s" % errstr  )
			return
		if results:
			for result in results:
				if not self.__data.has_key(result[0]):
					self.__data[result[0]] = result[1]
				else:
					ERROR_MSG( "account %s : key %s has aready exist!", self.__accountName, result[0] )
			callback()

	def query( self, key):
		"""
		����ָ����ֵ
		"""
		if self.__data.has_key(key):
			return self.__data[key]
		else:
			return None

	def set( self, key, value):
		"""
		���ú��޸��˺Ź�������
		"""
		isInsert = key not in self.__data
		self.__data[key] = value
		if isInsert:
			self.insertToDB( key, value )
		else:
			self.updateToDB( key, value )


	def updateToDB( self, key, value ):
		"""
		�����ʺŹ�������
		"""

		query = "Update custom_AccountData set `value` = \'%s\' where parentID = %i and `key` = \'%s\';" % ( value, self.__acountDBID, key )
		BigWorld.executeRawDatabaseCommand( query, self.onUpdateToDB )
	
	
	def onUpdateToDB( self, result, dummy, errstr):
		"""
		�����ʺŹ������ݻص�
		"""
		if errstr:
			ERROR_MSG( "account %s : update data wrong! error is %s.", self.__accountName, errstr )



	def insertToDB( self, key, value ):
		"""
		�����ʺŹ�������
		"""
		query = "Insert into custom_AccountData ( `key`, `value`, parentID ) value ( \'%s\', \'%s\', %i);" % ( key, value, self.__acountDBID )
		BigWorld.executeRawDatabaseCommand( query, self.onInsertToDB )
	
	
	def onInsertToDB( self, result, dummy, errstr):
		"""
		�����ʺŹ������ݻص�
		"""
		if errstr:
			ERROR_MSG( "account %s : insert data wrong! error is %s.", self.__accountName, errstr )
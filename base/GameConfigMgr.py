# -*- coding: gb18030 -*-
#

# $Id: DartManager.py,v 1.1 2008-09-05 03:41:04 zhangyuxing Exp $


import BigWorld
from bwdebug import *

"""
���������ó�ʼ���ű�
"""

class GameConfigMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		query = """CREATE TABLE IF NOT EXISTS `custom_GameConfig` (
				`id`			BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_key`		VARCHAR(255),
				`sm_value`		VARCHAR(255),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

		self.init()
	
	def init( self ):
		"""
		"""
		query = "select * from custom_GameConfig"
		BigWorld.executeRawDatabaseCommand( query, self.__onInit )
	

	def __createTableCB( self, result, rows, errstr ):
		"""
		�������ݿ���ص�����
		"""
		if errstr:
			# ���ɱ�����Ĵ���
			ERROR_MSG( "Create custom_GameConfig table fault! %s" % errstr  )
			return


	def __onInit( self,  result, dummy, errstr):
		"""
		"""
		if result:
			for i in result:
				BigWorld.globalData[i[1]] = i[2]
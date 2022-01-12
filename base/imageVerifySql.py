# -*- coding: gb18030 -*-

"""
对于图片验证消息处理，直接数据库操作函数

for rawOfflineMsg table struct:
CREATE TABLE IF NOT EXISTS `rawImageVerify` (
  `parentID` bigint(20) NOT NULL default '0',
  `loginTime` datetime NOT NULL default '0000-00-00 00:00:00',
  `questTime` datetime NOT NULL default '0000-00-00 00:00:00',
  `answerDelay` float NOT NULL default '0',
  `answerType` tinyint(6) NOT NULL default '0'
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 
"""
# $Id: imageVerifySql.py,v 1.3 2007-05-23 06:15:33 phw Exp $

import struct
from bwdebug import *
import BigWorld
import time

MSG_TABLE_NAME = "rawImageVerify"


def writeCallback( result ):
	"""
	@return: 0 if write false, otherwise return 1
	"""
	INFO_MSG( "write image verify log", ["failed","succeeded"][result] )
	return result

def write( who, resultCallback = writeCallback ):
	"""
	@param            who: 玩家
	@param            who: Entity
	@param resultCallback: 回调函数
	@param resultCallback: function
	@param         msg: 消息内容
	@return: 无
	"""
	curTime = time.time()
	parentID = who.databaseID
	loginTime = time.strftime( "%Y-%m-%d %H-%M-%S", time.localtime(who.loginTime) )
	questTime = time.strftime( "%Y-%m-%d %H-%M-%S", time.localtime(curTime) )
	answerDelay = who.ivfAnswerTime
	answerType = who.ivfAnswerType
	query = "insert into %s values (%i, \"%s\", \"%s\", %f, %i)" % ( MSG_TABLE_NAME, parentID, loginTime, questTime, answerDelay, answerType )
	#DEBUG_MSG( query )
	BigWorld.executeRawDatabaseCommand( query, resultCallback )
	return	# the end


#
# $Log: not supported by cvs2svn $
# Revision 1.2  2005/11/25 08:55:17  phw
# no message
#
# Revision 1.1  2005/11/23 09:29:26  phw
# 图片认证日志写入数据库代码
#
#

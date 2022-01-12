# -*- coding: gb18030 -*-
#
# $Id: Postoffice.py,v 1.3 2007-06-14 08:43:31 panguankong Exp $

"""
邮件系统
"""

import BigWorld
import time
from bwdebug import *
import Function

MAIL_MAX_ID = 9999999	# 邮件最大ID号
MAIL_CHECK_TIMERID = 2000 # 邮件生存ID
MAIL_CHECK_TIME = 5 # 邮件检测时间

class Postoffice(BigWorld.Base):
	def __init__( self ):
		self.entities = {}

		# 创建表格
		def __onCreateTable( result, dummy, error ):
			if error:
				ERROR_MSG( "create postoffice table error!", error)
		
		createTableCode = "CREATE TABLE IF NOT EXISTS `Postoffice` (  `id` bigint(20) NOT NULL auto_increment,  `src` char(255) NOT NULL default '',  `des` char(255) NOT NULL default '',  `existTime` int(11) NOT NULL default '0',  `isNotify` tinyint(1) NOT NULL default '0',  `item` char(255) NOT NULL default '',  `money` int(11) NOT NULL default '0',  `msg` char(255) NOT NULL default '',  `createTime` int(11) NOT NULL default '0',  PRIMARY KEY  (`id`),  KEY `desIndex` (`des`)) ENGINE=MyISAM DEFAULT CHARSET=latin1; "
		BigWorld.executeRawDatabaseCommand( createTableCode, __onCreateTable )
		
		# 注册邮件系统
		self.registerGlobally("Postoffice", self._onRegisterPostoffice)

	#-----------------------------------------------------------
	# private
	def _onRegisterPostoffice(self, complete):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register Postoffice Fail!" )
			# again
			self.registerGlobally("Postoffice", self._onRegisterPostoffice)
		else:
			self.playerName = "Postoffice"			
			INFO_MSG("Postoffice Create Complete!")		
			if not self.save:
				self.writeToDB( self._onCreatedPostoffice )
		
	def _onCreatedPostoffice( self, success, entity ):
		"""
		把实体写入数据库回调
		"""
		if success:
			self.save = True
			INFO_MSG("Postoffice Write To DataBase Complete!")		
		else:
			ERROR_MSG( "Postoffice can't write to DataBase!" )
	
	#------------------------------------------------------------------------------------
	# private
	def __addMail( self, mail ):
		"""
		添加邮件到邮箱
		"""
		def onAddCB( result, dummy, error ):
			if error:
				ERROR_MSG("add mail %s error! %s"%(mail['src'], error))
				return
		
		code = "insert into Postoffice(src,des,existTime,isNotify,item,money,msg,createTime) Value( \'%s\',\'%s\',%d,%d,\'%s\',%d,\'%s\',%d );"%(	mail["src"],mail["des"],mail["existTime"],mail["isNotify"],mail["item"],mail["money"],mail["msg"],mail["createTime"])
		BigWorld.executeRawDatabaseCommand( code, onAddCB )
	
	def __findMails( self, name,callback ):
		"""
		收信 从数据库FriendLetters表中查找好友的信件
		"""
		code = "select * from Postoffice where des = \'%s\' Order By id desc"%(name)
		BigWorld.executeRawDatabaseCommand( code, callback )
	
	def __removeMails( self, name ):
		"""
		删除自己的信 删除FriendLetters表中自己的信
		"""
		def onRemoveCB( result, dummy, error ):
			if error:
				ERROR_MSG("delete mails %s error! %s"%(name, error))
				return
			
		code = "delete from Postoffice where des = \'%s\'"%(name)
		BigWorld.executeRawDatabaseCommand( code, onRemoveCB )
	
	#------------------------------------------------------------------------------------
	# public	
	def send( self, src, des, existTime, msg, money, item ):
		"""
		define
		发邮件
		让邮件系统处理mail，邮件系统发送mail
		功能：
		    同时为邮件分配一个ID，用于标识它，并保存邮件，并通过在线记录判断邮件是否可以直接发送到目得地。
		作用：
		    发送邮件到有关entity
		@type	src	:	string
		@param	src	:	发信人
		@type	des	:	string
		@param	des	:	收信人
		@type	existTime:	INT32
		@param	existTime:	有效时间
		@type	msg	:	string
		@param	msg	:	文字信息
		@type	money	:	int32
		@param	money	:	金钱
		@type	item	:	string
		@param	item	:	物品
		"""
		#INFO_MSG( "===== postoffice send:", src, des )
		if src == des:
			WARNING_MSG( "send mail to self." )
			return
		
		# 添加邮件
		mail = {
			"src"		:	src,
			"des"		:	des,
			"existTime"	:	time.time()+existTime,
			"isNotify"	:	0,
			"item"		:	item,
			"money"		:	money,
			"msg"		:	msg,
			"createTime":	time.time(),
			}
		
		# 如果目标在线，则发送邮件
		if self.entities.has_key( des ):
			self.entities[des].cell.onReceiveMail( mail )
		else:
			# 目标不在线，则记录邮件
			self.__addMail( mail )
	
	def logon( self, name, base ):
		"""
		define
		上线
		
		功能：
		    在有关entity上线时，记录在线的有关entity，把该有关entity的邮件发送给有关entity
		
		作用：
		    为了能上邮件直接发送或通知到在线有关entity上。
		@type	name	:	string
		@param	name	:	实体名称，用于判断目标entity
		@return: 无
		"""
		#INFO_MSG( "===== postoffice logon:", name )
		self.entities[name] = base		
		self.checkMail( name )
	
	def logout( self, name ):
		"""
		define
		下线
		功能：
		    有关entity离线，停止邮件发送，删除在线有关entity记录
		作用：
		    为了上邮件不发到不在线的有关entity上
		@type	name	:	string
		@param	name	:	实体名称，用于判断目标entity
		"""
		#INFO_MSG( "===== postoffice logout:", name )
		if self.entities.has_key( name ):
			self.entities.pop( name )

	def checkMail( self, name ):
		"""
		define
		检查信箱
		如果信箱里有玩家的信件，则调用cell::onReceiveMail通知实体
		@type	name	:	string
		@param	name	:	实体名称，用于判断目标entity
		"""
		if self.entities.has_key( name ):
			self.__findMails( name, Function.Functor( self.__onMails, name ) )
		
	def __onMails( self, name, result, dummy, error ):
		"""
		发送信件
		"""
		if result == None:
			return
		
		l = len(result)
		if l == 0:
			DEBUG_MSG("%s not has mail!" % name)
			return

		for i in xrange( l - 1, -1, -1 ):
			info = result[i]
			if time.time() - eval(info[8]) > eval(info[3]) and eval(info[3]):
				continue
			
			base = self.entities[name]
			if base:
				mail = {
						"src"		:	info[1],
						"des"		:	info[2],
						"existTime"	:	eval(info[3]),
						"isNotify"	:	eval(info[4]),
						"item"		:	info[5],
						"money"		:	eval(info[6]),
						"msg"		:	info[7],
						"createTime":	eval(info[8]),
						}
				base.cell.onReceiveMail( mail )

	def remove( self, name ):
		"""
		删除该实体的邮件
		"""
		self.__removeMails( name )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/06/14 07:08:54  panguankong
# 修改邮件系统为直接对数据库操作
#
# Revision 1.1  2007/03/26 07:04:31  panguankong
# 添加文件
#
# 
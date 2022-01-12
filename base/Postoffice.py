# -*- coding: gb18030 -*-
#
# $Id: Postoffice.py,v 1.3 2007-06-14 08:43:31 panguankong Exp $

"""
�ʼ�ϵͳ
"""

import BigWorld
import time
from bwdebug import *
import Function

MAIL_MAX_ID = 9999999	# �ʼ����ID��
MAIL_CHECK_TIMERID = 2000 # �ʼ�����ID
MAIL_CHECK_TIME = 5 # �ʼ����ʱ��

class Postoffice(BigWorld.Base):
	def __init__( self ):
		self.entities = {}

		# �������
		def __onCreateTable( result, dummy, error ):
			if error:
				ERROR_MSG( "create postoffice table error!", error)
		
		createTableCode = "CREATE TABLE IF NOT EXISTS `Postoffice` (  `id` bigint(20) NOT NULL auto_increment,  `src` char(255) NOT NULL default '',  `des` char(255) NOT NULL default '',  `existTime` int(11) NOT NULL default '0',  `isNotify` tinyint(1) NOT NULL default '0',  `item` char(255) NOT NULL default '',  `money` int(11) NOT NULL default '0',  `msg` char(255) NOT NULL default '',  `createTime` int(11) NOT NULL default '0',  PRIMARY KEY  (`id`),  KEY `desIndex` (`des`)) ENGINE=MyISAM DEFAULT CHARSET=latin1; "
		BigWorld.executeRawDatabaseCommand( createTableCode, __onCreateTable )
		
		# ע���ʼ�ϵͳ
		self.registerGlobally("Postoffice", self._onRegisterPostoffice)

	#-----------------------------------------------------------
	# private
	def _onRegisterPostoffice(self, complete):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
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
		��ʵ��д�����ݿ�ص�
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
		����ʼ�������
		"""
		def onAddCB( result, dummy, error ):
			if error:
				ERROR_MSG("add mail %s error! %s"%(mail['src'], error))
				return
		
		code = "insert into Postoffice(src,des,existTime,isNotify,item,money,msg,createTime) Value( \'%s\',\'%s\',%d,%d,\'%s\',%d,\'%s\',%d );"%(	mail["src"],mail["des"],mail["existTime"],mail["isNotify"],mail["item"],mail["money"],mail["msg"],mail["createTime"])
		BigWorld.executeRawDatabaseCommand( code, onAddCB )
	
	def __findMails( self, name,callback ):
		"""
		���� �����ݿ�FriendLetters���в��Һ��ѵ��ż�
		"""
		code = "select * from Postoffice where des = \'%s\' Order By id desc"%(name)
		BigWorld.executeRawDatabaseCommand( code, callback )
	
	def __removeMails( self, name ):
		"""
		ɾ���Լ����� ɾ��FriendLetters�����Լ�����
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
		���ʼ�
		���ʼ�ϵͳ����mail���ʼ�ϵͳ����mail
		���ܣ�
		    ͬʱΪ�ʼ�����һ��ID�����ڱ�ʶ�����������ʼ�����ͨ�����߼�¼�ж��ʼ��Ƿ����ֱ�ӷ��͵�Ŀ�õء�
		���ã�
		    �����ʼ����й�entity
		@type	src	:	string
		@param	src	:	������
		@type	des	:	string
		@param	des	:	������
		@type	existTime:	INT32
		@param	existTime:	��Чʱ��
		@type	msg	:	string
		@param	msg	:	������Ϣ
		@type	money	:	int32
		@param	money	:	��Ǯ
		@type	item	:	string
		@param	item	:	��Ʒ
		"""
		#INFO_MSG( "===== postoffice send:", src, des )
		if src == des:
			WARNING_MSG( "send mail to self." )
			return
		
		# ����ʼ�
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
		
		# ���Ŀ�����ߣ������ʼ�
		if self.entities.has_key( des ):
			self.entities[des].cell.onReceiveMail( mail )
		else:
			# Ŀ�겻���ߣ����¼�ʼ�
			self.__addMail( mail )
	
	def logon( self, name, base ):
		"""
		define
		����
		
		���ܣ�
		    ���й�entity����ʱ����¼���ߵ��й�entity���Ѹ��й�entity���ʼ����͸��й�entity
		
		���ã�
		    Ϊ�������ʼ�ֱ�ӷ��ͻ�֪ͨ�������й�entity�ϡ�
		@type	name	:	string
		@param	name	:	ʵ�����ƣ������ж�Ŀ��entity
		@return: ��
		"""
		#INFO_MSG( "===== postoffice logon:", name )
		self.entities[name] = base		
		self.checkMail( name )
	
	def logout( self, name ):
		"""
		define
		����
		���ܣ�
		    �й�entity���ߣ�ֹͣ�ʼ����ͣ�ɾ�������й�entity��¼
		���ã�
		    Ϊ�����ʼ������������ߵ��й�entity��
		@type	name	:	string
		@param	name	:	ʵ�����ƣ������ж�Ŀ��entity
		"""
		#INFO_MSG( "===== postoffice logout:", name )
		if self.entities.has_key( name ):
			self.entities.pop( name )

	def checkMail( self, name ):
		"""
		define
		�������
		�������������ҵ��ż��������cell::onReceiveMail֪ͨʵ��
		@type	name	:	string
		@param	name	:	ʵ�����ƣ������ж�Ŀ��entity
		"""
		if self.entities.has_key( name ):
			self.__findMails( name, Function.Functor( self.__onMails, name ) )
		
	def __onMails( self, name, result, dummy, error ):
		"""
		�����ż�
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
		ɾ����ʵ����ʼ�
		"""
		self.__removeMails( name )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/06/14 07:08:54  panguankong
# �޸��ʼ�ϵͳΪֱ�Ӷ����ݿ����
#
# Revision 1.1  2007/03/26 07:04:31  panguankong
# ����ļ�
#
# 
# -*- coding: gb18030 -*-
#
# $Id: ProtectTong.py,v 1.12 2008/08/07 07:10:40 kebiao Exp $

import time
import BigWorld
from bwdebug import *
import csdefine
import csstatus
import csconst
from Function import Functor
import Love3
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

sqlcmd = "select id, sm_playerName from tbl_TongEntity where sm_prestige >= 400 and sm_level > 1 order by rand() limit 1;"
sqlcmd1 = "select sm_playerName from tbl_TongEntity where id=%i;"
sqlcmdMidAutumn = "select id, sm_playerName from tbl_TongEntity order by rand() limit 1;"


class ProtectTong( BigWorld.Base ):
	def __init__( self ):
		self.registerGlobally( "ProtectTong", self.onRegisterSelf )
		self.teamDBIDDict = {}
		self.spaces = []
		self.tongDBID = 0
		self.tongName = ""
		self.protectTongOverCount = 0

	def onRegisterSelf( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register ProtectTong Failed!" )
			# again
			self.registerGlobally( "ProtectTong", self.onRegisterSelf )
		else:
			DEBUG_MSG( "ProtectTong Register Succeed!" )
			BigWorld.globalData["ProtectTong"] = self				# ע�ᵽ���еķ�������
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"ProtectTong_start_notice" : "onStartNotice",
						"ProtectTong_start" : "onStart",
						"ProtectTong_end" : "onEnd",
						"ProtectTong_mid_autumn_start_notice" : "onStartNoticeMidAutumn",
						"ProtectTong_mid_autumn_start" : "onStartMidAutumn",
						"ProtectTong_mid_autumn_end" : "onEndMidAutumn",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.searchTong_Callback, cschannel_msgs.BCT_PROTECTTONG_BEGIN_NOTIFY_0 ) )
		INFO_MSG( "ProtectTong", "notice", "" )

	def searchTong_Callback( self, msg, result, dummy, error ):
		"""
		����Ҫ�����İ�� ���ݿ�ص�
		"""
		DEBUG_MSG( "searchTong start:", result, dummy, error )
		if (error):
			ERROR_MSG( error )
			return

		if len( result ) <= 0:
			DEBUG_MSG( "��������û�з��������İ�ᣬ���α������ɻ�������ɹ���" )
			return

		tongDBID = int( result[ 0 ][ 0 ] )
		self.tongDBID = tongDBID
		tongName = result[ 0 ][ 1 ]
		self.tongName = tongName
		Love3.g_baseApp.anonymityBroadcast( msg % tongName, [] )
		DEBUG_MSG( "searchTong::[tongDBID:%d, tongName:%s]" % ( tongDBID, tongName ) )

	def onStart( self ):
		"""
		define method.
		���ʼ
		"""
		if BigWorld.globalData.has_key( "AS_ProtectTong" ):
			curTime = time.localtime()
			ERROR_MSG( "ProtectTong is running��%i:%i try open"%(curTime[3],curTime[4] ) )
			return

		if self.tongDBID > 0:
			BigWorld.executeRawDatabaseCommand( sqlcmd1 % self.tongDBID, Functor( self.checkTong_Callback, cschannel_msgs.BCT_PROTECTTONG_BEGIN_NOTIFY, csdefine.PROTECT_TONG_NORMAL ) )
		INFO_MSG( "ProtectTong", "start", "" )
		

	def checkTong_Callback( self, msg, protectType, result, dummy, error ):
		"""
		��ѯ�Է���ἶ�� ���ݿ�ص�
		"""
		DEBUG_MSG( "checkTong start:", result, dummy, error )
		if (error):
			ERROR_MSG( error )
			return

		if len( result ) <= 0:
			DEBUG_MSG( "���( %s )�Ѿ��������ˣ����α������ɻ�жϡ�" % self.tongName )
			return

		Love3.g_baseApp.anonymityBroadcast( msg % self.tongName, [] )
		BigWorld.globalData[ "AS_ProtectTong" ] = ( self.tongDBID, self.tongName, protectType )
		BigWorld.globalData[ "TongManager" ].onProtectTongStart( self.tongDBID, protectType )
		DEBUG_MSG( "ProtectTong::start[tongDBID:%d, tongName:%s, protectType:%i]" % ( self.tongDBID, self.tongName, protectType ) )

	def receiveMonsterCount( self, amount ):
		"""
		Define method.
		���չ����������Ա�ͳ��ɱ�����
		
		��Ϊ���������ڰ����صĿռ������У���������������ɱ������ɹ�����������Щ�������ã�
		����ʱ����������Ķ�����ʱ��ô����10:17 2010-8-24��wsf
		"""
		self.protectTongOverCount = amount

	def onEnd( self ):
		"""
		define method.
		�����
		"""
		# ��ֹ�������ڻ��ʼʱ��֮������ ���Ҳ����ñ��
		if not BigWorld.globalData.has_key( "AS_ProtectTong" ):
			curTime = time.localtime()
			ERROR_MSG( "ProtectTong is running��%i:%i try close"%( curTime[3],curTime[4] ) )
			return

		if self.protectTongOverCount > 0:
			tongName = BigWorld.globalData[ "AS_ProtectTong" ][1]
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_PROTECTTONG_END_NOTIFY % ( tongName, tongName ), [] )

		BigWorld.globalData[ "TongManager" ].onProtectTongEnd( self.tongDBID )
		self.tongDBID = 0
		self.tongName = ""

		for spaceMB in self.spaces:
			spaceMB.cell.onProtectTongEnd()

		del BigWorld.globalData[ "AS_ProtectTong" ]
		INFO_MSG( "ProtectTong", "end", "" )

	def onStartNoticeMidAutumn( self ):
		"""
		Define method.
		��ʼ��������������֪ͨ
		"""
		BigWorld.executeRawDatabaseCommand( sqlcmdMidAutumn, Functor( self.searchTong_Callback, cschannel_msgs.BCT_PROTECTTONG_MID_AUTUMN_BEGIN_NOTIFY_0 ) )
		INFO_MSG( "ProtectTong", "notice", "MidAutumn" )
		
	def onStartMidAutumn( self ):
		"""
		Define method.
		��ʼ������������
		"""
		if BigWorld.globalData.has_key( "AS_ProtectTong" ):
			curTime = time.localtime()
			ERROR_MSG( "ProtectTong is running��%i:%i try open"%(curTime[3],curTime[4] ) )
			return

		if self.tongDBID > 0:
			BigWorld.executeRawDatabaseCommand( sqlcmd1 % self.tongDBID, Functor( self.checkTong_Callback, cschannel_msgs.BCT_PROTECTTONG_MID_AUTUMN_BEGIN_NOTIFY, csdefine.PROTECT_TONG_MID_AUTUMN ) )
		
		INFO_MSG( "ProtectTong", "start", "MidAutumn" )

	def onEndMidAutumn( self ):
		"""
		Define method.
		����������������
		"""
		# ��ֹ�������ڻ��ʼʱ��֮������ ���Ҳ����ñ��
		if not BigWorld.globalData.has_key( "AS_ProtectTong" ):
			curTime = time.localtime()
			ERROR_MSG( "ProtectTong is running��%i:%i try close"%( curTime[3],curTime[4] ) )
			return

		if self.protectTongOverCount > 0:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_PROTECTTONG_MID_AUTUMN_END_NOTIFY, [] )

		BigWorld.globalData[ "TongManager" ].onProtectTongEnd( self.tongDBID )
		self.tongDBID = 0
		self.tongName = ""

		for spaceMB in self.spaces:
			spaceMB.cell.onProtectTongEnd()

		del BigWorld.globalData[ "AS_ProtectTong" ]
		INFO_MSG( "ProtectTong", "end", "MidAutumn" )

		
	def onTimer( self, id, userArg ):
		"""
		"""
		pass

	def onRegisterProtectTongSpace( self, spaceMB ):
		"""
		define method.
		ע��ﻧ���ɲ����ĸ���
		"""
		self.spaces.append( spaceMB )

	def protectTongOver( self, duizhangName, protectType ):
		"""
		define method.
		һ���������������
		
		"""
		if not BigWorld.globalData.has_key( "AS_ProtectTong" ):
			return
		self.protectTongOverCount -= 1
		
		tongName = BigWorld.globalData[ "AS_ProtectTong" ][1]
		if self.protectTongOverCount <= 0:
			if protectType == csdefine.PROTECT_TONG_NORMAL:
				msg = cschannel_msgs.BCT_PROTECTTONG_MONSTER_CLEAR_NOTIFY % tongName
			elif protectType == csdefine.PROTECT_TONG_MID_AUTUMN:
				msg = cschannel_msgs.BCT_PROTECTTONG_MID_AUTUMN_MONSTER_CLEAR_NOTIFY
			else:
				msg = cschannel_msgs.BCT_PROTECTTONG_MONSTER_CLEAR_NOTIFY % tongName
		else:
			if protectType == csdefine.PROTECT_TONG_NORMAL:
				msg = cschannel_msgs.BCT_PROTECTTONG_WIN_NOTIFY % ( duizhangName, tongName )
			elif protectType == csdefine.PROTECT_TONG_MID_AUTUMN:
				msg = cschannel_msgs.BCT_PROTECTTONG_MID_AUTUMN_WIN_NOTIFY % ( duizhangName, tongName )
			else:
				msg = cschannel_msgs.BCT_PROTECTTONG_WIN_NOTIFY % ( duizhangName, tongName )
		Love3.g_baseApp.anonymityBroadcast( msg, [] )
		
#
# $Log: ProtectTong.py,v $
#
#
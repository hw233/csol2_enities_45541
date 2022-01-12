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
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register ProtectTong Failed!" )
			# again
			self.registerGlobally( "ProtectTong", self.onRegisterSelf )
		else:
			DEBUG_MSG( "ProtectTong Register Succeed!" )
			BigWorld.globalData["ProtectTong"] = self				# 注册到所有的服务器中
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
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
		活动开始通知
		"""
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.searchTong_Callback, cschannel_msgs.BCT_PROTECTTONG_BEGIN_NOTIFY_0 ) )
		INFO_MSG( "ProtectTong", "notice", "" )

	def searchTong_Callback( self, msg, result, dummy, error ):
		"""
		搜索要攻击的帮会 数据库回调
		"""
		DEBUG_MSG( "searchTong start:", result, dummy, error )
		if (error):
			ERROR_MSG( error )
			return

		if len( result ) <= 0:
			DEBUG_MSG( "本服务器没有符合条件的帮会，本次保护帮派活动启动不成功。" )
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
		活动开始
		"""
		if BigWorld.globalData.has_key( "AS_ProtectTong" ):
			curTime = time.localtime()
			ERROR_MSG( "ProtectTong is running，%i:%i try open"%(curTime[3],curTime[4] ) )
			return

		if self.tongDBID > 0:
			BigWorld.executeRawDatabaseCommand( sqlcmd1 % self.tongDBID, Functor( self.checkTong_Callback, cschannel_msgs.BCT_PROTECTTONG_BEGIN_NOTIFY, csdefine.PROTECT_TONG_NORMAL ) )
		INFO_MSG( "ProtectTong", "start", "" )
		

	def checkTong_Callback( self, msg, protectType, result, dummy, error ):
		"""
		查询对方帮会级别 数据库回调
		"""
		DEBUG_MSG( "checkTong start:", result, dummy, error )
		if (error):
			ERROR_MSG( error )
			return

		if len( result ) <= 0:
			DEBUG_MSG( "帮会( %s )已经不存在了，本次保护帮派活动中断。" % self.tongName )
			return

		Love3.g_baseApp.anonymityBroadcast( msg % self.tongName, [] )
		BigWorld.globalData[ "AS_ProtectTong" ] = ( self.tongDBID, self.tongName, protectType )
		BigWorld.globalData[ "TongManager" ].onProtectTongStart( self.tongDBID, protectType )
		DEBUG_MSG( "ProtectTong::start[tongDBID:%d, tongName:%s, protectType:%i]" % ( self.tongDBID, self.tongName, protectType ) )

	def receiveMonsterCount( self, amount ):
		"""
		Define method.
		接收怪物总数，以便统计杀怪情况
		
		因为怪物配置在帮会领地的空间配置中，更合理的做法是由保护帮派管理器管理这些怪物配置，
		但此时不宜做过多改动，临时这么处理。10:17 2010-8-24，wsf
		"""
		self.protectTongOverCount = amount

	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		# 防止服务器在活动开始时间之后启动 则找不到该标记
		if not BigWorld.globalData.has_key( "AS_ProtectTong" ):
			curTime = time.localtime()
			ERROR_MSG( "ProtectTong is running，%i:%i try close"%( curTime[3],curTime[4] ) )
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
		开始保护帮派中秋活动的通知
		"""
		BigWorld.executeRawDatabaseCommand( sqlcmdMidAutumn, Functor( self.searchTong_Callback, cschannel_msgs.BCT_PROTECTTONG_MID_AUTUMN_BEGIN_NOTIFY_0 ) )
		INFO_MSG( "ProtectTong", "notice", "MidAutumn" )
		
	def onStartMidAutumn( self ):
		"""
		Define method.
		开始保护帮派中秋活动
		"""
		if BigWorld.globalData.has_key( "AS_ProtectTong" ):
			curTime = time.localtime()
			ERROR_MSG( "ProtectTong is running，%i:%i try open"%(curTime[3],curTime[4] ) )
			return

		if self.tongDBID > 0:
			BigWorld.executeRawDatabaseCommand( sqlcmd1 % self.tongDBID, Functor( self.checkTong_Callback, cschannel_msgs.BCT_PROTECTTONG_MID_AUTUMN_BEGIN_NOTIFY, csdefine.PROTECT_TONG_MID_AUTUMN ) )
		
		INFO_MSG( "ProtectTong", "start", "MidAutumn" )

	def onEndMidAutumn( self ):
		"""
		Define method.
		结束保护帮派中秋活动
		"""
		# 防止服务器在活动开始时间之后启动 则找不到该标记
		if not BigWorld.globalData.has_key( "AS_ProtectTong" ):
			curTime = time.localtime()
			ERROR_MSG( "ProtectTong is running，%i:%i try close"%( curTime[3],curTime[4] ) )
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
		注册帮户帮派产生的副本
		"""
		self.spaces.append( spaceMB )

	def protectTongOver( self, duizhangName, protectType ):
		"""
		define method.
		一个活动主动被结束了
		
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
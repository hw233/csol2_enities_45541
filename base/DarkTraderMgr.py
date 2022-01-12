# -*- coding: gb18030 -*-
#
# 投机商人管理器 2008-12-25 SongPeifang
#
import Love3
import csdefine
import BigWorld
import cschannel_msgs
import random
import Math
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from Love3 import g_DarkTraderDatas
from csconst import g_maps_info
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objects = GameObjectFactory.instance()


DARK_TRADER_BEGIN 	= 0					#投机商人开始活动
DARK_TRADER_RELOAD = 1					#投机商人结束活动

class DarkTraderMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self._npcClassName = None

		# 投机商人的className 目前只有这一个投机商人，但是不排除日后策划加其他的商人的可能
		if g_DarkTraderDatas._DarkTraderDatas == None or len( g_DarkTraderDatas._DarkTraderDatas ) == 0:
			ERROR_MSG( "投机商人出售物品配置表配置错误或读取错误！" )
		else:
			# 投机商人的className
			self._npcClassName = g_DarkTraderDatas._DarkTraderDatas.keys()[0]
		# 把自己注册为globalData全局实体
		self.registerGlobally( "DarkTraderMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register DarkTraderMgr Fail!" )
			self.registerGlobally( "DarkTraderMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["DarkTraderMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("DarkTraderMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"DarkTraderMgr_createNPC" : "onStart",
						"DarkTraderMgr_end" : "onEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def onStart( self ):
		"""
		define method.
		投机商人刷出
		"""
		npcSpaceName = self.genDarkTraderMap()			# 随机产生投机商人可能刷出的地图spaceName
		if not g_maps_info.has_key( npcSpaceName ):
			ERROR_MSG( "黑市地图信息生成错误，地图列表已过期！" )
			return
		npcSpaceNameCh = g_maps_info[ npcSpaceName ]	# 地图的中文名，如“凤鸣”
		npcPosition = self.genDarkTraderPosition( npcSpaceName )	# 随机产生的坐标点
		npcDirection = ( 0, 0, 0 )
		space = g_objects.getObject( npcSpaceName )
		maxLine = 1
		if hasattr( space, "maxLine" ):
			maxLine = space.maxLine

		# 如果存在多条线， 每条线都刷
		for line in xrange( maxLine ):
			BigWorld.globalData["SpaceManager"].createNPCObjectFormBase( npcSpaceName, \
																		self._npcClassName, \
																		npcPosition, \
																		npcDirection, \
																		{ "_lineNumber_" : line + 1 } )

		g_DarkTraderDatas.genCollectGoodID( self._npcClassName, npcSpaceName )	# 根据地图产生投机商人此次收购的商品名
		npcCurrGoodName = g_DarkTraderDatas._currentGoodName		# 目的是通知全服务器该投机商人收购的商品
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_HSSR_TRADER_SITE_NOTIFY % ( npcSpaceNameCh, npcPosition[0], npcPosition[2], npcCurrGoodName ), [] )
		INFO_MSG( "DarkTraderMgr.", "start", "" )


	def onEnd( self ):
		"""
		define method
		"""
		INFO_MSG( "DarkTraderMgr.", "end", "" )

	def genDarkTraderMap( self ):
		"""
		生成投机商人NPC的地图
		"""
		dark_trader_maps = g_DarkTraderDatas._DarkTraderMaps
		index = random.randint( 0, len( dark_trader_maps ) - 1 )
		spaceName = dark_trader_maps[index]
		return spaceName

	def genDarkTraderPosition( self, spaceName ):
		"""
		生成投机商人的位置坐标
		"""
		# 具体如何生成尚未确定，要与策划讨论，暂时写成这样
		x = random.randint( -3,3 )
		y = 3	# 向上多生成3米避免陷入地下
		z = random.randint( -3,3 )
		npcPosition = (0,0,0)
		posList = g_DarkTraderDatas._DarkTraderPositions[spaceName]
		index = random.randint( 0,len( posList ) - 1 )
		npcPosition = posList[index] + Math.Vector3( x, y, z )
		return npcPosition
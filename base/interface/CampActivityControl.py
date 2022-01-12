# -*- coding: gb18030 -*-

import random

import BigWorld
from csconst import g_maps_info
from config.server.CampMapPosConfig import Datas as ActivityPosData
import Love3

import csdefine
import csconst
import cschannel_msgs


"""
阵营活动控制器
"""
class ActIntf( object ):
	def __init__( self ):
		object.__init__( self )
		self.openSpaces = []
		self.activity = 0
		self.activityTime = 0
		self.attrCamp = 0
	
	def init( self, mgr, spaces, camp , activityTime ):
		self.openSpaces = spaces
		self.attrCamp = camp
		self.activityTime = activityTime
		
	def _notify( self ):
		"""
		活动广播
		"""
		pass
	
	def start( self, mgr ):
		"""
		活动开启
		"""
		self._notify()
		mgr.startActivityCountDown()
		mgr.addTimer( 1, 0, 3 )			# 刷日常任务
	
	def close( self, mgr ):
		"""
		活动结束
		"""
		mgr.destroyMonster()
		mgr.addTimer( 1, 0, 3 )
		
	def checkAndReward( self ):
		pass
		
	def getBroadMsgDict( self, msg ):
		"""
		区分阵营生成地图寻路坐标
		"""
		d_spaceStr = ""
		t_spaceStr = ""
		for spaceName in self.openSpaces:
			pos = self.getDemonPos( spaceName )
			markStr = self.getMarkStr( spaceName, pos )
			d_spaceStr += markStr + ","
			
			pos = self.getTaoismPos( spaceName )
			markStr = self.getMarkStr( spaceName, pos )
			t_spaceStr += markStr + ","
			
		dict = { csdefine.ENTITY_CAMP_DEMON : msg % d_spaceStr[0:-1],\
				 csdefine.ENTITY_CAMP_TAOISM : msg % t_spaceStr[0:-1] }
		return dict
		
	def getMarkStr( self, spaceName, dstPos ):
		"""
		生成地图链接字符串
		"""
		pos = [ dstPos[0], dstPos[1], dstPos[2] ]
		spaceMark = cschannel_msgs.CAMP_ACT_MARK_STR % ( g_maps_info[ spaceName ], pos, spaceName )
		return spaceMark
		
	def getDemonPos( self, spaceName ):
		"""
		获得地图的魔道寻路坐标
		"""
		for i in ActivityPosData:
			if i["spaceName"] == spaceName:
				return i["demonPos"]
		return ( 0, 0, 0 )
		
	def getTaoismPos( self, spaceName ):
		"""
		获得地图的仙道寻路坐标
		"""
		for i in ActivityPosData:
			if i["spaceName"] == spaceName:
				return i["taoismPos"]
		return ( 0, 0, 0 )

class ActDesBase( ActIntf ):
	"""
	破坏据点
	"""
	def __init__( self ):
		ActIntf.__init__( self )
		self.activity = csdefine.CAMP_ACT_DESTROY_BASE
	
	def _notify( self ):
		"""
		活动广播
		"""
		dict = self.getBroadMsgDict( cschannel_msgs.CAMP_ACT_DESTROY_BASE )
		Love3.g_baseApp.campActivity_broadcast( dict, [] )
	
	def start( self, mgr ):
		"""
		活动开启
		"""
		ActIntf.start( self, mgr )
		mgr.spawnMonster( self.openSpaces, self.attrCamp )
		mgr.campLocationMgr.resertAllLocation()

class ActObtainPoint( ActIntf ):
	"""
	获得积分
	"""
	def __init__( self ):
		ActIntf.__init__( self )
		self.activity = csdefine.CAMP_ACT_OBTAIN_POINT
	
	def _notify( self ):
		"""
		活动广播
		"""
		dict = self.getBroadMsgDict( cschannel_msgs.CAMP_ACT_OBTAIN_POINT )
		Love3.g_baseApp.campActivity_broadcast( dict, [] )
	
	def start( self, mgr ):
		"""
		活动开启
		"""
		ActIntf.start( self, mgr )
		mgr.spawnMonster( self.openSpaces, self.attrCamp )
		
class ActKillBoss( ActIntf ):
	"""
	击杀Boss
	"""
	def __init__( self ):
		ActIntf.__init__( self )
		self.activity = csdefine.CAMP_ACT_KILL_BOSS
	
	def _notify( self ):
		"""
		活动广播
		"""
		dict = self.getBroadMsgDict( cschannel_msgs.CAMP_ACT_KILL_BOSS )
		Love3.g_baseApp.campActivity_broadcast( dict, [] )
	
	def start( self, mgr ):
		"""
		活动开启
		"""
		ActIntf.start( self, mgr )
		mgr.spawnMonster( self.openSpaces, self.attrCamp )
		mgr.campLocationMgr.resertAllLocation()

class ActOccuptBase( ActIntf ):
	"""
	攻占据点
	"""
	def __init__( self ):
		ActIntf.__init__( self )
		self.activity = csdefine.CAMP_ACT_OCCUPY_BASE
	
	def _notify( self ):
		"""
		活动广播
		"""
		dict = self.getBroadMsgDict( cschannel_msgs.CAMP_ACT_OCCUPY_BASE )
		Love3.g_baseApp.campActivity_broadcast( dict, [] )
	
	def getBroadMsgDict( self, msg ):
		"""
		区分阵营生成地图寻路坐标
		"""
		d_spaceStr = ""
		t_spaceStr = ""
		for spaceName in self.openSpaces:
			pos = self.getDemonPos( spaceName )
			markStr = self.getMarkStr( spaceName, pos )
			d_spaceStr += markStr + ","
			
			pos = self.getTaoismPos( spaceName )
			markStr = self.getMarkStr( spaceName, pos )
			t_spaceStr += markStr + ","
			
		dict = { csdefine.ENTITY_CAMP_DEMON : msg % ( d_spaceStr[0:-1], d_spaceStr[0:-1] ),\
				 csdefine.ENTITY_CAMP_TAOISM : msg % ( t_spaceStr[0:-1], t_spaceStr[0:-1] ) }
		return dict
	
	def start( self, mgr ):
		"""
		活动开启
		"""
		ActIntf.start( self, mgr )
		mgr.spawnMonster( self.openSpaces, self.attrCamp )
		mgr.campLocationMgr.resertAllLocation()
		
class ActIntercept( ActIntf ):
	"""
	拦截支援部队
	"""
	def __init__( self ):
		ActIntf.__init__( self )
		self.activity = csdefine.CAMP_ACT_INTERCEPT_HELPER
	
	def _notify( self ):
		"""
		活动广播
		"""
		dict = self.getBroadMsgDict( cschannel_msgs.CAMP_ACT_INTERCEPT_HELPER )
		Love3.g_baseApp.campActivity_broadcast( dict, [] )
	
	def start( self, mgr ):
		"""
		活动开启
		"""
		ActIntf.start( self, mgr )
		mgr.spawnMonster( self.openSpaces, self.attrCamp )

class ActLittleWar( ActIntf ):
	"""
	小攻防
	"""
	def __init__( self ):
		ActIntf.__init__( self )
		self.activity = csdefine.CAMP_ACT_LITTLE_WAR
		
	def init( self, mgr, spaces, camp , activityTime ):
		ActIntf.init( self, mgr, spaces, camp , activityTime )
		if camp == 0:
			self.attrCamp = random.choice( [ csdefine.ENTITY_CAMP_TAOISM, csdefine.ENTITY_CAMP_DEMON ] )
		else:
			self.attrCamp = camp
		
	def _notify( self ):
		"""
		活动广播
		"""
		msg = ""
		if self.attrCamp == csdefine.ENTITY_CAMP_TAOISM:
			msg = cschannel_msgs.CAMP_ACT_LITTLE_WAR
		elif self.attrCamp == csdefine.ENTITY_CAMP_DEMON:
			msg = cschannel_msgs.CAMP_ACT_LITTLE_WAR_1
		
		dict = self.getBroadMsgDict( msg )
		Love3.g_baseApp.campActivity_broadcast( dict, [] )
	
	def getBroadMsgDict( self, msg ):
		"""
		区分阵营生成地图寻路坐标
		"""
		d_spaceStr = ""
		t_spaceStr = ""
		for spaceName in self.openSpaces:
			pos = self.getDemonPos( spaceName )
			markStr = self.getMarkStr( spaceName, pos )
			d_spaceStr += markStr + ","
			
			pos = self.getTaoismPos( spaceName )
			markStr = self.getMarkStr( spaceName, pos )
			t_spaceStr += markStr + ","
		dict = { csdefine.ENTITY_CAMP_DEMON : msg % ( d_spaceStr[0:-1], d_spaceStr[0:-1] ),\
				 csdefine.ENTITY_CAMP_TAOISM : msg % ( t_spaceStr[0:-1], t_spaceStr[0:-1] ) }
		return dict
	
	def start( self, mgr ):
		"""
		活动开启
		"""
		ActIntf.start( self, mgr )
		mgr.spawnMonster( self.openSpaces, self.attrCamp )
		mgr.campLocationMgr.resertAllLocation()


class ActBigWar( ActIntf ):
	"""
	全面战争
	"""
	def __init__( self ):
		ActIntf.__init__( self )
		self.activity = csdefine.CAMP_ACT_BIG_WAR

	def _notify( self ):
		"""
		活动广播
		"""
		dict = self.getBroadMsgDict( cschannel_msgs.CAMP_ACT_BIG_WAR )
		Love3.g_baseApp.campActivity_broadcast( dict, [] )
	
	def start( self, mgr ):
		"""
		活动开启
		"""
		ActIntf.start( self, mgr )
		mgr.spawnMonster( self.openSpaces, self.attrCamp )
		mgr.campLocationMgr.resertAllLocation()


CAMP_ACTIVITY_CONTROL = {
		csdefine.CAMP_ACT_DESTROY_BASE		:	ActDesBase,
		csdefine.CAMP_ACT_OBTAIN_POINT		:	ActObtainPoint,
		csdefine.CAMP_ACT_KILL_BOSS			:	ActKillBoss,
		csdefine.CAMP_ACT_OCCUPY_BASE		:	ActOccuptBase,
		csdefine.CAMP_ACT_INTERCEPT_HELPER	:	ActIntercept,
		csdefine.CAMP_ACT_LITTLE_WAR		:	ActLittleWar,
		csdefine.CAMP_ACT_BIG_WAR			:	ActBigWar,
}

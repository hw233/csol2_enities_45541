# -*- coding: gb18030 -*-
#
# $Id: SpaceNormal.py,v 1.49 2008-08-20 01:22:17 zhangyuxing Exp $

"""
"""
import BigWorld
import random
import Language
import Love3
import csdefine
import csconst
import time
from Resource.DialogManager import DialogManager
from bwdebug import *
from interface.GameObject import GameObject

class SpaceNormal( GameObject ):
	"""
	用于控制SpaceNormal entity的脚本，所有有需要的SpaceNormal方法都会调用此脚本(或继承于此脚本的脚本)的接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		# register to BigWorld.cellAppData
		BigWorld.cellAppData["spaceID.%i" % self.spaceID] = self.base
		
		super( SpaceNormal, self ).__init__()
		# 设置ENTITY类型
		self.setEntityType( csdefine.ENTITY_TYPE_SPACE_ENTITY )
		# 记录创建时间
		self.createdTime = time.time()
		
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_KEY, self.className )
		if len(self.dirmapping):
			BigWorld.addSpaceGeometryMapping( self.spaceID, None, self.dirmapping )
		else:
			WARNING_MSG( "space %s has no geometry mapping." % (self.className) )

		# 城市税率
		if BigWorld.globalData.has_key( self.className + ".revenueRate" ):
			revenueRate = BigWorld.globalData[ self.className + ".revenueRate" ]
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CITY_REVENUE, revenueRate )

		space_type = self.getScript().getSpaceType()
		space_timeOfDay = self.getScript().getTimeOfDay()
		space_canPk = self.getScript().canPk
		space_canQieCuo = self.getScript().canQieCuo
		space_canConjureEidolon = self.getScript().canConjureEidolon
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY, space_type )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_NUMBER, self.spaceNumber )
		if space_canPk != True : # 如果不能PK，则标记
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CANNOTPK, 1 )
		if space_canQieCuo != True : # 如果不能切磋，则标记
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CANNOTQIECUO, 1 )
		if space_canConjureEidolon != True : # 如果不能召唤小精灵，则标记
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CANNOTCONJUREEIDOLON, 1 )
		BigWorld.setSpaceTimeOfDay( self.spaceID, space_timeOfDay, 0 )

		# 将是否可以飞行填入space data，方便客户端使用
		canFly = self.getScript().canFly
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CAN_FLY, str( canFly ) )

		# 将是否可以召唤骑宠填入space data，方便客户端使用
		canVehicle = self.getScript().canVehicle
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_CAN_VEHICLE, str( canVehicle ) )

		# 将空间外接体的对角顶点填入space data, 方便客户端使用（虽然目前的实现中没有使用）
		minBBox = self.getScript().minBBox
		maxBBox = self.getScript().maxBBox
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_MIN_BBOX, str( minBBox ) )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_MAX_BBOX, str( maxBBox ) )

		# 地图死亡深度保存到space data
		deathDepth = self.getScript().deathDepth
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_DEATH_DEPTH, str( deathDepth ) )

		# 昌平镖局和兴隆镖局运镖积分初始化
		pointDict = {csdefine.ROLE_FLAG_XL_DARTING:csconst.DART_INITIAL_POINT,csdefine.ROLE_FLAG_CP_DARTING:csconst.DART_INITIAL_POINT}
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_DART_POINT, str( pointDict ) )

		# 注：以下代码当前没有使用，而是使用的上面"spaceID.%i"的方式代替，
		#     留下此代码主要是起到以后借鉴的作用。
		# 写入space entity自身的basemailbox数据到space data中,
		# 这样任何entity都能在任何地方获得它当前space的basemailbox( 理论而言 )
		#BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_MAILBOX, cPickle.dumps( self.base, 2 ) )

		# 通知base自身的spaceID
		# 用于SpaceFace::cell::teleportToSpace()判断目标地图与源地图是否是同一地图。
		self.base.onGetSpaceID( self.spaceID )

		self.RestoreTimeRatio()

	# Restore time ratio
	def RestoreTimeRatio(self):
		"""
         恢复系统时间比例，或者暂停系统时间的流逝
	    """
		if self.timeon == 1: # time on ok; currently ratio = 2:24
			#BigWorld.setSpaceTimeOfDay(self.spaceID, BigWorld.time(), 12)
			pass
		elif self.timeon == 0: # else, stop time
			#BigWorld.setSpaceTimeOfDay(self.spaceID, BigWorld.time(), 0)
			pass

	# time on/off
	def switchTime(self, value):
		"""
		打开/暂停系统时间
		@param value:	标识打开/关闭
		@type value:	UINT
		"""
		if value == 1 or value == 0:
			self.timeon = value
			self.RestoreTimeRatio()


	def onDestroy( self ):
		"""
		cell 被删除时发生
		"""
		self.getScript().onSpaceDestroy( self )
		# deregister to BigWorld.cellAppData
		self.destroySpace()
		del BigWorld.cellAppData["spaceID.%i" % self.spaceID]

	def onTimer( self, id, userArg ):
		"""
		覆盖底层的onTimer()处理机制
		"""
		self.getScript().onTimer( self, id, userArg )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		INFO_MSG( self.className, self.spaceID, params[ "databaseID" ], params[ "playerName" ] )
		self.getScript().onEnter( self, baseMailbox, params )

	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		INFO_MSG( self.className, self.spaceID, params[ "databaseID" ], params[ "playerName" ] )
		self.getScript().onLeave( self, baseMailbox, params )

	def onTeleportReady( self, baseMailbox ):
		"""
		define method
		此接口用于通知角色加载地图完毕，可以移动了，可以正常和其他游戏内容交流。
		@param baseMailbox: 要离开此space的entity mailbox
		"""
		self.getScript().onTeleportReady( self, baseMailbox )

	def timeFromCreated( self ) :
		"""
		获取从创建到调用此方法的时间
		"""
		return time.time() - self.createdTime


#
# $Log: not supported by cvs2svn $
# Revision 1.48  2008/07/23 03:13:55  kebiao
# add:spaceType
#
# Revision 1.47  2007/12/26 09:03:38  phw
# method modified: __init__(), 去掉了self.getScript().initEntity( self ),原因是底层 GameObject 就已经做了
#
# Revision 1.46  2007/10/03 07:39:27  phw
# 代码整理
# method removed:
#     _createTransport(), 移到ObjectScripts/Space.py
#     _createDoor(), 移到ObjectScripts/Space.py
#     registerPlayer(), 只有SpaceCopy才有存在此方法的必要
#     unregisterPlayer(), 只有SpaceCopy才有存在此方法的必要
#
# Revision 1.45  2007/09/29 05:56:12  phw
# 修改了registerPlayer(), unregisterPlayer()方法的实现方式；
# 修改onEnter(), onLeave()方法的参数cellMailbox为baseMailbox
#
# Revision 1.44  2007/09/24 08:30:30  kebiao
# add:onTimer
#
# Revision 1.43  2007/09/22 09:04:08  kebiao
# 重新调整了设计
#
#
#
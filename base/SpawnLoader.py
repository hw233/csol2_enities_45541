# -*- coding: gb18030 -*-

"""
# ------------------------------------------------------------------------
# space spawn的处理队列
# 设计思想：当一个space创建完成了以后就向该space的SpawnLoader(当前类)
#           注册(调用registerSpace())，SpawnLoader把它排到队列中，当轮到该
#           space创建entity时则调用该spaceEntity的createSpawnPoint()方法。
# 问：为什么不直接在每个spaceEntity创建时自己决定创建entity？
# 答：由于一个baseapp可能会同时创建多个space，如果每个space同时创建entity，
#     那么只能允许每个space每秒同时创建少量的（如10个）entity，否则该baseapp
#     的entityID分配跟不上速度则会出错；
# 问：为什么需要space每秒创建大量的entity，每个只创建10个会有什么问题：
# 答：如果每秒只创建10个entity，那么，当玩家进入副本的时候，该副本可能需要很
#     长时间才能把entity创建完，这样当玩家刚进入副本时可能会什么都看不到。
#     因此，我们需要同时创建更多的entity来使创建时间尽量减少。至于怎么处理
#     多个副本同时创建的问题，我想这个需要多方面调控，如副本的entity数量少些，
#     以期让创建速度加快，或在不同的baseapp里创建副本。
# 问：为什么不放在spaceManager中，而是放在每个baseapp中？
# 答：这样做的好处是每个baseapp都可以同时创建自己服务器上的space的entity，
#     以达到分流的目的。
# ------------------------------------------------------------------------
"""
import Language
import BigWorld
from bwdebug import *
from Function import Functor
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnLoader( BigWorld.Base ):
	"""
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )

		self.spaceInfo 			= []
		self.spawnTimerID 			= 0

	def registerSpace( self, spaceEntity ):
		"""
		define method
		"""
		self.spaceInfo.append(  spaceEntity )
		self.startSpawnEntity()

	def startSpawnEntity( self ):
		"""
		"""
		if self.spawnTimerID == 0:
			INFO_MSG( "Start spawn entity." )
			self.spawnTimerID = self.addTimer( 1, 0.1 )			#以服务器的一个tick 0.1秒为周期进行刷挂

	# -----------------------------------------------------------------
	# 回调函数
	# -----------------------------------------------------------------
	def onTimer( self, timerID, userData ):
		"""
		使用回调创建spawnPoint
		"""
		if self.spawnTimerID != timerID:
			ERROR_MSG( "Space spawn timer was be change! please check!!"  )
			return
		
		if len( self.spaceInfo ) == 0:
			self.delTimer( timerID )
			self.spawnTimerID = 0
			return
		
		spaceEntity = self.spaceInfo[0]

		try:
			if not spaceEntity.createSpawnPoint():
				self.spaceInfo.pop( 0 )
		except:
			EXCEHOOK_MSG( "Space (entity className = %s) createSpawnPoint error." % ( spaceEntity.className ) )
			self.spaceInfo.pop( 0 )

# SpawnLoader.py

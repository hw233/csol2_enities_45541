# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import Const

NEXT_CONTENT			= 999				#下一个内容的timerArg

WAIT 					= 10				#等待一会刷怪
END_WAIT 				= 60				#1分钟后离开场景
"""
类 CopyContent， 描述的是副本的一项内容。

这里把副本组成分成多项内容。

这些内容，按照顺序一个个的执行，则副本完成。

"""

class CopyContent:
	"""
	副本内容
	"""
	def __init__( self ):
		"""
		"""
		self.key = ""												#一个内容关联的 临时 属性的 "key"
		self.val = 0												#临时属性需要达到 val 的值，这个内容才结束。
	
	def beginContent( self, spaceEntity ):
		"""
		内容开始
		"""
		pass
	
	def onContent( self, spaceEntity ):
		"""
		内容执行
		"""
		pass
	
	def doContent( self, spaceEntity ):
		"""
		"""
		self.beginContent( spaceEntity )
		self.onContent( spaceEntity )
	
	def onConditionChange( self, spaceEntity, params ):
		"""
		一个条件发生变化，通知内容
		"""
		if not self.doConditionChange( spaceEntity, params ):
			return
		keyVal = spaceEntity.queryTemp( self.key, 0 )
		keyVal += 1
		spaceEntity.setTemp( self.key, keyVal )
		if keyVal >= self.val:
			self.endContent( spaceEntity )
	
	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		return True

	def endContent( self, spaceEntity ):
		"""
		内容结束
		"""
		spaceEntity.getScript().doNextContent( spaceEntity )
	
	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色进入
		"""
		pass
	
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		pass
	
	def onTeleportReady( self, spaceEntity, baseMailbox ):
		"""
		内容期间，角色进入而且client地图加载完毕,可以开始游戏内容方面的正常交互
		"""
		pass


	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		if userArg == NEXT_CONTENT:
			spaceEntity.getScript().onConditionChange( spaceEntity, { "reason": "timeOver" } )
		
		
		elif userArg == Const.SPACE_TIMER_ARG_CLOSE:
			spaceEntity.base.closeSpace( True )
			
		elif userArg == Const.SPACE_TIMER_ARG_KICK:
			spaceEntity.getScript().kickAllPlayer( spaceEntity )



class CCKickPlayersProcess( CopyContent ):
	"""
	#把所有副本玩家踢出去,副本结束
	"""
	def __init__( self ):
		"""
		"""
		self.key = "closeProcess"
		self.val = 0
	
	def onContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()
				
		spaceEntity.addTimer( 10, 0, Const.SPACE_TIMER_ARG_CLOSE )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		return False


class CCWait( CopyContent ):
	"""
	#等待
	"""
	def __init__( self ):
		"""
		"""
		self.key = "wait"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( WAIT, 0, NEXT_CONTENT )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		return "reason" in params and params["reason"] == "timeOver"


class CCEndWait( CopyContent ):
	"""
	#等待
	"""
	def __init__( self ):
		"""
		"""
		self.key = "endWait"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.client.onStatusMessage( csstatus.SPACE_WILL_BE_CLOSED, "" )
		spaceEntity.addTimer( END_WAIT, 0, NEXT_CONTENT )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		return "reason" in params and params["reason"] == "timeOver"
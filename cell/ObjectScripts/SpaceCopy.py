# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.3 2007-10-07 07:23:49 phw Exp $

"""
"""
import BigWorld
import csstatus
import Const
from bwdebug import *
from Space import Space

class SpaceCopy( Space ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Space.__init__( self )
		
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		Space.load( self, section )
		
		#spaceSec = section["Space"]

	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		"""
		#如果条件  packedDomainDataInTo 在写脚本时就应该对应上相关条件
		级别大月10，
		params = self.packedDataInTo( player )
		if params[ "level" ] < 10:
			return csstatus.SPACE_MISS_LEVELLACK
		在某队伍
		if not entity.getTeamMailbox():
			return csstatus.SPACE_MISS_NOTTEAM
		军团判断
		if not entity.corpsID:
			return csstatus.SPACE_MISS_NOTCORPS
		物品判断
		for name, bag in entity.kitbags.items():
			if bag.find2All( self.__itemName ):
				if self.val == self.__itemName:
					return csstatus.SPACE_OK
		return csstatus.SPACE_MISS_NOTITEM
		"""
		return csstatus.SPACE_OK
		
	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		params = Space.packedDomainData( self, entity )
		params[ 'dbID' ] = entity.databaseID
		params[ 'spaceKey' ] = entity.databaseID
		return params
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		pickDict = Space.packedSpaceDataOnEnter( self, entity )
		pickDict[ "isViewer" ] = entity.spaveViewerIsViewer()
		return pickDict
		
	def packedSpaceDataOnLeave( self, entity ):
		"""
		获取entity离开时，向所在的space发送离开该space消息的额外参数；
		@param entity: 想要向space entity发送离开该space消息(onLeave())的entity（通常为玩家）
		@return: dict，返回要离开的space所需要的entity数据。如，有些space可能会需要比较离开的玩家名字与当前记录的玩家的名字，这里就需要返回玩家的playerName属性
		"""
		pickDict = Space.packedSpaceDataOnLeave( self, entity )
		pickDict[ "isViewer" ] = entity.spaveViewerIsViewer()
		return pickDict
	
	def onEnterViewer( self, selfEntity, baseMailbox, params ):
		# 以观察者的身份进入副本
		pass
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		# 以正常的方式进入副本
		Space.onEnter( self, selfEntity, baseMailbox, params )
		if params[ "databaseID" ] not in selfEntity._enterRecord:
			selfEntity._enterRecord.append( params[ "databaseID" ] )
		
	def onLeaveViewer( self, selfEntity, baseMailbox, params ):
		# 以观察者的身份退出副本
		pass
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		# 以正常的方式退出副本
		playerEntity = BigWorld.entities.get( baseMailbox.id )
		if playerEntity:
			if playerEntity.queryTemp( 'leaveSpaceTime'):
				playerEntity.removeTemp( 'leaveSpaceTime')
			if playerEntity.leaveTeamTimer != 0:
				playerEntity.cancel( playerEntity.leaveTeamTimer )
				playerEntity.leaveTeamTimer = 0
		Space.onLeave( self, selfEntity, baseMailbox, params )

	def onConditionChange( self, params  ):
		"""
		define method
		用于副本的事件变化通知。
		副本的事件变化可以是多个变化构成一个内容的完成，也可以是一个。
		"""
		pass

	def eventHandle( self, selfEntity, eventID, params ):
		"""
		处理副本中的事件
		"""
		pass
	
	def isViewer( self, params ):
		# 判断当前进入玩家是否是观察者
		if params.get( "isViewer", False ):
			return True
			
		return False

	def onSpaceDestroy( self, selfEntity ):
		"""
		当space entity的onDestroy()方法被调用时触发此接口；
		在此我们可以处理一些事情，如把记录下来的玩家全部传送到指定位置等；
		"""
		for e in selfEntity.spaceViewers:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()
				
		Space.onSpaceDestroy( self, selfEntity )
	
	def nofityTeamDestroy( self, selfEntity, teamEntityID ):
		"""
		队伍解散
		"""
		pass
	
	def closeCopy( self, selfEntity, userArg = 0 ):
		"""
		副本关闭
		"""
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
		
		selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
	
	def kickAllPlayer( self, selfEntity ):
		"""
		将副本所有玩家踢出
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == Const.SPACE_TIMER_ARG_CLOSE:
			selfEntity.base.closeSpace( True )		# 关闭副本
		
		elif userArg == Const.SPACE_TIMER_ARG_KICK:
			self.kickAllPlayer( selfEntity )
		else:
			Space.onTimer( self, selfEntity, id, userArg )

	def onEntitySpaceGone( self, entity ):
		"""
		called when the space this entity is in wants to shut down. 
		"""
		Space.onEntitySpaceGone( self, entity )
		try:
			entity.spawnMB = None
		except:
			WARNING_MSG( " Entity %s ,id %i has now attribute 'SpawnMB' " % ( entity, entity.id  ) )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/10/03 07:42:22  phw
# 代码整理，转移一些代码到entity SpaceCopy中
#
# Revision 1.1  2007/09/29 05:59:57  phw
# no message
#
# Revision 1.2  2007/09/24 08:30:17  kebiao
# add:onTimer
#
# Revision 1.1  2007/09/22 09:09:19  kebiao
# space脚本基础类
#
# 
#

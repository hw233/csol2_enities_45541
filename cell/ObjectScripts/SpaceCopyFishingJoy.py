# -*- coding:gb18030 -*-

from SpaceMultiLine import SpaceMultiLine
from bwdebug import *
import Const


class SpaceCopyFishingJoy( SpaceMultiLine ):
	def __init__( self ):
		SpaceMultiLine.__init__( self )
	
	def onEnter( self, selfEntity, baseMailbox, params ):
		SpaceMultiLine.onEnter( self, selfEntity, baseMailbox, params )
		BigWorld.globalData["FishingJoyMgr"].enterRoom( params["playerName"], baseMailbox, selfEntity.id )
		
	def onLeave( self, selfEntity, baseMailbox, params ):
		SpaceMultiLine.onLeave( self, selfEntity, baseMailbox, params )
		BigWorld.globalData["FishingJoyMgr"].leaveRoom( baseMailbox.id )
		
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		pickDict = SpaceMultiLine.packedSpaceDataOnEnter( self, entity )
		pickDict[ "playerName" ] = entity.getName()
		return pickDict
# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.3 2007-10-07 07:23:49 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import csconst
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyFirstMap( SpaceCopy ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )

	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		enterID = entity.queryTemp( "lineNumber", -1 )
		if enterID != -1:
			return { "spaceKey" : enterID }

		spaceLabel = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if spaceLabel == "xin_ban_xin_shou_cun":
			lineNumber = BigWorld.getSpaceDataFirstForKey( entity.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER )
			return { "spaceKey" : int(lineNumber) }
		return {}

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		lineNumber = selfEntity.params[ "lineNumber" ]
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER, lineNumber )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		selfEntity.base.onEnter( baseMailbox, params )
		func = getattr( baseMailbox.cell, "recordLastSpaceLineNumber" )
		if func:
			func( selfEntity.params[ "lineNumber" ] )
		SpaceCopy.onEnter( self, selfEntity, baseMailbox, params )

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		selfEntity.base.onLeave( baseMailbox, params )
		SpaceCopy.onLeave( self, selfEntity, baseMailbox, params )

#
# $Log: not supported by cvs2svn $
#

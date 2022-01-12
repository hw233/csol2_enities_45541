# -*- coding: gb18030 -*-
#
# $Id: SpaceNormal.py,v 1.49 2008-08-20 01:22:17 kebiao Exp $

"""
"""
import BigWorld
import random
import Language
import Love3
import csdefine
import csconst
from bwdebug import *
from SpaceNormal import SpaceNormal

class SpaceMultiLine( SpaceNormal ):
	"""
	用于控制SpaceNormal entity的脚本，所有有需要的SpaceNormal方法都会调用此脚本(或继承于此脚本的脚本)的接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceNormal.__init__( self )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER, self.getLineNumber() )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_MAX_LINE_NUMBER, self.getScript().maxLine )
		
	def getLineNumber( self ):
		"""
		获得自身的线数编号
		"""
		return self.params[ "lineNumber" ]
		
	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
	
		self.base.onEnter( baseMailbox, params )
		SpaceNormal.onEnter( self, baseMailbox, params )
		
		entity = BigWorld.entities.get( baseMailbox.id )
		if not entity:
			entity = baseMailbox.cell
			
		func = getattr( entity, "recordLastSpaceLineData" )
		if func:
			func( self.getLineNumber(), self.getScript().maxLine )

	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		self.base.onLeave( baseMailbox, params )
		SpaceNormal.onLeave( self, baseMailbox, params )
				
#
# $Log: not supported by cvs2svn $
#
#
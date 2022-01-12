# -*- coding: gb18030 -*-

# 60 级剧情副本
# by hezhiming

# bigworld
import BigWorld
# common
import csdefine
from bwdebug import *
# cell
from SpaceCopy import SpaceCopy


class SpaceCopyPlotLv60( SpaceCopy ) :
	def __init__( self ):
		SpaceCopy.__init__( self )

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity :
			INFO_MSG( "%s enter copy plot lv60." % entity.getName() )
		else :
			INFO_MSG( "Something enter copy plot lv60." )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity :
			INFO_MSG( "%s leave copy plot lv60." % entity.getName() )
		else :
			INFO_MSG( "Something leave copy plot lv60." )

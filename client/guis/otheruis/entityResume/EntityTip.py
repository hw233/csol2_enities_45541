# -*- coding: gb18030 -*-
#
# $Id: EntityTip.py,v 1.1 2008-08-21 09:02:39 huangyongwei Exp $

"""
implement tips window( 用以显示 entity 信息)

-- 2008/08/12 : writen by huangyongwei
"""

import BigWorld
from guis import *
from guis.common.Frame import HVFrame
from guis.tooluis.CSRichText import CSRichText

class EntityTip( HVFrame ) :
	__cc_fade_speed			= 0.5									# 渐隐延时
	__cc_edge_width			= 8.0									# 边宽

	def __init__( self ) :
		wnd = GUI.load( "guis/tooluis/infotip/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		HVFrame.__init__( self, wnd )
		self.focus = False
		self.moveFocus = False
		self.__initialize( wnd )
		wnd.visible = False
		GUI.addRoot( wnd )

		self.__fadeDelayCBID = 0

	def __del__( self ) :
		if Debug.output_del_InfoTip :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, wnd ) :
		self.__fader = wnd.fader
		self.__fader.value = 0
		self.__fader.speed = self.__cc_fade_speed

		self.__pyRich = CSRichText()
		self.__pyRich.maxWidth = 300.0
		self.addPyChild( self.__pyRich )
		self.__pyRich.left = self.__cc_edge_width
		self.__pyRich.top = self.__cc_edge_width


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layout( self ) :
		"""
		设置窗口适应文本大小
		"""
		self.width = self.__pyRich.right + self.__cc_edge_width
		self.height = self.__pyRich.bottom + self.__cc_edge_width


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, text ) :
		"""
		显示工具提示
		"""
		BigWorld.cancelCallback( self.__fadeDelayCBID )
		self.__pyRich.text = text
		self.__layout()
		self.__fader.value = 1.0
		self.visible = True

	def hide( self ) :
		"""
		隐藏 tooltip
		"""
		BigWorld.cancelCallback( self.__fadeDelayCBID )
		self.__fader.value = 0.0
		def delayHide() :
			self.visible = False
			self.__pyRich.clear()
		self.__fadeDelayCBID = BigWorld.callback( self.__fader.speed, delayHide )

# -*- coding: gb18030 -*-
#
# $Id: ToolTip.py,v 1.3 2008-08-26 02:21:39 huangyongwei Exp $

"""
implement tooltip window
－－TipWindow 的特化，因此 ToolTip 可以实现的 TipWindow 也可以实现，只是 ToolTip 的数据结构更加简单

-- 2008/08/12 : writen by huangyongwei
"""

import BigWorld
from guis import *
from guis.tooluis.CSRichText import CSRichText
from TipWindow import TipWindow

class ToolTip( TipWindow ) :
	__cc_max_width = 300.0								# 最大宽度（超过该宽度将会自动换行）

	def __init__( self ) :
		TipWindow.__init__( self )
		self.__initialize( self.getGui() )

	def __del__( self ) :
		if Debug.output_del_InfoTip :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, wnd ) :
		self.__pyRich = CSRichText()
		self.__pyRich.maxWidth = self.__cc_max_width
		self.__pyRich.widthAdapt = True					# 设置为以最大宽度的文本行作为 CSRichText 的最大宽度
		self.addPyChild( self.__pyRich )
		self.__pyRich.left = self.cc_edge_width_
		self.__pyRich.top = self.cc_edge_width_


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layout( self ) :
		"""
		设置窗口适应文本大小
		"""
		self.width = self.__pyRich.right + self.cc_edge_width_
		self.height = self.__pyRich.bottom + self.cc_edge_width_


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setText( self, text ) :
		"""
		设置提示文本
		"""
		self.__pyRich.text = text
		self.__layout()

	def clear( self ) :
		"""
		清空文本
		"""
		self.__pyRich.clear()

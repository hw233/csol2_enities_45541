# -*- coding: gb18030 -*-
#
# $Id: CSRichText.py,v 1.2 2008-04-14 10:43:07 huangyongwei Exp $

"""
implement richtext control for csol

2008.03.24: writen by huangyongwei
"""

import StringFormat
from guis import *
from guis.controls.RichText import RichText


class CSRichText( RichText ) :
	__cc_def_plugin_path = "guis/tooluis/richtext_plugins"				# 默认插件路径

	def __init__( self, panel = None, pyBinder = None ) :
		RichText.__init__( self, panel, pyBinder )
		self.setPluginsPath( self.__cc_def_plugin_path )				# 设置适合本项目用的插件路径
		self.opGBLink = False											# 是否使用默认连接操作

	def onComponentLClick_( self, pyComponent ) :
		if self.opGBLink :
			rds.hyperlinkMgr.process( self, pyComponent.linkMark )
		RichText.onComponentLClick_( self, pyComponent )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setText( self, text ) :
		if self.opGBLink :
			text = StringFormat.format( text )							# 创世相关转义
		RichText._setText( self, text )
	
	def _setText_axi( self, text ) :      								# 用于聊天面板是不转义
		RichText._setText( self, text )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( RichText._getText, _setText )
	text_axi = property( RichText._getText, _setText_axi )

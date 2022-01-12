# -*- coding: gb18030 -*-
#
# $Id: Icon.py,v 1.7 2008-06-21 01:44:43 huangyongwei Exp $

"""
implement icon class

2006.12.14: writen by huangyongwei
"""
"""
composing :
	GUI.Window
"""

from guis import *
from Control import Control

class Icon( Control ) :
	def __init__( self, icon = None, pyBinder = None ) :
		Control.__init__( self, icon, pyBinder )
		self.__initialize( icon )

	def subclass( self, icon, pyBinder = None ) :
		Control.subclass( self, icon, pyBinder )
		self.__initialize( icon )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_Icon :
			INFO_MSG( str( self ) )

	# -------------------------------------------------
	def __initialize( self, icon ) :
		if icon is None : return


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getIcon( self ) :
		return ( self.texture, self.mapping )

	def _setIcon( self, icon ) :
		isTuple = type( icon ) is tuple										# 如果赋的是 tuple
		self.texture = ( isTuple and [icon[0]] or [icon] )[0]				# 则第一个元素是图标路径
		if not isTuple or icon[1] is None :									# 第二个元素是 mapping
			self.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )
		else :
			self.mapping = icon[1]


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	icon = property( _getIcon, _setIcon )			# tuple / str : 获取/设置图标路径和 mapping：( 图标路径, mapping )，如果 mapping 默认，也可以直接用图标路径

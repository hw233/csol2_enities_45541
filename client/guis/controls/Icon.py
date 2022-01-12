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
		isTuple = type( icon ) is tuple										# ��������� tuple
		self.texture = ( isTuple and [icon[0]] or [icon] )[0]				# ���һ��Ԫ����ͼ��·��
		if not isTuple or icon[1] is None :									# �ڶ���Ԫ���� mapping
			self.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )
		else :
			self.mapping = icon[1]


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	icon = property( _getIcon, _setIcon )			# tuple / str : ��ȡ/����ͼ��·���� mapping��( ͼ��·��, mapping )����� mapping Ĭ�ϣ�Ҳ����ֱ����ͼ��·��

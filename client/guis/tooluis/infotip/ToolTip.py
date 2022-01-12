# -*- coding: gb18030 -*-
#
# $Id: ToolTip.py,v 1.3 2008-08-26 02:21:39 huangyongwei Exp $

"""
implement tooltip window
����TipWindow ���ػ������ ToolTip ����ʵ�ֵ� TipWindow Ҳ����ʵ�֣�ֻ�� ToolTip �����ݽṹ���Ӽ�

-- 2008/08/12 : writen by huangyongwei
"""

import BigWorld
from guis import *
from guis.tooluis.CSRichText import CSRichText
from TipWindow import TipWindow

class ToolTip( TipWindow ) :
	__cc_max_width = 300.0								# ����ȣ������ÿ�Ƚ����Զ����У�

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
		self.__pyRich.widthAdapt = True					# ����Ϊ������ȵ��ı�����Ϊ CSRichText �������
		self.addPyChild( self.__pyRich )
		self.__pyRich.left = self.cc_edge_width_
		self.__pyRich.top = self.cc_edge_width_


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layout( self ) :
		"""
		���ô�����Ӧ�ı���С
		"""
		self.width = self.__pyRich.right + self.cc_edge_width_
		self.height = self.__pyRich.bottom + self.cc_edge_width_


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setText( self, text ) :
		"""
		������ʾ�ı�
		"""
		self.__pyRich.text = text
		self.__layout()

	def clear( self ) :
		"""
		����ı�
		"""
		self.__pyRich.clear()

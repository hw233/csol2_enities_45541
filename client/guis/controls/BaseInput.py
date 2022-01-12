# -*- coding: gb18030 -*-
#
# $Id: BaseInput.py,v 1.19 2008-06-21 01:48:39 huangyongwei Exp $

"""
implement textbox class
2007/09/8 : writen by huangyongwei
"""

from AbstractTemplates import AbstractClass
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Cursor import Cursor
from Control import Control


class BaseInput( AbstractClass, Control ) :
	__abstract_methods = set()								# ���Ϊ������

	def __init__( self, inputBox, pyBinder = None ) :
		Control.__init__( self, inputBox, pyBinder )
		self.pyCursor_ = Cursor()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTabIn_( self ) :
		"""
		set focus
		"""
		self.showCursor_()
		Control.onTabIn_( self )

	def onTabOut_( self ) :
		"""
		release focus
		"""
		self.hideCursor_()										# hide cursor
		Control.onTabOut_( self )

	# -------------------------------------------------
	def showCursor_( self ) :
		self.pyCursor_.cap( self )

	def hideCursor_( self ) :
		self.pyCursor_.uncap( self )

	# -------------------------------------------------
	def isAllowInput_( self ) :
		"""
		indicate weather allow input
		"""
		if self.pyCursor_.capped( self ) :
			return self.tabStop
		return False

	def keyInput_( self, key, mods ) :
		pass

	# -------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if Control.onKeyDown_( self, key, mods ) :
			return True
		if self.isAllowInput_() :
			return self.keyInput_( key, mods )		# ��Ϣ�Ƿ�����ػ�
		return False

	def onLMouseDown_( self, mods ) :
		Control.onLMouseDown_( self, mods )
		self.tabStop = True
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def notifyInput( self, text ) :
		pass

	# -------------------------------------------------
	@staticmethod
	def getLeftWordEnd( wtext ) :
		"""
		��ȡ�ַ�������ߵ�һ�����ʵĽ���λ��
		"""
		segTexts = wtext.split( " " )
		count = 0
		while len( segTexts ) :
			segText = segTexts.pop( 0 )
			if len( segText ) == 0 :
				count += 1
			elif count :
				break
			else :
				count += len( segText ) + 1
		return count

	@staticmethod
	def getRightWordStart( wtext ) :
		"""
		��ȡ�ַ������ұ�һ�����ʵ���ʼλ��
		"""
		segTexts = wtext.split( " " )
		count = len( wtext )
		while len( segTexts ) :
			segText = segTexts.pop()
			if len( segText ) == 0 :
				count -= 1
			else :
				count -= len( segText )
				break
		return max( 0, count )


	# ----------------------------------------------------------------
	# add abstarct methods
	# ----------------------------------------------------------------
	__abstract_methods.add( keyInput_ )
	__abstract_methods.add( notifyInput )

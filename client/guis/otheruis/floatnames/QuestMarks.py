# -*- coding: gb18030 -*-
#
# $Id: NPCName.py,v 1.14 2008-05-29 05:44:12 huangyongwei Exp $

"""
implement float name of the character
2009.02.13 : writen huangyongwei
"""

from cscollections import MapList
from guis import *
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.PyGUI import PyGUI

class QuestMarks( GUIBaseObject ) :
	def __init__( self, bg ) :
		GUIBaseObject.__init__( self, bg )
		self.__pyMarks = MapList()
		self.__pyMarks["normalStart"] = PyGUI( bg.qstStart )
		self.__pyMarks["normalFinish"] = PyGUI( bg.qstFinish )
		self.__pyMarks["normalIncomplete"] = PyGUI( bg.qstIncomplete )
		self.__pyMarks["fixloopStart"] = PyGUI( bg.qstStart_b )
		self.__pyMarks["directFinish"] = PyGUI( bg.qstFinish_b )
		self.__pyMarks["qstTalk"] = PyGUI( bg.qstTalk )
		self.__pyMarks["warnStart"] = PyGUI( bg.qstStart_w )

		for pyMark in self.__pyMarks.values() :
			pyMark.visible = False


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layout( self ) :
		left = 0
		for pyMark in self.__pyMarks.values() :
			if pyMark.visible :
				pyMark.left = left
				left = pyMark.right
		if left == 0 :
			self.visible = False
		else :
			self.width = left
			self.visible = True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def flush( self ) :
		"""
		隐藏全部标记
		"""
		for pyMark in self.__pyMarks.values() :
			pyMark.visible = False
		self.__layout()

	def showMark( self, name ) :
		"""
		显示指定标记
		"""
		if name in self.__pyMarks :
			self.__pyMarks[name].visible = True
		self.__layout()

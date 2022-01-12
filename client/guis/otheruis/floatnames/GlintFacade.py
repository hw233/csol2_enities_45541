# -*- coding: gb18030 -*-

# written by ganjinxing 2010-07-07
# 提供实现Entity头顶UI闪烁功能的接口

import GUI
import BigWorld
from Weaker import WeakList
from AbstractTemplates import Singleton

class GlintFacade( Singleton ) :

	def __init__( self ) :
		self.__pyGlitteryUI = WeakList()
		self.__alphaSd = GUI.AlphaShader()					# 所有UI共用的alphaShader
		self.__alphaSd.speed = 0.2


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def __glitter( self ) :
		"""
		开始闪烁
		"""
		if len( self.__pyGlitteryUI ) == 0 : return
		sdValue = self.__alphaSd.value
		sdValue = 0 if sdValue else 1
		self.__alphaSd.value = sdValue
		cbInterval = sdValue and 0.7 or 0.3					# 显示0.7秒，隐藏0.3秒
		BigWorld.callback( cbInterval, self.__glitter )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addPyGlitteryUI( self, pyGui ) :
		"""
		添加一个需要不停闪烁的UI
		"""
		currGlittering = len( self.__pyGlitteryUI ) > 0		# 列表中还有元素，表明还在闪烁
		if pyGui not in self.__pyGlitteryUI :
			self.__pyGlitteryUI.append( pyGui )
			pyGui.gui.addShader( self.__alphaSd )
		if not currGlittering :
			self.__glitter()

	def delPyGlitteryUI( self, pyGui ) :
		"""
		移去一个不需要再闪烁的UI
		"""
		if pyGui in self.__pyGlitteryUI :
			self.__pyGlitteryUI.remove( pyGui )
			pyGui.gui.delShader( self.__alphaSd )


glintFacade = GlintFacade()
# -*- coding: gb18030 -*-

# written by ganjinxing 2010-07-07
# �ṩʵ��Entityͷ��UI��˸���ܵĽӿ�

import GUI
import BigWorld
from Weaker import WeakList
from AbstractTemplates import Singleton

class GlintFacade( Singleton ) :

	def __init__( self ) :
		self.__pyGlitteryUI = WeakList()
		self.__alphaSd = GUI.AlphaShader()					# ����UI���õ�alphaShader
		self.__alphaSd.speed = 0.2


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def __glitter( self ) :
		"""
		��ʼ��˸
		"""
		if len( self.__pyGlitteryUI ) == 0 : return
		sdValue = self.__alphaSd.value
		sdValue = 0 if sdValue else 1
		self.__alphaSd.value = sdValue
		cbInterval = sdValue and 0.7 or 0.3					# ��ʾ0.7�룬����0.3��
		BigWorld.callback( cbInterval, self.__glitter )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addPyGlitteryUI( self, pyGui ) :
		"""
		���һ����Ҫ��ͣ��˸��UI
		"""
		currGlittering = len( self.__pyGlitteryUI ) > 0		# �б��л���Ԫ�أ�����������˸
		if pyGui not in self.__pyGlitteryUI :
			self.__pyGlitteryUI.append( pyGui )
			pyGui.gui.addShader( self.__alphaSd )
		if not currGlittering :
			self.__glitter()

	def delPyGlitteryUI( self, pyGui ) :
		"""
		��ȥһ������Ҫ����˸��UI
		"""
		if pyGui in self.__pyGlitteryUI :
			self.__pyGlitteryUI.remove( pyGui )
			pyGui.gui.delShader( self.__alphaSd )


glintFacade = GlintFacade()
# -*- coding: gb18030 -*-
#
# $Id: ItemParticle.py, huangdong Exp $
#���Ը�ITEM��ͼ������һ���µ�Ч��


from guis import *
from guis.controls.Control import Control

# --------------------------------------------------------------------
# implement item cover array
# --------------------------------------------------------------------
class ItemParticleArray :
	__inst = None

	def __init__( self ) :
		assert self.__inst is None
		self.__inst = self

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addParticle( self, pyItem, textureName, Name, posZ = 1.0) :
		"""
		����һ��Ч��
		@type				pyItem : python ui
		@param				pyItem : ������� UI
		@return					   : None
		"""
		pyItemgui = pyItem.getGui()
		pyParticle = GUI.load( "guis/tooluis/itemparticle/itemparticle.gui" )
		pyParticle.textureName = textureName
		self.resetMode( pyParticle , pyItemgui.size )
		pyItemgui.addChild( pyParticle, Name )
		s_util.setGuiPos( pyParticle, (0,0) )
		pyParticle.visible = True
		pos = pyParticle.position
		pyParticle.position = ( pos[0], pos[1], posZ )

	def resetMode( self, gui, size ) :
		"""
		���� binder ���� item �Ĺ��
		"""
		mode   = int( round( size[0] ) ), int( round( size[1] ) )
		width  = 4.0 * mode[0] / 3.0
		height = 4.0 * mode[1] / 3.0
		gui.size = width, height
		util.setGuiState( gui )
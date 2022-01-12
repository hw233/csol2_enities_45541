# -*- coding: gb18030 -*-
#
# role special sign & show formula
# written by gjx 2009-4-3
#

from bwdebug import *
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Frame import HFrame
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Image import PL_Image

sign_texture = "maps/signboard/sign_%d_%d.texanim" #对应招牌贴图，第1个编号是招牌类型，第2个编号是位置，0左，1右， 2上

pos_maps = { 0:[2],1:[1],2:[0],3:[0],4:[0,1],5:[1],6:[0,1],7:[0] }#每个类型对应的贴图位置

MINWIDTH = 160.0

class SignBoard( PyGUI ):
	def __init__( self ):
		board = GUI.load( "guis/otheruis/floatnames/signboard/board.gui" )
		uiFixer.firstLoadFix( board )
		PyGUI.__init__( self, board )
		self.__pyHBoard = BoardFrame( board.hBoard ) #名称面板
		self.__pyRtName = CSRichText( board.hBoard.rtName ) #招牌名称
		self.__pyRtName.align = "L" #名称居中
		self.__pyRtName.maxWidth = 240.0 #招牌名称不能超过20字节
		self.__sitScale = float( self.__pyHBoard.center )/ self.width

		self.__pySigns = {}
		for name, item in board.children: #左、右、上3个招牌贴图
			if name.startswith( "sign_" ):
				index = int( name.split( "_" )[1] )
				pySign = PyGUI( item )
				self.__pySigns[index] = pySign

	def setBoardName( self, name ): #设置招牌名称
		self.__pyRtName.text = PL_Font.getSource( name, fc = ( 230, 227, 185 ) )
		self.__pyHBoard.width = self.__pyRtName.width + 16.0
		self.__pyRtName.center = self.__pyHBoard.width/2.0
		self.___layout()

	def setSignNumber( self, numberStr ):
		number = int( numberStr )
		self.__clearTexure()
		if pos_maps.has_key( int( number ) ):
			poslist = pos_maps[number]
			for pos in poslist:
				if self.__pySigns.has_key( pos ):
					self.__pySigns[pos].texture = sign_texture%( number, pos ) #更新贴图
					if number in [2,4,6,7]:
						self.__pySigns[pos].size = (64, 64 )
					elif number in [0,1,3]:
						self.__pySigns[pos].size = (128, 64 )
					elif number == 5:
						self.__pySigns[pos].size = (64, 128 )
			self.___layout()

	def ___layout( self ):
		self.__pyHBoard.width = max( MINWIDTH, self.__pyRtName.width + 16.0)
		
		if self.__pySigns[0].texture != "":
			self.__pySigns[0].left = 0.0
			self.__pyHBoard.left = self.__pySigns[0].center
			self.__pySigns[0].top=0.0
			self.__pyHBoard.middle = self.__pySigns[0].middle
			if self.__pySigns[1].texture != "":
				self.width = self.__pySigns[1].right
			else:
				self.width = self.__pyHBoard.right
		if self.__pySigns[1].texture != "":
			self.__pySigns[1].top=0.0
			self.__pyHBoard.middle = self.__pySigns[1].middle
			self.height = self.__pySigns[1].bottom
			if self.__pySigns[0].texture != "":
				self.__pyHBoard.left = self.__pySigns[0].center
			else:
				self.__pyHBoard.left = 0.0
			self.__pySigns[1].center = self.__pyHBoard.right
			self.width = self.__pySigns[1].right
		if self.__pySigns[2].texture != "":
			self.__pySigns[2].top = 0.0
			self.__pyHBoard.top = self.__pySigns[2].bottom - 13.0 #贴图上下之间间隙
			self.height = self.__pyHBoard.bottom
			self.width = self.__pyHBoard.width
			self.__pySigns[2].center = self.width/2.0
		self.__pyRtName.center = self.__pyHBoard.width/2.0
		self.__sitScale = float( self.__pyHBoard.center )/ self.width

	def __clearTexure( self ):
		self.__pyHBoard.top = 0.0
		self.__pyHBoard.left = 0.0
		self.__pyRtName.left = 4.0
		self.__pyHBoard.width = max( MINWIDTH, self.__pyRtName.width ) + 16.0
		self.width = self.__pyHBoard.right
		for pySign in self.__pySigns.itervalues():
			pySign.texture = ""

	def _getCenter( self ):
		offset = self.width*( 0.5 - self.__sitScale )
		center = PyGUI._getCenter( self )
		return center - offset

	def _setCenter( self, center ):
		offset = self.width*( 0.5 - self.__sitScale )
		PyGUI._setCenter( self, center + offset )

	center = property( _getCenter, _setCenter )
	
class BoardFrame( HFrame ):

	__cc_edge = 0.5

	def __init__( self, frame = None ):
		HFrame.__init__( self, frame)
	# ----------------------------------------------------------------
	# property method
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		HFrame._setWidth( self, width )
		self.pyR_.right = width
		self.pyBg_.left = self.pyL_.right - self.__cc_edge
		self.pyBg_.width = self.pyR_.left - self.pyBg_.left
		if self.pyT_ is not None :
			self.pyT_.left = self.pyL_.right - self.__cc_edge
			self.pyB_.left = self.pyL_.right - self.__cc_edge

			self.pyT_.width = self.pyR_.left - self.pyT_.left
			self.pyB_.width = self.pyR_.left - self.pyB_.left

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HFrame._getWidth, _setWidth )
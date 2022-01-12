# -*- coding: gb18030 -*-
#
# $Id: ChartsItem.py, fangpengjun Exp $

"""
implement charts item class

"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.ODListPanel import ViewItem
from guis.controls.ListItem import ListItem
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from LabelGather import labelGather
import csconst
import Const

BG_TEXTURES = {UIState.COMMON:
			{"l": "com_%d",
			"c": "com_%d",
			"r": "com_%d"
			},
		UIState.HIGHLIGHT:
			{"l": "lightlr",
			"c": "lightc",
			"r": "lightlr"
			},
		UIState.SELECTED:
			{"l": "lightlr",
			"c": "lightc",
			"r": "lightlr"
			}
		}

ABOUTPLAYER_TEXTURE = { "l": "selectlr",
						"c": "selectc",
						"r": "selectlr"
						}

class RankItem( ListItem ):

	bg_teture_path = "guis/general/rankwindow/bars/%s.tga"

	class __SubItem( CSRichText ):
		def __init__( self, item, pyBinder ):
			CSRichText.__init__( self, item, pyBinder )
			self.focus = False
			self.crossFocus = True
			self.realText = ""
			self.showTips = False
			self.autoNewline = False
			self.align = "C"

		# ----------------------------------------------------------------
		# protected
		# ----------------------------------------------------------------
		def onMouseEnter_( self ):
			"""
			������ʱ������
			ע�⣺���ﲻҪ�ص� Lavel �� onMouseEnter_
			"""
			self.pyBinder.onMouseEnter_()
			if self.showTips: #�ж��У��򸡶�����ʾ
				toolbox.infoTip.showToolTips( self, self.realText )
			return True

		def onMouseLeave_( self ):
			"""
			����뿪ʱ������
			ע�⣺���ﲻҪ�ص� Lavel �� onMouseLeave_
			"""
			self.pyBinder.onMouseLeave_()
			toolbox.infoTip.hide()
			return True
	# ---------------------------------------------------------

	def __init__( self, item = None, pyBinder = None ):
		ListItem.__init__( self, item, pyBinder )
		self.pyCols_ = []
		self.index = -1
		self.__isAboutPlayer = False		#�Ƿ�ͽ�ɫ���
		self.selected = False
		self.__initialize( item )

	def subclass( self, item, pyBinder = None ):
		ListItem.subclass( self, item, pyBinder )
		self.__initialize( item )

	def __del__( self ) :
		ListItem.__del__( self )
		if Debug.output_del_ListItem :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item ):
		if item is None : return
		self.__initCells( item )

	def __initCells( self, item ) :
		for name, ch in item.children :
			if "col_" not in name : continue
			pyCol = RankItem.__SubItem( ch, self )
			self.pyCols_.append( pyCol )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ):
		if self.isAboutPlayer:return
		for name, child in self.getGui().children: #����״̬�滻��ͼ
			if name in ["l","c","r"]:
				if state in [UIState.HIGHLIGHT, UIState.SELECTED]:
					child.textureName = self.bg_teture_path%BG_TEXTURES[state][name]
				elif state == UIState.COMMON:
					child.textureName = self.bg_teture_path%BG_TEXTURES[state][name]%( self.index%2 ) #

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setTextes( self, *textes ):
		"""
		����ÿ��col����
		"""
		assert len( textes[0] ) == len( self.pyCols_ )
		for index, pyCol in enumerate( self.pyCols_ ) :
			textStr = str( textes[0][index] )
			cellText = PL_Font.getSource( textStr, fc = ( 255, 250, 190, 255 ) )
			pyCol.realText = cellText
			pyCol.text = cellText
			pyCol.showTips = False
			if pyCol.width > pyCol.maxWidth :
				pyCol.showTips = True
				textStr = textStr[:6]
				cellText = PL_Font.getSource( textStr, fc = ( 255, 250, 190, 255 ) )
				pyCol.text = cellText + "..."	


	def updateRankData( self, rankType, gbIndex, rankData ):
		"""
		����rankData��Ϣ
		"""
		player = BigWorld.player()
		defColor = ( 255, 250, 190, 255 )
		rankInfos = []
		familyStr = labelGather.getText( "RankWindow:main", "miNone" )
		tongStr = labelGather.getText( "RankWindow:main", "miNone" )
		NPCStr = labelGather.getText( "RankWindow:main", "miNone" )
		playerName = player.getName()
		tongName = player.tongName
		if rankData[0]:
			offsetOrder =  rankData[0]
		else:
			offsetOrder = 0
		diffColor = defColor
		diffStr = "--"
		if offsetOrder > 0:
			diffColor = ( 0, 255, 212, 255 )
			diffStr = "��%d"%offsetOrder
		elif offsetOrder < 0:
			diffColor = ( 255, 0, 0, 255 )
			diffStr = "��%d"%(0 - offsetOrder)
		else:
			diffColor = defColor
			diffStr = "--"
		diffStr = PL_Font.getSource( "%s"%diffStr, fc = diffColor )
		#�������ݿ���Ϣ��ת��Ϊ�ͻ�����ʾ��Ϣ
		if rankType == Const.LEVELRANKING: #�ȼ�����
			levelStr = PL_Font.getSource( labelGather.getText( "RankWindow:main", "miLevel", rankData[2] ), fc = defColor ) #�ȼ�
			classStr = PL_Font.getSource( "%s"%csconst.g_chs_class[int( rankData[3] )], fc = defColor ) #ְҵ
			if rankData[4] is not None:
				familyStr = rankData[4]
			if rankData[5] is not None:
				tongStr = rankData[5]
			self.isAboutPlayer = rankData[1] == playerName
			rankInfos = [diffStr, rankData[1], levelStr, classStr, tongStr]
		elif rankType == Const.MONEYRANKING: #�Ƹ�����
			money = int( rankData[2] )#��Ǯ
			moneyStr = PL_Font.getSource( utils.currencyToViewText( money ), fc = ( 255, 250, 190, 255 ) )
			if rankData[4] is not None:
				familyStr = rankData[4]
			if rankData[5] is not None:
				tongStr = rankData[5]
			self.isAboutPlayer = rankData[1] == playerName
			rankInfos = [diffStr, rankData[1], moneyStr, tongStr]
		elif rankType == Const.TONGRANKING: #���
			self.isAboutPlayer = rankData[1] == tongName
			rankInfos = [diffStr, rankData[1], rankData[2], rankData[3], rankData[4], rankData[5] ]
		else: #PK����
			levelStr = PL_Font.getSource( labelGather.getText( "RankWindow:main", "miLevel", rankData[2] ), fc = defColor ) #�ȼ�
			classStr = PL_Font.getSource( "%s"%csconst.g_chs_class[int( rankData[3] )], fc = defColor ) #ְҵ
			self.isAboutPlayer = rankData[1] == playerName
			rankInfos = [diffStr, rankData[1], levelStr, classStr, rankData[4], rankData[5]]
		indexStr = str( gbIndex + 1 )
		rankInfos.insert( 0, indexStr )
		self.setTextes( rankInfos )


	def setTongActPoit( self, index, infoList ): #
		self.isAboutPlayer = BigWorld.player().tongName == infoList[1]
		self.setTextes( [index] + infoList )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCols( self ):
		return self.pyCols_[:]

	# ---------------------------------------
	def _getAboutPlayer( self ):
		return self.__isAboutPlayer

	def _setAboutPlayer( self, aboutPlayer ):
		self.__isAboutPlayer = aboutPlayer
#		self.crossFocus = not aboutPlayer
		if aboutPlayer:
			for name, child in self.getGui().children: #����״̬�滻��ͼ
				if name in ["l","c","r"]:
					child.textureName = self.bg_teture_path%ABOUTPLAYER_TEXTURE[name]

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyCols = property( _getCols )													# ��ȡ��������
	isAboutPlayer = property( _getAboutPlayer, _setAboutPlayer )					# �Ƿ���������
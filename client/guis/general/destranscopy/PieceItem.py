# -*- coding: gb18030 -*-
# $Id: PieceItem.py, fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from DestransDatasLoader import destransDatasLoader

class PieceItem( Control ):
	"""
	棋子
	"""
	_evtMaps = { 0:(1,1), 1:(2,1), 2:(2,3),3:(2,2),
				4:(1,3),5:(1,4),6:(1,5),7:(1,6),
				8:(1,7),9:(1,8), 10:(2,4),11:(2,5),
				12:(1,2),
				}
				
	def __init__( self, piece, index, pyBinder = None ):
		Control.__init__( self, piece )
		self.focus = True
		self.crossFocus = True
		self.index = index
		self.__evtid = -1
		self.__pyRoutes = {}
		for name, item in piece.children:
			self.__pyRoutes[name] = PyGUI( item )
	
	def setRoutes( self, names ):
		"""
		设置路径
		"""
		for name in names:
			pyChild = self.__pyRoutes.get( name, None )
			if pyChild is None:continue
			pyChild.visible = True
			
	def resetPiece( self ):
		"""
		重置路径
		"""
		for pyRoute in self.__pyRoutes.values():
			pyRoute.visible = False
		util.setGuiState( self.gui, (2,8), (2,6) )
		self.__evtid = -1
	
	def setPieceInfo( self, piece ):
		"""
		设置棋子信息
		"""
		if piece:
			self.__evtid = piece["evtID"]
			mapping = self._evtMaps.get( self.__evtid, (2,6) )
			util.setGuiState( self.gui, (2,8), mapping )
			for name, pyRoute in self.__pyRoutes.items():
				status = piece.get( name, 0 )
				pyRoute.visible = status > 0
		else:
			self.resetPiece()
	
	def _setEvtid( self, evtid ):
		self.__evtid = evtid
	
	def _getEvtid( self ):
		return self.__evtid

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	evtid = property( _getEvtid, _setEvtid )
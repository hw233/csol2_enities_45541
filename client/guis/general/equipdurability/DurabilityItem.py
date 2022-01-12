# -*- coding: gb18030 -*-
#
# $Id: DurabilityItem.py,v 1.12 2008-08-21 09:08:44 huangyongwei Exp $


from guis import *
from guis.controls.Control import Control
import ItemTypeEnum as ItemType
import math
import GUIFacade
import csconst

class DurabilityItem( Control ):
	def __init__( self, equip, pyBinder = None ) :
		Control.__init__( self, equip, pyBinder )
		self.__itemInfo = None
		self.__description = None
		self.__showFlag = False
		self.__initialize( equip )

	def subclass( self, equip, pyBinder = None ) :
		Control.subclass( self, equip, pyBinder )
		self.__initialize( equip )
		return self

	def dispose( self ) :
		self.__itemInfo = None
		Control.dispose( self )

	def __initialize( self, equip ):
		if equip is None : return
		self.focus = False
		self.crossFocus = True
		self.dragFocus = False
		self.dropFocus = False
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		dsp = self.description
		if not BigWorld.isKeyDown( KEY_MOUSE0 ) :
			toolbox.infoTip.showToolTips( self, dsp )
		return True

	def onMouseLeave_( self ) :
		Control.onMouseLeave_( self )
		toolbox.infoTip.hide()
		return True
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		"""
		update item
		"""
		self.__itemInfo = itemInfo
		if itemInfo is None :
			self.visible = False
			self.__description = None
			self.__showFlag = False
		else :
			self.visible = True
			if itemInfo.query( "type" ) in ItemType.WEAPON_LIST:
				parm = 100 * ( 154 - itemInfo.query( "reqLevel" ) )
				hardinessMax = int( itemInfo.eq_hardinessLimit / parm )
				hardiness = int( itemInfo.hardiness / parm )
			else:
				hardinessMax = int( itemInfo.eq_hardinessLimit / csconst.EQUIP_HARDINESS_UPDATE_VALUE )	 #耐久度公式变化时要改变这里；由除10000修改为1000 modify by gjx 2009-3-30
				hardiness = int( math.ceil( itemInfo.hardiness / csconst.EQUIP_HARDINESS_UPDATE_VALUE ) ) #耐久度公式变化时要改变这里
			if hardiness > hardinessMax:
				hardiness = hardinessMax
			self.__description = "%s: %i/%i" % ( itemInfo.name(), hardiness, hardinessMax )
			ratio =  itemInfo.hardiness / ( itemInfo.eq_hardinessLimit + 1 )
			if ratio > GUIFacade.getWarningVal():
				self.__showFlag = False
				util.setGuiState( self.getGui(), ( 2, 2 ), ( 1, 1 ) )
			if ratio >= GUIFacade.getAbateval() and ratio <= GUIFacade.getWarningVal():
				self.__showFlag = True
				util.setGuiState( self.getGui(), ( 2, 2 ), ( 1, 2 ) )
			elif ratio < GUIFacade.getAbateval():
				self.__showFlag = True
				util.setGuiState( self.getGui(), ( 2, 2 ), ( 2, 1 ) )

	# -------------------------------------------------
	def _getDescription( self ) :
		return self.__description

	def _setDescription( self, dsp ) :
		self.__description = dsp

	def _getItemInfo( self ) :
		return self.__itemInfo

	def _getShowFlag( self ):
		return self.__showFlag

	def _setShowFlag( self, flag ):
		self.__showFlag = flag

	itemInfo = property( _getItemInfo )
	description = property( _getDescription )			# get or set the description of the object
	showFlag = property( _getShowFlag, _setShowFlag )

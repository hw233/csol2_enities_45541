# -*- coding: gb18030 -*-
#
# $Id: DropItemName.py, fangpengjun Exp $

"""
implement float name of the character
2009.02.13：tidy up by huangyongwei
"""
import Pixie
from guis import *
from FloatName import FloatName
import event.EventCenter as ECenter
from ItemSystemExp import EquipQualityExp
from DoubleName import DoubleName

class DropItemName( FloatName ):
	def __init__( self ) :
		wnd = GUI.load( "guis/otheruis/floatnames/dropitemname.gui" )
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		self.viewInfoKey_ = "dropItem"
		self.gx = Pixie.create( "particles/tong_tong/diaoluowupin.xml" )
		
		self.pyLbName_ = DoubleName( wnd.elemName )	
		self.pyLbName_.toggleRightName( False )
		self.pyElements_ = [self.pyLbName_]
		
	def dispose( self ) :
		FloatName.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		FloatName.registerTriggers_( self )

	def __updateViewInfo( self ):
		root = self.entity_.model.node("HP_root")
		self.pyLbName_.toggleLeftName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "name" ) )
		isAtached = rds.viewInfoMgr.getSetting( self.viewInfoKey_, "particle" )
		if not isAtached:
			root.detach( self.entity_.gx )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onViewInfoChanged_( self, infoKey, itemKey, oldValue, value ) :
		"""
		显示信息改变时被触发
		"""
		if self.viewInfoKey_ != infoKey : return
		if itemKey == "particle" : #光效
			root = self.entity_.model.node("HP_root")
			if value:
				root.attach( self.entity_.gx )
			else:
				root.detach( self.entity_.gx )
		FloatName.onViewInfoChanged_( self, infoKey, itemKey, oldValue, value )
		
	def onAttachEntity_( self ):
		itemProp = self.entity_.itemProp
		nameColor = EquipQualityExp.instance().getColorByQuality( itemProp.query("quality") )
		self.pyLbName_.leftColor = nameColor
		self.__updateViewInfo()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		FloatName.onEnterWorld( self )

	# ---------------------------------------
	def onTargetFocus( self ) :
		self.visible = True
		self.pyLbName_.toggleLeftName( rds.viewInfoMgr.getSetting( self.viewInfoKey_, "name" ) )

	def onTargetBlur( self ) :
		if BigWorld.player().targetEntity != self.entity_:
			self.visible = False
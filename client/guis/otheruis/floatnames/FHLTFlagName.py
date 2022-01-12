# -*- coding: gb18030 -*-
#
# $Id: QuestBoxName.py,v 1.3 2008-06-27 03:20:42 huangyongwei Exp $

"""
implement float name of the character
2009.02.13：tidy up by huangyongwei
"""

import event.EventCenter as ECenter
from guis import *
from FloatName import FloatName
from bwdebug import *
from DoubleName import DoubleName

class FHLTFlagName( FloatName ) :
	def __init__( self, flagbox ) :
		wnd = GUI.load( "guis/otheruis/floatnames/questboxname.gui" )
		uiFixer.firstLoadFix( wnd )
		printStackTrace()
		FloatName.__init__( self, wnd, flagbox )
		self.pyLbName_ = DoubleName( wnd.elemName )	
		self.pyLbName_.toggleRightName( False )
		self.pyElements_ = [self.pyLbName_]
		self.registerTriggers_()
#		self.__setHeadColor()

	def dispose( self ) :
		FloatName.dispose( self )

	def __setHeadColor( self ):
		"""
		设置名称显示
		"""
		flagBox = self.entity_
		ownTongDBID = flagBox.ownTongDBID
		player = BigWorld.player()
		color = "c1"
		fontSize = 12.0
		if ownTongDBID == 0:
			fontSize = 12.0
			color = "c6"
		else:
			fontSize = 20.0
			if ownTongDBID == player.tong_dbID:
				color = "c4"
			else:
				color = "c48"
		self.pyLbName_.rightFontSize = fontSize
		self.pyLbName_.rightColor = cscolors[color]
		self.layout_()
	
	def __onFlagOwnTongChange ( self, flagBox ):
		if self.entity_ is None or flagBox.id != self.entity_.id:return
		self.__setHeadColor()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_BATTLE_FLAG_OWNTONG_CHANGE"] = self.__onFlagOwnTongChange
		FloatName.registerTriggers_( self )
		
	def layout_( self ) :
		FloatName.layout_( self )
		self.visible = True
		self.pyLbName_.toggleRightName( True )
		
	def onAttachEntity_( self ):
		self.__setHeadColor()	

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		FloatName.onEnterWorld( self )
		
	def flush( self ):
		"""
		刷新模型（更改模型后，将原模型的头顶信息迁移过去）
		"""
		FloatName.flush( self )
		self.__setHeadColor()
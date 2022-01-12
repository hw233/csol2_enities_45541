# -*- coding: gb18030 -*-
#
# $Id: NPCName.py,v 1.14 2008-05-29 05:44:12 huangyongwei Exp $

"""
implement float name of the character
2009.02.13：tidy up by huangyongwei
"""

import csdefine
import Const
import event.EventCenter as ECenter
import ResMgr
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from FloatName import FloatName
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from config.client.colors import Datas as cscolors
from DoubleName import DoubleName

class CityMasterName( FloatName ) :
	__cg_wnd = None
	__cc_dummySection = ResMgr.openSection( "guis/otheruis/floatnames/mastername.gui" )

	def __init__( self ) :
		if CityMasterName.__cg_wnd is None :
			CityMasterName.__cg_wnd = GUI.load( CityMasterName.__cc_dummySection )
		wnd = util.copyGuiTree( CityMasterName.__cg_wnd )
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		self.visible = False
		self.__initialize( wnd )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.pyLbName_ = DoubleName( wnd.elemName )	
		self.pyLbName_.toggleRightName( False )
		self.__pyTitle = StaticText( wnd.ownerName )
		self.__pyTitle.setFloatNameFont()
		self.__pyTitle.color = cscolors["c39"]
		if self.entity_:
			self.__pyTitle.text = self.entity_.title
			self.title = self.entity_.tongName
			self.fName = self.entity_.uname
			self.color = cscolors["c4"]
			self.pyLbName_.leftColor = cscolors["c1"]
		self.pyElements_ = [self.pyLbName_, self.__pyTitle ]
		self.registerTriggers_()

	def __onNameChange( self, id, name ) :
		"""
		城主名称改变
		"""
		if self.entity_ is None:return
		if id != self.entity_.id:return
		self.fName = name
		self.layout_()
	
	def __onTitleChange( self, id, title ):
		"""
		城主称号改变
		"""
		if self.entity_ is None or id != self.entity_.id:return
		self.__pyTitle.text = title

	def __onTongNameChange( self, id, tongName ):
		"""
		城主帮会名称改变
		"""
		if self.entity_ is None or id != self.entity_.id:return
		self.title = tongName
		self.layout_()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_CITYMASTER_NAME_CHANGED"] = self.__onNameChange
		self.triggers_["EVT_ON_CITYMASTER_TITLE_CHANGED"] = self.__onTitleChange
		self.triggers_["EVT_ON_CITYMASTER_TONGNAME_CHANGED"] = self.__onTongNameChange
		FloatName.registerTriggers_( self )
		
	def onAttachEntity_( self ):		
		ppos = BigWorld.player().position
		npos = self.entity_.position
		self.visible = ppos.distTo( npos ) < Const.SHOW_NPCNAME_RANGE+3.0				# 超出指定范围，不显示 NPC 头顶名称	
		self.__pyTitle.text = self.entity_.title
		self.title = self.entity_.tongName
		self.fName = self.entity_.uname
		self.color = cscolors["c4"]
		self.pyLbName_.leftColor = cscolors["c1"]
	
	def onDetachEntity_( self ):
		self.visible = False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def dispose( self ) :
		FloatName.dispose( self )

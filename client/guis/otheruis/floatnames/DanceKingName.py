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
import cschannel_msgs
from DoubleName import RoleDoubleName


class DanceKingName( FloatName ) :
	__cg_wnd = None
	__cc_dummySection = ResMgr.openSection( "guis/otheruis/floatnames/danceking.gui" )
	
	def __init__( self ) :
		if DanceKingName.__cg_wnd is None :
			DanceKingName.__cg_wnd = GUI.load( DanceKingName.__cc_dummySection )
		wnd = util.copyGuiTree( DanceKingName.__cg_wnd )
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		self.visible = False
		self.__initialize( wnd )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		
		self.pyLbName_ = RoleDoubleName( wnd.elemName )	
		self.pyLbName_.toggleDoubleName( False )
		
		self.pyElements_ = [self.pyLbName_,]
		self.registerTriggers_()

	def __onNameChange( self, id, name ) :
		"""
		名字
		"""
		if self.entity_ is None or id != self.entity_.id:return
		self.fName = name
		self.layout_()
	
	def __onTitleChange( self, id, title ):
		"""
		称号
		"""
		if self.entity_ is None or id != self.entity_.id:return
		self.title = title
		self.layout_()
	
	def __onTitleColorChange(self, id, color):
		if self.entity_ is None or id != self.entity_.id:return
		self.pyLbName_.rightColor = color
		self.layout_()

	
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_DANCEKING_NAME_CHANGED"] = self.__onNameChange
		self.triggers_["EVT_ON_DANCEKING_TITLENAME_CHANGE"] = self.__onTitleChange
		self.triggers_["EVT_ON_DANCEKING_TITLECOLOR_CHANGE"] = self.__onTitleColorChange
		FloatName.registerTriggers_( self )
		
	def onAttachEntity_( self ):
		npc = self.entity_
		npos = npc.position
		self.visible = ppos.distTo( npos ) < csdefine.DANCEKINGRANGE				# 超出指定范围，不显示 NPC 头顶名称

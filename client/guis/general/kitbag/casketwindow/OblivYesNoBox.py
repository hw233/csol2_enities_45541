# -*- coding: gb18030 -*-
#
# $Id: MsgBox.py,v 1.9 2008-08-26 02:22:08 huangyongwei Exp $

"""
implement yell verify messagebox
-- 2009/04/23: writen by huangyongwei
"""

import csconst
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.tooluis.messagebox.MsgBox import YesNoBox
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
from guis.MLUIDefine import ItemQAColorMode, QAColor
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from ItemsFactory import ObjectItem

class OblivYesNoBox( YesNoBox ) :
	def __init__( self ) :
		box = GUI.load( "guis/general/kitbag/casketwindow/oblyesno.gui" )
		uiFixer.firstLoadFix( box )
		YesNoBox.__init__( self, box )
		self.activable_ = False
		self.__pyDrawBg = PyGUI( box.drawItem )
		self.__pyDrawItem = BaseObjectItem( box.drawItem.item )
		self.minHeight_ = 186.0								# ������С�߶�
		self.addToMgr( "oblivBox" )
		
	def dispose( self ) :
		YesNoBox.dispose( self )
		self.__pyDrawItem.update( None )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, callback, drawInfo, pyOwner = None ) :
		if drawInfo is None:return
		player = BigWorld.player()
		scrollID = drawInfo["itemID"]
		scrollItem = player.createDynamicItem( scrollID )
		scrollInfo = ObjectItem( scrollItem )
		self.__pyDrawItem.update( scrollInfo )
		quality = scrollItem.getQuality()
		name = scrollItem.name()
		util.setGuiState( self.__pyDrawBg.getGui(), (4,2), ItemQAColorMode[quality] )
		name = PL_Font.getSource( name, fc = QAColor[quality] )
		YesNoBox.show( self, mbmsgs[0x03cc] % name, "", callback, pyOwner )
		self.pyMsgPanel_.align = "C"
		if self.pyBgPanel_:
			self._YesNoBox__pyYesBtn.top = self.pyBgPanel_.bottom
			self._YesNoBox__pyNoBtn.top = self.pyBgPanel_.bottom
		self.pyMsgPanel_.top = self.__pyDrawBg.bottom + 2.0

	def hide( self ) :
		"""
		���ش���
		"""
		self.notifyCallback_( self.defRes_ )			# ��Ĭ�ϵ�����֪ͨ
		self.setOkButton( None ) 
		self.setCancelButton( None )
		YesNoBox.hide( self )
# -*- coding: gb18030 -*-

"""
implement UnchainPrentice window
"""

from guis import *
from guis.common.Window import Window
from guis.controls.ListPanel import ListPanel
from guis.controls.ListItem import SingleColListItem
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather

import random
# --------------------------------------------------------------------
# implement UnchainPrentice window
# --------------------------------------------------------------------
class UnchainPrentice( Window ):
	def __init__( self ) :
		wnd = GUI.load( "guis/general/npctalk/unchain.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.posZSegment = ZSegs.L2											# ����Ĭ��Ϊ�ڶ���
		self.escHide_ = True													# ���԰� esc ���ر�
		self.activable_ = True													# ���Ա�����
		self.h_dockStyle = "CENTER"												# ˮƽ������ʾ
		self.v_dockStyle = "MIDDLE"												# ��ֱ������ʾ

		self.__npcID = 0
		self.pyPanel_ = ListPanel( wnd.conwindow.clipPanel, wnd.conwindow.sbar )	# ͽ���б�
		labelGather.setLabel( wnd.lbTitle, "NPCTalkWnd:UnchainPrentice", "lbTitle" )
		self.addToMgr( "UnchainPrentice" )											# ��ӵ�������

	def __onItemClick( self, pyItem ):
		"""
		ѡ��ĳ��ͽ��
		"""
		player = BigWorld.player()
		for dbid, playerItem in player.prenticeDict.iteritems():
			if playerItem.playerName == pyItem.text:
				prenticeID = dbid
				prenticeName = playerItem.playerName
		def unChain( rs_id ):
			player = BigWorld.player()
			if rs_id == RS_OK:
				player.base.teach_requestDisband( prenticeName )
		# "���Ƿ�Ҫ���ͽ��%s"
		showMessage( mbmsgs[0x04a1] % pyItem.text, "", MB_OK_CANCEL, unChain )
		Window.hide( self )

	def addItem( self, text ):
		"""
		���һ��ͽ�ܵ����
		"""
		pyItem = SingleColListItem()
		pyItem.text = text
		pyItem.texture = ""
		pyItem.commonForeColor = ( 160, 160, 160, 255 )
		pyItem.highlightForeColor = ( 255, 0, 0, 255 )
		pyItem.selectedForeColor = pyItem.commonForeColor
		pyItem.onLClick.bind( self.__onItemClick )
		self.pyPanel_.addItem( pyItem )
		return pyItem

	def clearItems( self ):
		"""
		������
		"""
		self.pyPanel_.clearItems()

	def showWindow( self, npcID ):
		"""
		��ʾ���
		"""
		player = BigWorld.player()
		self.__npcID = npcID
		self.clearItems()
		for playerName, playerItem in player.prenticeDict.iteritems():
			pyItemText = playerItem.playerName
			self.addItem( pyItemText )
		Window.show( self )


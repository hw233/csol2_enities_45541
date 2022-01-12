# -*- coding: gb18030 -*-
# $Id: DestransWnd.py, fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText

class MarkItem( PyGUI ):
	"""
	玩家标记
	"""
	def __init__( self, dbid ):
		item = GUI.load( "guis/general/destranscopy/mark.gui" )
		uiFixer.firstLoadFix( item )
		PyGUI.__init__( self, item )
		self.__pyStName = StaticText( item.stName )
		self.__pyStName.text = ""
		self.__pyStName.font = "MSYHBD.TTF"
		self.__pyStName.fontSize = 12
		self.__pyStName.charSpace = -2.0
		self.__pyMark = PyGUI( item.mark )
		self.__dbid = dbid
		self.entityID = 0
		self.step = 0
		self.initeMark( dbid )
	
	def initeMark( self, dbid ):
		"""
		设置玩家标识颜色
		"""
		player = BigWorld.player()
		teamMember = player.teamMember
		dbids = [member.DBID for member in teamMember.values()]
		mapping = (1,1)
		name = ""
		if dbid in dbids:							
			if dbid == player.databaseID:		#自己
				mapping = (1,1)
				name = player.getName() 
			else:								#队友
				mapping = (1,2)
				name = self.__getMemberName( dbid )
		else:
			mapping = (2,1)					#敌人
			name = "敌人"
		self.__pyStName.text = name
		util.setGuiState( self.gui, (2,2), mapping )
		self.entityID = self.__getEntityByDbid( dbid )
	
	def __getMemberName( self, dbid ):
		"""
		队友名称
		"""
		player = BigWorld.player()
		for member in player.teamMember.values():
			if member.DBID == dbid:
				return member.name
	
	def setStep( self, step ):
		"""
		当前所在棋子位置
		"""
		self.step = step
	
	def __getEntityByDbid( self, dbid ):
		"""
		通过dbid获取entityid
		"""
		player = BigWorld.player()
		
		for entityid, member in player.teamMember.items():
			if member.DBID == dbid:
				return entityid
		return 0
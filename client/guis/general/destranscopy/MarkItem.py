# -*- coding: gb18030 -*-
# $Id: DestransWnd.py, fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText

class MarkItem( PyGUI ):
	"""
	��ұ��
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
		������ұ�ʶ��ɫ
		"""
		player = BigWorld.player()
		teamMember = player.teamMember
		dbids = [member.DBID for member in teamMember.values()]
		mapping = (1,1)
		name = ""
		if dbid in dbids:							
			if dbid == player.databaseID:		#�Լ�
				mapping = (1,1)
				name = player.getName() 
			else:								#����
				mapping = (1,2)
				name = self.__getMemberName( dbid )
		else:
			mapping = (2,1)					#����
			name = "����"
		self.__pyStName.text = name
		util.setGuiState( self.gui, (2,2), mapping )
		self.entityID = self.__getEntityByDbid( dbid )
	
	def __getMemberName( self, dbid ):
		"""
		��������
		"""
		player = BigWorld.player()
		for member in player.teamMember.values():
			if member.DBID == dbid:
				return member.name
	
	def setStep( self, step ):
		"""
		��ǰ��������λ��
		"""
		self.step = step
	
	def __getEntityByDbid( self, dbid ):
		"""
		ͨ��dbid��ȡentityid
		"""
		player = BigWorld.player()
		
		for entityid, member in player.teamMember.items():
			if member.DBID == dbid:
				return entityid
		return 0
# -*- coding: gb18030 -*-
#
# $Id: DialogManager.py,v 1.2 2008-01-15 06:06:21 phw Exp $

"""
"""

from bwdebug import *
from DialogMsg import DialogMsg
from DialogData import DialogData

class DialogManager:
	"""
	�Ի������
	"""
	def __init__( self, section = None ):
		"""
		"""
		self._dialogs = {}		# key is dlgKey with string type, value is instance of class DialogData
		if section:
			self.init( section )
	
	def init( self, section ):
		"""
		@param section: xml data section
		@type  section: pyDataSection
		"""
		# load all dialog
		for sec in section.values():
			dlg = DialogData( sec )
			self._dialogs[sec.readString( "key" )] = dlg
		
		# build dialog depend
		for v in self._dialogs.itervalues():
			v.buildDepend( self )
	
	def doTalk( self, dlgKey, player, param = None ):
		"""
		ִ�жԻ�����
		
		@param dlgKey: �Ի��ؼ���
		@type  dlgKey: string
		@param player: ���
		@type  player: Entity
		@param target: һ����չ�Ĳ���
		@type  target: any
		@return: None
		"""
		try:
			dlg = self._dialogs[dlgKey]
		except KeyError, errstr:
			return
		dlg.doTalk( player, param )
		
	def getDialog( self, dlgKey ):
		"""
		��ָ���ؼ���ȡ��һ���Ի����������򷵻�None
		
		@param dlgKey: �Ի��ؼ���
		@type  dlgKey: string
		@return: instance of DialogData/None
		"""
		try:
			return self._dialogs[dlgKey]
		except KeyError:
			return None



#
# $Log: not supported by cvs2svn $
# Revision 1.1  2005/12/08 01:07:44  phw
# no message
#
#

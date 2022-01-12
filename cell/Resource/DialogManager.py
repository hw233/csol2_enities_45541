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
	对话抽像层
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
		执行对话动作
		
		@param dlgKey: 对话关键字
		@type  dlgKey: string
		@param player: 玩家
		@type  player: Entity
		@param target: 一个扩展的参数
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
		以指定关键字取得一个对话，不存在则返回None
		
		@param dlgKey: 对话关键字
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

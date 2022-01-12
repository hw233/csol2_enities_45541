# -*- coding: gb18030 -*-
#
# $Id: DialogMsg.py,v 1.2 2008-02-26 02:02:36 zhangyuxing Exp $

"""
"""

class DialogMsg:
	"""
	@ivar dlgDict: 对话内容; key = 对话关键字；value = dict as {"msg":"", "name":"", "menu":[]}，"name"可以不存在
	               - value["menu"] is a list that as [ (menukey, msg), (menukey, msg), ... ]
	@type dlgDict: dict
	@ivar nextAction: 当前菜单项关键字记录, It's a list that as [ menukey, menukey, menukey, ... ]
	@type nextAction: list of string
	"""
	def __init__( self ):
		self.reset()
	
	def reset( self ):
		"""
		重置对话内容
		"""
		self.dlgDict = {}
		self.nextAction = []
	
	def copy( self ):
		"""
		复制自己
		
		@return: DialogMsg对像实例
		@rtype:  DialogMsg
		"""
		obj = DialogMsg()
		obj.dlgDict = self.dlgDict.copy()
		if obj.dlgDict.has_key( "menu" ):
			obj.dlgDict["menu"] = list( self.getMenus() )	# 为了防止复制后被修改,这里再复制一次列表
		obj.nextAction = list( self.nextAction )			# 同上
		return obj
	
	def getData( self ):
		"""
		取得对话内容
		
		@return: dict
		@rtype:  dict
		"""
		return self.dlgDict

	def getMenuKeys( self ):
		"""
		取得菜单选项关键字列表
		
		@return: list as [menukey, menukey, ...]
		@rtype:  list of string
		"""
		return self.nextAction

	def getMenus( self ):
		"""
		取得菜单选项列表
		
		@return: list as [ (menukey, msg), (menukey, msg), ... ], 如果不存在menu则返回None
		@rtype:  list of string
		"""
		try:
			return self.dlgDict["menu"]
		except KeyError:
			return []

	def addMenu( self, key, title, type ):
		"""
		增加一个菜单选项条
		
		@param key: 关键字
		@type  key: str
		@param msg: 对话内容
		@type  msg: str
		return: 无
		"""
		dlgDict = self.dlgDict
		if len( key ) != 0:
			self.nextAction.append( key )
		try:
			dlgDict["menu"].append( (key, title, type) )
		except KeyError:
			dlgDict["menu"] = [(key, title, type)]
	
	def getMsg( self ):
		"""
		取得对话内容
		
		@return: 对话内容
		@rtype:  string
		"""
		try:
			return self.dlgDict["msg"]
		except KeyError:
			return ""
	
	def setMsg( self, msg ):
		"""
		设置对话默认内容
		
		@param msg: 对话内容
		@type  msg: str
		return: 无
		"""
		self.dlgDict["msg"] = msg
		
	def getName( self ):
		"""
		取得和玩家对话的人(npc)的名称
		
		@return: 返回和玩家对话的人(npc)的名称
		@rtype:  string
		"""
		try:
			return self.dlgDict["name"]
		except KeyError:
			return ""

	def setName( self, name ):
		"""
		设置和玩家对话的人(npc)的名称
		
		@param name: 和玩家对话的人(npc)的名称
		@type  name: str
		return: 无
		"""
		self.dlgDict["name"] = name
		


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2005/12/08 01:07:44  phw
# no message
#
#

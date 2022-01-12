# -*- coding: gb18030 -*-
#
# $Id: DialogMsg.py,v 1.2 2008-02-26 02:02:36 zhangyuxing Exp $

"""
"""

class DialogMsg:
	"""
	@ivar dlgDict: �Ի�����; key = �Ի��ؼ��֣�value = dict as {"msg":"", "name":"", "menu":[]}��"name"���Բ�����
	               - value["menu"] is a list that as [ (menukey, msg), (menukey, msg), ... ]
	@type dlgDict: dict
	@ivar nextAction: ��ǰ�˵���ؼ��ּ�¼, It's a list that as [ menukey, menukey, menukey, ... ]
	@type nextAction: list of string
	"""
	def __init__( self ):
		self.reset()
	
	def reset( self ):
		"""
		���öԻ�����
		"""
		self.dlgDict = {}
		self.nextAction = []
	
	def copy( self ):
		"""
		�����Լ�
		
		@return: DialogMsg����ʵ��
		@rtype:  DialogMsg
		"""
		obj = DialogMsg()
		obj.dlgDict = self.dlgDict.copy()
		if obj.dlgDict.has_key( "menu" ):
			obj.dlgDict["menu"] = list( self.getMenus() )	# Ϊ�˷�ֹ���ƺ��޸�,�����ٸ���һ���б�
		obj.nextAction = list( self.nextAction )			# ͬ��
		return obj
	
	def getData( self ):
		"""
		ȡ�öԻ�����
		
		@return: dict
		@rtype:  dict
		"""
		return self.dlgDict

	def getMenuKeys( self ):
		"""
		ȡ�ò˵�ѡ��ؼ����б�
		
		@return: list as [menukey, menukey, ...]
		@rtype:  list of string
		"""
		return self.nextAction

	def getMenus( self ):
		"""
		ȡ�ò˵�ѡ���б�
		
		@return: list as [ (menukey, msg), (menukey, msg), ... ], ���������menu�򷵻�None
		@rtype:  list of string
		"""
		try:
			return self.dlgDict["menu"]
		except KeyError:
			return []

	def addMenu( self, key, title, type ):
		"""
		����һ���˵�ѡ����
		
		@param key: �ؼ���
		@type  key: str
		@param msg: �Ի�����
		@type  msg: str
		return: ��
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
		ȡ�öԻ�����
		
		@return: �Ի�����
		@rtype:  string
		"""
		try:
			return self.dlgDict["msg"]
		except KeyError:
			return ""
	
	def setMsg( self, msg ):
		"""
		���öԻ�Ĭ������
		
		@param msg: �Ի�����
		@type  msg: str
		return: ��
		"""
		self.dlgDict["msg"] = msg
		
	def getName( self ):
		"""
		ȡ�ú���ҶԻ�����(npc)������
		
		@return: ���غ���ҶԻ�����(npc)������
		@rtype:  string
		"""
		try:
			return self.dlgDict["name"]
		except KeyError:
			return ""

	def setName( self, name ):
		"""
		���ú���ҶԻ�����(npc)������
		
		@param name: ����ҶԻ�����(npc)������
		@type  name: str
		return: ��
		"""
		self.dlgDict["name"] = name
		


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2005/12/08 01:07:44  phw
# no message
#
#

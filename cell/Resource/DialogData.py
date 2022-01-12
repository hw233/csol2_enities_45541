# -*- coding: gb18030 -*-
#
# $Id: DialogData.py,v 1.13 2008-08-11 01:02:04 kebiao Exp $

"""
"""

from bwdebug import *
from DialogMsg import DialogMsg
from Resource.FuncsModule.Functions import Functions

class DialogData:
	"""
	�Ի������
	"""
	def __init__( self, section = None ):
		"""
		"""
		self._functions = []
		self._actions = []
		self._dlgMsg = None	# dict type
		self._dlgDepands = {}	# key is menuKey, value is instance of class DialogData
		self._isAlwayOpen = False
		if section:
			self.init( section )

	def init( self, section ):
		"""
		@param section: xml data section
		@type  section: pyDataSection
		"""
		# init dialog message
		self.initDialogMsg( section )
		if section.has_key( "alwayOpen" ):
			self._isAlwayOpen = True

		# init functions
		if section.has_key( "functions" ):
			funcs = Functions( section["functions"] )
			self._functions.append( funcs )		# ��ʵ�ϣ���ǰ������ֻ��һ��Functions��

	def initDialogMsg( self, section ):
		"""
		@param section: xml data section
		@type  section: pyDataSection
		"""
		dlg = DialogMsg()
		self._dlgMsg = dlg
		dlg.setMsg( section.readString( "msg" ) )
		if section.has_key( "keys" ):
			for m in section["keys"].values():
				key = m.readString( "key" )
				title = m.readString( "title" )
				type = m.readInt( "type" )
				dlg.addMenu( key, title, type )
		return	# the end

	def doTalk( self, player, talkEntity = None ):
		"""
		ִ�жԻ�����

		@param player: ���
		@type  player: Entity
		@param talkEntity: �Ի���ԭʼĿ��Entity
		@type  talkEntity: Entity
		@return: None
		"""
		if not self.doFunction( player, talkEntity ):
			player.endGossip( talkEntity )
			return	# ���ִ�й���ʧ���򲻽��жԻ�

		if self._dlgMsg is None:
			return	# û�жԻ�,ֱ�ӷ���

		# send dialog
		player.setGossipText( self._dlgMsg.getMsg() )
		for m in self._dlgMsg.getMenus():
			if self._dlgDepands[m[0]].canTalk( player, talkEntity ):
				player.addGossipOption( *m )

		# ��䲻Ӧ�÷�����,��ǰ����ֻ����Ի�,���Ƿ�������������
		#target.sendGossipComplete( player )


	def doFunction( self, player, talkEntity = None ):
		"""
		ִ�й���

		@return: �����actions�����е�action��ִ��ʧ���򷵻�False,���򷵻�True
		@return: BOOL
		"""
		if len( self._functions ) == 0:
			if talkEntity != None:
				player.endGossip( talkEntity )
			return True

		# do all functions
		for funcs in self._functions:
			ret = funcs.valid( player, talkEntity )
			if ret == None:
				funcs.do( player, talkEntity )
				return True
			else:
				if ret != -1:
					ret.doTalk( player, talkEntity )
		return False

	def canTalk( self, player, talkEntity = None ):
		"""
		���Ի������Ƿ�����

		@param player: ���
		@type  player: Entity
		@param talkEntity: һ����չ�Ĳ���
		@type  talkEntity: entity
		@return: None
		"""
		if len( self._functions ) == 0 or self._isAlwayOpen: return True	# no function
		for funcs in self._functions:
			if funcs.valid( player, talkEntity ) is None:
				return True
		return False

	def buildDepend( self, manager ):
		"""
		@param manager: ��Ĺ�����
		@type  manager: DialogManager
		"""
		# buildDepend all functions
		for funcs in self._functions:
			funcs.buildDepend( manager )

		if self._dlgMsg is None:
			return
		menus = self._dlgMsg.getMenuKeys()
		for m in menus:
			dlgData = manager.getDialog( m )
			if dlgData is None:
				continue
			self._dlgDepands[m] = dlgData



#
# $Log: not supported by cvs2svn $
# Revision 1.12  2008/08/05 06:30:59  zhangyuxing
# ����û�ж԰ײ����ͶԻ���Ϣ�ж�
#
# Revision 1.11  2008/02/26 02:02:24  zhangyuxing
# ���ڶԻ�ѡ���һ��ͼ���ʶ������޸ģ���Ҫ�������ļ���һ�� type,)
# ������Ҫ����
#
# Revision 1.10  2008/01/15 06:06:21  phw
# �����˳�ʼ����ʽ
#
# Revision 1.9  2007/12/04 04:39:54  fangpengjun
# ��npc��ͨ�Ի��ӿ�ת�����
#
# Revision 1.8  2007/05/22 08:18:31  phw
# method modified: canTalk(), �����к������ܵĶԻ�������ȷ���ֵ�bug
#
# Revision 1.7  2007/05/18 08:40:20  kebiao
# ����isAlwayOpen���Ծ���һ�����ܲ����Ƿ�ʧ�ܶ���ʾ�Ի��Ͳ˵�
# �޸�����param ΪtargetEntity
# ����ĳ������ʧ�� �����ʧ�ܹ���
#
# Revision 1.6  2006/12/23 07:28:14  kebiao
# ����˶Ի�key���� "quit�������Ի�"����û���ƶ�һ�����ܺ��������ʱ��Ĭ��Ϊ�رնԻ���param.endGossip( player )
#
# Revision 1.5  2006/03/23 09:24:53  phw
# *** empty log message ***
#
# Revision 1.4  2006/02/28 08:03:03  phw
# no message
#
# Revision 1.3  2005/12/08 01:07:20  phw
# no message
#
#

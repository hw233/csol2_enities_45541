# -*- coding: gb18030 -*-
#

from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
import Love3
import BigWorld
from bwdebug import *


class SpaceCopyExpMelee( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		BigWorld.globalData["ExpMeleeMgr"].onRegisterSpace( self )

	def closeSpace( self, deleteFromDB = True ):
		"""
		define method.
		destroy space��Ψһ��ڣ����е�spaceɾ����Ӧ���ߴ˽ӿڣ�
		space�������ڽ�����ɾ��space
		"""
		BigWorld.globalData["ExpMeleeMgr"].onUnRegisterSpace( self.id )
		SpaceCopy.closeSpace( self, deleteFromDB )

	def onLoseCell( self ):
		"""
		CELL����
		"""
		BigWorld.globalData["ExpMeleeMgr"].onUnRegisterSpace( self.id )
		SpaceCopy.onLoseCell( self )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		��ҽ����˿ռ䣬��Ҫ���ݸ���boss�Ļ�ɱ����������
		��Ӧ����ʾ���������ѡ���Ǽ������������뿪������
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )

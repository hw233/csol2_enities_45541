# -*- coding: gb18030 -*-
#
# ��ұ���ϵͳ	2009-01-10 SongPeifang & LinQing
#

import BigWorld
import GUIFacade
import csstatus
import csdefine
import Const
from gbref import rds
from NPCModelLoader import NPCModelLoader as NPCModel

class RoleChangeBody:
	"""
	��ұ���ϵͳ
	"""
	def __init__( self ):
		"""
		"""
		pass

	def canChangeBody( self ):
		"""
		�������Ƿ��������
		"""
		return True

	def begin_body_changing( self, modelNumber, modelScale ):
		"""
		��ұ���Ľӿ�
		"""
		if not self.canChangeBody():
			return
		# ֪ͨ������Ҫ���ʲô
		self.cell.begin_body_changing( modelNumber, modelScale )

	def set_currentModelNumber( self, old = '' ):
		"""
		ģ�ͱ�ŷ����ı�
		"""
		player = BigWorld.player()
		if self.currentModelNumber == "":
			self.createEquipModel()
		else:
			self.createChangeModel()

	def end_body_changing( self, modelNumber ):
		"""
		���ȡ������Ľӿ�
		"""
		player = BigWorld.player()
		if player.id == self.id:
			self.cell.end_body_changing( modelNumber )

	def isFishing( self ):
		"""
		�Ƿ��ǵ���
		"""
		return self.currentModelNumber == "fishing"

	def endFishing( self ):
		"""
		ȡ������
		"""
		self.end_body_changing( "" )
# -*- coding: gb18030 -*-
#
# Ұ������ֽű��ļ� 2009-02-12 SongPeifang
#

from Monster import Monster
import csdefine
import Resource.AIData

class QuestNPCMonster( Monster ):
	"""
	"""	
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		# ��ʼ���������ݷ���ǰͷ
		Monster.initEntity( self, selfEntity )
		selfEntity.changeToNPC()
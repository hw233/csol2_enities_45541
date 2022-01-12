# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import BigWorld
from bwdebug import *
from interface.GameObject import GameObject

class SkillTrap( BigWorld.Base, GameObject ):
	"""
	���ã�����ҽ�������뿪������ʱ��ͨ������ҽ���һЩ����ȥ������ҵ�һЩ��Ϊ�����̯��������
	"""
	def __init__( self ):
		super( SkillTrap, self ).__init__()

		try:
			cell = self.createOnCell
			del self.createOnCell
		except AttributeError, e:
			cell = None

		if cell is not None:
			self.createCellEntity( cell )

	def onLoseCell( self ):
		self.destroy()

# -*- coding:gb18030 -*-

from Monster import Monster
from LevelEXP import TeachSpaceAmendExp

class TeachSpaceMonster( Monster ):
	"""
	ʦͽ����С�ֽű�
	"""
	def getExpAmendRate( self, levelFall ):
		"""
		���ݵȼ����þ�������ֵ
		
		@param levelFall : ��Һ͹���ĵȼ���
		"""
		return TeachSpaceAmendExp.instance().getLevelRate( levelFall )
		
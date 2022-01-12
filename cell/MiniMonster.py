# -*- coding: gb18030 -*-


from Monster import Monster
import BigWorld
import csdefine
from bwdebug import *
import time

class MiniMonster( Monster ):
	"""
	����ս��AI���̹���
	"""
	def onFightAIHeartbeat( self ):
		"""
		ս��״̬��AI �� ���������ǵײ�ս��������Ϊ
		"""
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :				# �������ý����л�
			Monster.onFightAIHeartbeat( self )	
			return 
			
		if self.fightStartTime == 0.0:
			self.fightStartTime = time.time()
			
		self.getScript().onFightAIHeartbeat( self )	# Ϊ�˼��ٹ�������ͣ�����ת�ɹ����Scriptȥ������
		self.setAITargetID( 0 ) # ��ձ���AI����, ��һ������һ��ȥ����
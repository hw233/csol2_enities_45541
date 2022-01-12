# -*- coding:gb18030 -*-

from Skill_Posture import Skill_Posture
from bwdebug import *

class Skill_400040( Skill_Posture ):
	"""
	��̬�������� ��׼
	
	ÿ�ȼ����X����������
	"""
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Posture.init( self, dict )
		self._param2 = float( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) * 100
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.hitProbability_value += self._param2
		ownerEntity.calcHitProbability()
		
	def detach( self, ownerEntity ):
		"""
		virtual method
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.hitProbability_value -= self._param2
		ownerEntity.calcHitProbability()
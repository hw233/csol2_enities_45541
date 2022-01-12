# -*- coding:gb18030 -*-
#

from Skill_Posture import Skill_Posture
from bwdebug import *

class Skill_400037( Skill_Posture ):
	"""
	��Ѫ
	
	����ÿ�ȼ����1%�����˺�����50��
	"""
	def init( self, data ):
		"""
		"""
		Skill_Posture.init( self, data )
		self._param2 = float( data[ "param2" ] if len( data[ "param2" ] ) > 0 else 0 ) * 100
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.double_hit_multiple_percent += self._param2
		ownerEntity.calcDoubleHitMultiple()
		
	def detach( self, ownerEntity ):
		"""
		virtual method
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.double_hit_multiple_percent -= self._param2
		ownerEntity.calcDoubleHitMultiple()
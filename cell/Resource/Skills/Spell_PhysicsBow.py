# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysicsBow.py,v 1.3 2008-03-03 06:34:23 kebiao Exp $

"""
������Ч��
"""

from bwdebug import *
from Spell_Physics import Spell_Physics

class Spell_PhysicsBow( Spell_Physics ):
	"""
	��ͨ�����˺������ڹ���Զ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Physics.__init__( self )


	def calcDelay( self, caster, target ):
		"""
		virtual method.
		ȡ���˺��ӳ�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: float(��)
		"""
		#����͵ײ�spell��һ���� ���ڼ̳���Spell_Physics����Ҫ��ԭ����
		return target.calcDelay( self, caster )
		

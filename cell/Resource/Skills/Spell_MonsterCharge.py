# -*- coding:gb18030 -*-

#edit by wuxo 2014-1-8
"""
����ר�ó�漼��
֧�ֳ������ס���浽Ŀ��boundingboxǰ
"""

import Math
import csdefine
import csarithmetic
from Spell_PhysSkillImprove import Spell_PhysSkillImprove

class Spell_MonsterCharge( Spell_PhysSkillImprove ):
	"""
	����ר�ó�漼��
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
		self.casterMoveDistance = 0.0	#��̾���
		self.casterMoveSpeed    = 0.0	#����ٶ�
		self.traceDis           = 0.0  #���ֿ�������
		self.delayTime  	= 0.0 #�����˺�Ч���ӳ�ʱ��

	def init( self, data ):
		"""
		"""
		Spell_PhysSkillImprove.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) > 0:
			self.casterMoveSpeed = float( param2[0] )
		if len( param2 ) > 1:	
			self.casterMoveDistance = float( param2[1] )
		if len( param2 ) > 2:	
			self.traceDis = float( param2[2] )	

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		ȡ���˺��ӳ�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: float(��)
		"""
		return  self.delayTime

	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return #����ר��
		# ʩ����λ��
		en = target.getObject()
		dis = self.getDistance( caster, en )
		self.delayTime = dis / self.casterMoveSpeed
		if self.casterMoveSpeed and dis:
			direction = en.position - caster.position
			direction.normalise()
			dstPos = caster.position + direction * dis
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+3,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-3,endDstPos[2]) )
			caster.moveToPosFC( endDstPos, self.casterMoveSpeed, True )
		Spell_PhysSkillImprove.cast( self, caster, target )
	
	def getDistance( self, caster, target ):
		"""
		���ʩ����Ҫ��̵ľ���
		"""
		if self.casterMoveDistance > 0.0: #��������˳�̾���
			return self.casterMoveDistance
		else:  #û�����ó�̾��룬�Ͳ���boundingbox�������
			return caster.distanceBB( target ) - self.traceDis
	
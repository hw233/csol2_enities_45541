# -*- coding: gb18030 -*-

"""
������������
"""
from Monster import Monster
import BigWorld
from Resource.SkillLoader import g_skills
from utils import checkAndMoveByDis, checkAndMove
import csdefine
import csstatus
from bwdebug import *
from Resource.MiniMonsterSkillLoader import MiniMonsterSkillLoader
import time
MOVE_MAX_RANGE = 5.0

g_MiniMonsterSkill = MiniMonsterSkillLoader.instance()

class MiniMonster_Mini( Monster ):
	"""
	������������࣬��Ҫ�����У�
	1��������Ч�Լ��
	2����������Ұ��Χ�ĵ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.__init__( self )
		self.skillID = 0
		
	def onFightAIHeartbeat( self, selfEntity ):
		"""
		ս��״̬��AI �� ����
		"""
		selfEntity.checkAttackTarget( selfEntity.targetID )			# ������Ч�Լ��
		selfEntity.onViewRange()									# ��������Ұ��Χ�ĵ���
		
		if selfEntity.targetID == 0:
			return
		
		# ʹ�ü���
		if checkAndMove( selfEntity ):
			return
		selfEntity.rotateToTarget()
		if not self.skillID:
			self.skillID = g_MiniMonsterSkill.getSkillIDByClassName( selfEntity.className )
		state = selfEntity.spellTarget( self.skillID,  selfEntity.targetID )

		if selfEntity.isDestroyed or selfEntity.state == csdefine.ENTITY_STATE_DEAD:
			return
		elif state == csstatus.SKILL_GO_ON:						# ����ʩչ,ֱ�ӷ���
			return
		elif state == csstatus.SKILL_TOO_FAR:
			if selfEntity.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "I can't move!" )
				selfEntity.stopMoving()
				return
			spell = g_skills[ self.skillID ]
			selfEntity.chaseTarget( BigWorld.entities[ selfEntity.targetID ], spell.getRangeMax( selfEntity ) )

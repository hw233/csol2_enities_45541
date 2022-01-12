# -*- coding: gb18030 -*-

"""
精简怪物基础类
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
	基本精简怪物类，主要功能有：
	1、敌人有效性检查
	2、清理不在视野范围的敌人
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
		self.skillID = 0
		
	def onFightAIHeartbeat( self, selfEntity ):
		"""
		战斗状态下AI 的 心跳
		"""
		selfEntity.checkAttackTarget( selfEntity.targetID )			# 敌人有效性检查
		selfEntity.onViewRange()									# 清理不在视野范围的敌人
		
		if selfEntity.targetID == 0:
			return
		
		# 使用技能
		if checkAndMove( selfEntity ):
			return
		selfEntity.rotateToTarget()
		if not self.skillID:
			self.skillID = g_MiniMonsterSkill.getSkillIDByClassName( selfEntity.className )
		state = selfEntity.spellTarget( self.skillID,  selfEntity.targetID )

		if selfEntity.isDestroyed or selfEntity.state == csdefine.ENTITY_STATE_DEAD:
			return
		elif state == csstatus.SKILL_GO_ON:						# 正常施展,直接返回
			return
		elif state == csstatus.SKILL_TOO_FAR:
			if selfEntity.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "I can't move!" )
				selfEntity.stopMoving()
				return
			spell = g_skills[ self.skillID ]
			selfEntity.chaseTarget( BigWorld.entities[ selfEntity.targetID ], spell.getRangeMax( selfEntity ) )

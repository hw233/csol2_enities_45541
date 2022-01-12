# -*- coding: gb18030 -*-
#
# �ٻ�NPC����

import copy
import math
import random
import Math
import ECBExtend
import csstatus
import csarithmetic
from bwdebug import *
import SkillTargetObjImpl
from Spell_BuffNormal import Spell_BuffNormal

class Spell_Summon( Spell_BuffNormal ):
	"""
	�ٻ�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )
		self.npcs = []   #����NPC��Ϣ
		self._target = None 
		self.level = 0	#������NPC�ȼ� ���������0 ΪĬ�ϵ�ʩ���ߵȼ�
		self.randomPosFlag = False  #�Ƿ�Ҫ��ʩ���߷���������������
		self.dis = 0   #�������
		self.maxHeightDiff = 0.0	#����ˢ��λ�����й���λ�ø߶Ȳ��ܳ�����ֵ������ȡʩ����λ��Ϊˢ��λ�� CSOL-230
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		if dict["param1"] != "" :
			self.npcs = eval(dict["param1"])
		else:
			self.npcs = []
			
		if dict["param2"] != "" :
			self.level = int(dict["param2"])
		else:
			self.level = 0
			
		if dict["param3"] != "" :
			self.dis = float(dict["param3"])
		else:
			self.dis = 0
			
		if dict["param4"] != "" :
			self.randomPosFlag = bool( int(dict["param4"]) )
		else:
			self.randomPosFlag = False
		
		if dict["param5"] != "" :
			self.maxHeightDiff = float(dict["param5"])
			
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# ʩ��������
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ʩ���߼��
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		
		if not target:
			dstPos = tuple( caster.position )
		else:
			dstPos = target.getObjectPosition()
		self._target = copy.deepcopy(SkillTargetObjImpl.createTargetObjPosition(dstPos))
		caster.setTemp( "SUMMON_CENTER_POS", dstPos )
		return csstatus.SKILL_GO_ON
	
	def onArrive( self, caster, target ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		# ��ʼ��NPC
		level = 50
		if self.level > 0:
			level = self.level
		else:
			level = caster.level
		posList = [] #������꼯��
		entitiesL = [] #������������ʵ�弯��
		if self.dis:
			dstPos = caster.popTemp( "SUMMON_CENTER_POS",  tuple( caster.position ) )
			posList = calculatePos( caster.spaceID, caster.yaw, self.dis, dstPos )
		for info in self.npcs:
			for i in range( info[1] ):
				entity = caster.createObjectNearPlanes( info[0], tuple( caster.position ), caster.direction,{"level":level,"spawnPos":tuple( caster.position ) } )
				entitiesL.append( entity )
		if self.randomPosFlag:
			entitiesL.append( caster )
		for en in entitiesL:
			if len( posList ) != 0:
				pos = random.choice( posList )
				posList.remove( pos )
				if self.maxHeightDiff == 0.0 or abs(pos.y - en.position.y) <= self.maxHeightDiff:
					en.openVolatileInfo()
					en.position = pos
		
		self.receiveLinkBuff( caster, target.getObject() )	#֧��buff
		Spell_BuffNormal.onArrive( self, caster, target )
		

def calculatePos( spaceID, yaw, dis, pos):
	"""
	����8���㣬�Ƕ�yaw������dis
	"""
	posL = []
	for i in range(8):
		y = yaw + ( math.pi * 2 / 8 ) * i
		direction = Math.Vector3( math.sin(y), 0.0, math.cos(y) ) 
		direction.normalise()
		dstPos = pos + direction * dis
		collPos = csarithmetic.getCollidePoint( spaceID, pos, dstPos )
		endDstPos = csarithmetic.getCollidePoint( spaceID, Math.Vector3( collPos[0],collPos[1] + 10,collPos[2]), Math.Vector3( collPos[0],collPos[1] - 10,collPos[2]) )
		posL.append( endDstPos )
	return posL
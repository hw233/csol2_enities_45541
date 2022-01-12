# -*- coding: gb18030 -*-
#
# $Id: RoleGem.py,v 1.1 2008-08-01 11:22:25 wangshufeng Exp $

"""
��ɫ���鱦ʯϵͳ��15:31 2008-7-21��wsf
"""

import time
import csdefine
import csstatus
import csconst
import Const
from bwdebug import *
import random
import ECBExtend
from LevelEXP import RoleLevelEXP as RLevelEXP
from ExpGem import CommonExpGem


class RoleGem:
	def __init__( self ):
		self.gem_login()
		# self.gemActive,��Ҿ��鱦ʯϵͳ�Ƿ񱻼���ı�־���ұߵ�1λ��ʾ��Ҿ��鱦ʯ����2λ��ʾ��ҳ��ﾭ�鱦ʯ


	def gem_canActivateGem( self ):
		"""
		�ж��Ƿ��ܹ�����鱦ʯϵͳ
		"""
		if self.level < Const.PCG_GET_GEM_LEVEL:
			DEBUG_MSG( "���( %s )����С��PCG_GET_GEM_LEVEL�����ܼ���鱦ʯ��" % ( self.getName() ) )
			return False
		return True


	def gem_activateGem( self, entityID ):
		"""
		����鱦ʯϵͳ

		@param entityID : npc��id
		@type entityID : OBJECT_ID
		"""
		if self.isRoleTrainGemActive():
		#	self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
			return

		if self.money < csconst.GEM_ACTIVATE_COST:
			self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
		else :
			self.gemActive |= csdefine.GEM_ROLE_ACTIVE_FLAG


	def gem_charge( self, gold ):
		"""
		Define method.
		��������ʯ��ֵ

		@param value : Ԫ��
		@type value : UINT32
		"""
		if not self.isRoleTrainGemActive():
			HACK_MSG( "���( %s )���鱦ʯ��û������ܳ�ֵ������ʯ��" % ( self.getName() ) )
			self.base.gem_chargeCB( gold, False )
			return
		statusID = self.roleTrainGem.charge( gold * 180, self )	# Ŀǰ20��Ԫ��������1��Сʱ
		if statusID != csstatus.PET_TRAIN_CHARGE_SUCCESS:
			state = False
			self.statusMessage( statusID )
		else:
			state = True
			self.statusMessage( statusID, gold )
		self.base.gem_chargeCB( gold, state )

	def gem_startTrain( self, srcEntityID, trainType ):
		"""
		Exposed method.
		��ʼ����������ģʽ����ͨ�������̿������

		@param trainType : ����ģʽ
		@type trainType : UINT8
		"""
		if not self.hackVerify_( srcEntityID ):
			return

		if trainType not in [ csdefine.GEM_WORK_NORMAL, csdefine.GEM_WORK_HARD ]:
			HACK_MSG( "���( %s )ѡ��Ĵ�������( %i )����ȷ��" % ( self.getName(), trainType ) )
			return

		if not self.isRoleTrainGemActive():
			HACK_MSG( "���( %s )���鱦ʯ��û������ܿ�ʼ������" % ( self.getName() ) )
			return
		self.roleTrainGem.startTrain( trainType, self )


	def gem_stopTrain( self, srcEntityID ):
		"""
		Exposed method.
		ֹͣ������
		��ʼ�����󣬴˺����ᱻ����������û�����clientʱ�޵��ں���á�
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not self.isRoleTrainGemActive():
			HACK_MSG( "���( %s )���鱦ʯ��û�������ֹͣ������" % ( self.getName() ) )
			return
		self.roleTrainGem.update( self )
		self.roleTrainGem.stopTrain( self )


	def isRoleTrainGemActive( self ):
		"""
		�ж���Ҿ��鱦ʯ�Ƿ񼤻�
		"""
		return self.gemActive & csdefine.GEM_ROLE_ACTIVE_FLAG


	def gem_onLevelUp( self ):
		"""
		�������֪ͨ��֪ͨ������ʯ
		"""
		self.roleTrainGem.onRoleLevelUp( self )
		self.absorbableEXPLevelValue = 0


	def gem_derive( self, srcEntityID ):
		"""
		Exposed method.
		�ӱ�ʯ��ȡ����
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not self.isRoleTrainGemActive():
			HACK_MSG( "���( %s )���鱦ʯ��û������ɼ�ȡ���顣" % ( self.getName() ) )
			return
		if self.roleTrainGem.isInTrain():
			DEBUG_MSG( "���( %s )���ڴ����У����ܼ�ȡ����" % self.getName() )
			return
			
		# ������ȡ�ľ��鲻�ܳ����ȼ����辭��10% by ����
		value = self.roleTrainGem.exp
		absorbLevelMax = RLevelEXP.getEXPMax( self.level ) / 10
		if self.absorbableEXPLevelValue >= absorbLevelMax:
			self.statusMessage( csstatus.GEM_ROLE_LEVEL_EXP_MAX )
			return
		limitValue = absorbLevelMax - self.absorbableEXPLevelValue
		if value > limitValue: value = limitValue
		
		self.absorbableEXPLevelValue += value
		
		self.roleTrainGem.giveExp( self, value )


	def gem_hire( self, srcEntityID, index, remainTime ):
		"""
		Exposd method.

		������Ҿ��鱦ʯ

		@param index : ���õı�ʯ����,int8
		@param remainTime : �ͻ���������ɵı�ʯ����ʱ�䣬int64
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if self.isState( csdefine.ENTITY_STATE_DEAD ):
			self.statusMessage( csstatus.GEM_DEAD_CANT_HIRE )
			return
		if not self.isRoleTrainGemActive():
			HACK_MSG( "���( %s )���鱦ʯ��û����������þ��鱦ʯ��" % ( self.getName() ) )
			return
		if self.ptn_getComGemCount() + self.gem_getComGemCount() >= csconst.GEM_COUNT_UPPER:	# Ŀǰ��������ȡ5��
			self.statusMessage( csstatus.GEM_HIRE_FULL )
			return
		if index < csdefine.GEM_ROLE_COMMON_INDEX or index >= csdefine.GEM_ROLE_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER:
			return
		if remainTime < 3 * 3600 or remainTime > 24 * 3600:	# ��ʯ������ʱ������
			return
		if not self.payMoney( csconst.GEM_HIRE_PAY, csdefine.CHANGE_MONEY_GEM_HIRE ):
			DEBUG_MSG( "��ȡ���鱦ʯ�Ļ��Ѳ���" )
			return
		comGem = CommonExpGem( index )
		timerBegin = self.gem_getLimitTime( remainTime )
		comGem.timerID = self.addTimer( timerBegin, 0, ECBExtend.GEM_ROLE_TIME_LIMIT_CBID )
		limitTime = time.time() + timerBegin
		comGem.load( self, limitTime )

	def gem_endHire( self, srcEntityID, index ):
		"""
		Exposed method.
		��ֹ��ȡ
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not self.isRoleTrainGemActive():
			HACK_MSG( "���( %s )���鱦ʯ��û���" % ( self.getName() ) )
			return
		comGem = None
		for gem in self.roleCommonGem:
			if gem.index == index:
				comGem = gem
				break
		if comGem is None:	# ��Ҳ�û�����õ�ǰ�����ı�ʯ
			pass
		else:
			comGem.offload( self )


	def gem_updateTrain( self, srcEntitiID ):
		"""
		Exposed method.

		�ͻ���������´�������
		"""
		if not self.roleTrainGem.isInTrain():
			return
		self.roleTrainGem.update( self )


	def gem_getLimitTime( self, remainTime ):
		"""
		����ó�����ʱ�䡣

		����ű�ʯ�Ѿ���ȡ��ʱ��ﵽ�ñ�ʯ��ʱ���30%ʱ����50%�ļ��ʻ��Զ���ֹ��
		��������ʣ�µ�ʱ���������ߵ�δ��ȡ�б��С����û���ж�Ϊ��ֹ����ô��30%��
		ÿ�ۼ�����10%��ʱ�����һ�̣���50%�ļ��ʻ��Զ���ֹ����ʣ��ʱ��Ϊ0��������ֹ��ȡ��
		"""
		limitTime = remainTime * 0.3
		restTime = remainTime * 0.1
		count = 7	# ÿ�ۼ�����10%��ʱ�����һ�̣���50%�ļ��ʻ��Զ���ֹ
		while restTime > 0 and count > 0:
			count -= 1
			restTime *= random.random() > 0.5 and 1 or 0
			limitTime += restTime
		return limitTime


	def onRoleGemTimeLimit( self, controllerID, userData ):
		"""
		timer
		"""
		for gem in self.roleCommonGem:
			if gem.timerID == controllerID:
				gem.offload( self )
				break


	def gem_login( self ):
		"""
		��ҵ�¼
		"""
		if not self.isRoleTrainGemActive():
			return
		if self.roleTrainGem.isInTrain():
			self.roleTrainGem.update( self )


	def gem_getComGemCount( self ):
		"""
		�����ҵ�ǰ��ȡ�ľ��鱦ʯ����
		"""
		return len( self.roleCommonGem )

#
# $Log: not supported by cvs2svn $
#
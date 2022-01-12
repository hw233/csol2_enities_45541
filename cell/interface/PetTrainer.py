# -*- coding: gb18030 -*-
#
# $Id: PetTrainer.py,v 1.14 2008-09-05 01:39:51 zhangyuxing Exp $

"""
This module implements the pet entity.

2007/07/01: writen by huangyongwei
2007/10/24: according to new version documents, it is rewriten by huangyongwei
"""

import time

import csstatus
import csdefine
import csconst
import Const
from bwdebug import *
from PetFormulas import formulas
from PetGem import CommonGem
from LevelEXP import PetLevelEXP
from MsgLogger import g_logger
import BigWorld

import ECBExtend


class PetTrainer :
	def __init__( self ) :
		self.ptn_login()


	# ----------------------------------------------------------------
	# public methods for npc dialog
	# ----------------------------------------------------------------
	def ptn_dlgAllownActivateTrainGem( self ) :
		if self.level < Const.PCG_GET_GEM_LEVEL :
			return False
		return not self.isPetTrainGemActive()

	def ptn_questActiveTrainGem( self ) :	# ���񼤻���ﾭ��ʯ
		if self.isPetTrainGemActive():
			#self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
			return
		self.activateGem()
		self.statusMessage( csstatus.PET_GEM_OPEN_SUCCESS )

		# �����������ʱ����Ҽ���һ��Сʱ�Ĵ���ʱ�䡣
		self.roleTrainGem.charge( 3600.0, self )
		self.__trainGem.charge( 3600.0, self )

	def ptn_dlgBuyTrainGem( self, npcEntity ) :	# NPC������ﾭ��ʯ
		if self.isPetTrainGemActive():
			#self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
			return
		cost = formulas.getTrainGemActivateCost()
		if cost > self.money :
			self.statusMessage( csstatus.PET_GEM_OPEN_FAIL_LACK_MONEY )
		else :
			self.activateGem()
			self.payMoney( cost, csdefine.CHANGE_MONEY_DLGBUYTRAINGEM )
			self.statusMessage( csstatus.PET_GEM_OPEN_SUCCESS )


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def ptn_onFeedEXPResult( self, result, value ) :
		"""
		<Defined/>
		����ι������
		"""
		if result == csstatus.PET_TRAIN_FEED_SUCCESS :
			self.__trainGem.subtractEXP( value, self )
			self.questPetEvent( "feed" )
		else :
			self.statusMessage( result )
		self.pcg_releaseOperating_()


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def ptn_hireCommonGem( self, srcEntityID, index, remainTime ) :
		"""
		<Exposed/>
		������ó��ﾭ��ʯ

		@param index : ���õı�ʯ����,int8
		@param remainTime : �ͻ���������ɵı�ʯ����ʱ�䣬���ܳ���24Сʱ��int64
		"""
		if not self.hackVerify_( srcEntityID ) :
			return
		if self.isState( csdefine.ENTITY_STATE_DEAD ):
			self.statusMessage( csstatus.GEM_DEAD_CANT_HIRE )
			return
		if not self.isPetTrainGemActive() :
			HACK_MSG( "gems are not activated!" )
			return
		if self.ptn_getComGemCount() + self.gem_getComGemCount() >= csconst.GEM_COUNT_UPPER:
			self.statusMessage( csstatus.GEM_HIRE_FULL )
			return
		if index < csdefine.GEM_PET_COMMON_INDEX or index >= csdefine.GEM_PET_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER:
			HACK_MSG( "gem index out of range!" )
			return

		if remainTime < 3 * 3600 or remainTime > 24 * 3600:	# ��ʯ������ʱ������
			return
		if self.money < formulas.getCommonGemActicateCost() :
			self.statusMessage( csstatus.PET_GEM_ACTIVATE_FAIL_LACK_MONEY )
			return
		comGem = CommonGem( index )
		self.__commonGems.append( comGem )
		self.payMoney( formulas.getCommonGemActicateCost(), csdefine.CHANGE_MONEY_HIRECOMMONGEM )
		timerBegin = self.gem_getLimitTime( remainTime )
		timerID = self.addTimer( timerBegin, 0, ECBExtend.GEM_PET_TIME_LIMIT_CBID )
		comGem.setTimerID( timerID )
		limitTime = time.time() + timerBegin
		comGem.load( self, limitTime )

	def ptn_inactivateCommonGem( self, srcEntityID, index ) :
		"""
		<Exposed/>
		ȡ������ʯ����ȡ
		"""
		if not self.hackVerify_( srcEntityID ) :
			return
		if not self.isPetTrainGemActive():
			HACK_MSG( "gems are not activated!" )
			return
		if index < csdefine.GEM_PET_COMMON_INDEX or index >= csdefine.GEM_PET_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER:
			HACK_MSG( "gem index out of range!" )
			return
		comGem = None
		for gem in self.__commonGems:
			if gem.getIndex() == index:
				comGem = gem
				break
		if comGem is None:	# ��Ҳ�û�����õ�ǰ�����ı�ʯ
			pass
		else:
			comGem.offload( self )
			self.cancel( comGem.getTimerID() )
			self.__commonGems.remove( gem )

		#	self.statusMessage( scstatus.PET_GEM_INACTIVATE_SUCCESS )

		#	self.statusMessage( scstatus.PET_GEM_INACTIVATE_FAIL )

	# ---------------------------------------
	def ptn_flushTrain( self, srcEntityID ) :
		"""
		<Exposed/>

		���´�������
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.__trainGem.flush( self )


	def ptn_trainCharge( self, gold ) :
		"""
		Define method.

		��������ʯ��ֵ
		"""
		if not self.isPetTrainGemActive():
			HACK_MSG( "player( %s )'s gems are not activated!" % self.getName() )
			self.base.ptn_trainChargeCB( gold, False )
			return
		statusID = self.__trainGem.charge( formulas.getTrainTime( gold ), self )
		if statusID != csstatus.PET_TRAIN_CHARGE_SUCCESS:
			state = False
			self.statusMessage( statusID )
		else:
			state = True
			self.statusMessage( statusID, gold )
		self.base.ptn_trainChargeCB( gold, state )

	def ptn_stratTrain( self, srcEntityID, trainType ) :
		"""
		<Exposed/>
		��ʼ����
		��������д��:startTrain
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if not self.isPetTrainGemActive():
			HACK_MSG( "player( %s )'s gems are not activated!" % self.getName() )
			return
		if trainType not in [ csdefine.GEM_WORK_NORMAL, csdefine.GEM_WORK_HARD ]:
			HACK_MSG( "���( %s )ѡ��Ĵ�������( %i )����ȷ��" % ( self.getName(), trainType ) )
			return
		self.__trainGem.startTrain( trainType, self )
		try:
			g_logger.petStartTrainingsLog( self.databaseID, BigWorld.entities[srcEntityID].databaseID, trainType )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )


	def ptn_stopTrain( self, srcEntityID ) :
		"""
		<Exposed/>
		ֹͣ����
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if not self.isPetTrainGemActive():
			HACK_MSG( "player( %s )'s gems are not activated!" % self.getName() )
			return
		self.__trainGem.stopTrain( self )

	def ptn_feedPetEXP( self, srcEntityID, dbid, value ) :
		"""
		<Exposed/>
		ι������
		"""
		if not self.hackVerify_( srcEntityID ) : return
		gemValue = self.__trainGem.getEXP( self )
		if gemValue < value : value = gemValue
		if value <= 0 : return														# �������һ�㲻����֣����ǿͻ�����ƭ����˲����ظ���ֱ�Ӻ���
		if not self.pcg_lockOperation_() : return									# ��ס������ע�����õ�ÿ���������ڶ�Ҫ�ص���ptn_onFeedEXPResult��
		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :											# �����ι����ս����
			if actPet.etype == "MAILBOX" :											# ��ʱ�Ҳ��������ĳ���
				self.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_FAIL_NOT_EXIST, value )
			else :
				entity = actPet.entity
				if self.level + Const.PET_EXP_LEVEL_LIMIT_GAP > entity.level:
					entity.absorbEXP( value )										# ע���������ص���ptn_onFeedEXPResult
				elif self.level + Const.PET_EXP_LEVEL_LIMIT_GAP == entity.level :	# �պø�����ҵȼ���ֻ������
					expMax = PetLevelEXP.getEXPMax( entity.level )
					tempValue = expMax - entity.EXP
					if value > tempValue: value = tempValue
					entity.absorbEXP( value )	
					if entity.EXP >= expMax:
						self.ptn_onFeedEXPResult( csstatus.PET_TRAIN_LEVEL_LIMIT, tempValue )
				else :			# ����ȼ��������5�����ϲ���������
					self.ptn_onFeedEXPResult( csstatus.PET_TRAIN_LEVEL_LIMIT, value )
		else :
			if not self.pcg_petDict.has_key( dbid ):
				ERROR_MSG( "player( %s ) cannot find the pet( %i ) in pcg_petDict..." % ( self.getName(), dbid ) )
				return
			level = self.pcg_petDict.get( dbid ).level
			if self.level + Const.PET_EXP_LEVEL_LIMIT_GAP > level:		# ����ȼ��������5�����ϲ���������
				self.base.ptn_feedPetEXP( dbid, value )								# ע���������ص���ptn_onFeedEXPResult
			elif self.level + Const.PET_EXP_LEVEL_LIMIT_GAP == level:
				self.base.ptn_feedPetEXPNotLevel( dbid, value )
			else :
				self.ptn_onFeedEXPResult( csstatus.PET_TRAIN_LEVEL_LIMIT, value )

	def isPetTrainGemActive( self ):
		"""
		�жϳ��ﾭ��ʯ�Ƿ񼤻�
		"""
		return self.gemActive & csdefine.GEM_PET_ACTIVE_FLAG

	def activateGem( self ):
		"""
		�����ʯ
		"""
		self.gemActive |= csdefine.GEM_PET_ACTIVE_FLAG
		self.gemActive |= csdefine.GEM_ROLE_ACTIVE_FLAG
		self.statusMessage( csstatus.GEM_LOAD_COMMON ) #����������Ϊ�˱����������ͬ������ʾ

	def ptn_getComGemCount( self ):
		"""
		public
		��õ�ǰ�����ȡ�ľ���ӳɱ�ʯ����
		"""
		return len( self.__commonGems )

	def onPetGemTimeLimit( self, controllerID, userData ):
		"""
		������ó��ﾭ��ʯ��timer�ص�
		"""
		for gem in self.__commonGems:
			if gem.getTimerID() == controllerID:
				gem.offload( self )
				self.__commonGems.remove( gem )
				break

	def ptn_onLevelUp( self ):
		"""
		���ﱦʯϵͳ��ɫ����֪ͨ
		"""
		self.__trainGem.onRoleLevelUp( self )


	def ptn_login( self ):
		"""
		��ҵ�¼
		"""
		if not self.isPetTrainGemActive():
			return
		if self.__trainGem.isInTrain():
			self.__trainGem.flush( self )

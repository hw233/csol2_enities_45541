# -*- coding: gb18030 -*-
#
# $Id: PetTrainer.py,v 1.2 2008-08-01 11:27:31 wangshufeng Exp $

"""
this module implements pet cage interface.

2007/11/27: writen by huangyongwei
"""

import csstatus
import cschannel_msgs
import ShareTexts as ST
import csdefine
from PetFormulas import formulas
from LevelEXP import PetLevelEXP
import time
import sys

class PetTrainer :
	def __init__( self ) :
		pass

	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def ptn_feedPetEXP( self, dbid, value ) :
		"""
		����ι��
		"""
		epitome = self.pcg_getPetEpitome( dbid )
		if epitome is None :
			self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_FAIL_NOT_EXIST, value )
			return

		absorbLevelMax = PetLevelEXP.getEXPMax( epitome.getAttr( "level" ) ) / 10		# ������ȡ�ľ��鲻�ܳ����ȼ����辭��10%
		oldLevel = epitome.getAttr( "level" )
		absorbableEXPLevelValue = epitome.getAttr( "absorbableEXPLevelValue" )
		if absorbableEXPLevelValue >= absorbLevelMax:
			epitome.statusMessage( csstatus.PET_ABSORT_LEVEL_EXP_FULL )
			return
		limitValue = absorbLevelMax - absorbableEXPLevelValue
		if value > limitValue: value = limitValue

		tempDate = epitome.getAttr( "absorbDate" )
		date = time.localtime( tempDate )[ 0 : 3 ]				# ȡ��( ��, ��, �� )
		now = time.time()
		if cmp( date, time.localtime( now )[ 0 : 3 ] ) != 0:	# ���컹ûι��������
			expUpper = formulas.getAbsorbExpUpper( epitome.getAttr( "level" ) )
		else:
			expUpper = epitome.getAttr( "absorbableEXP" )
			if expUpper == 0:
				self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_LIMIT, value )
				return
		tempValue = value
		if tempValue > expUpper:
			tempValue = expUpper

		absorbableEXP = expUpper - tempValue
		absorbableEXPLevelValue += value

		def onUpdatePetAttrs( res ) :
			if res < 0 :
				self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_FAIL_UNKNOW, tempValue )
			elif res == 0 :
				self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_FAIL_NOT_EXIST, tempValue )
			else :
				self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_SUCCESS, tempValue )

		newLevel, newEXP = formulas.getAddedEXP( epitome.getAttr( "level" ), epitome.getAttr( "EXP" ), value )
		attrs = { "level" : newLevel, "EXP" : newEXP, "absorbableEXP" : absorbableEXP, "absorbDate" : now,"absorbableEXPLevelValue" : absorbableEXPLevelValue }
		epitome.updateByDict( attrs, self, onUpdatePetAttrs )

	def ptn_feedPetEXPNotLevel( self, dbid, value ) :
		"""
		����ι������������ by ����
		"""
		epitome = self.pcg_getPetEpitome( dbid )
		if epitome is None :
			self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_FAIL_NOT_EXIST, value )
			return

		tempDate = epitome.getAttr( "absorbDate" )
		date = time.localtime( tempDate )[ 0 : 3 ]				# ȡ��( ��, ��, �� )
		now = time.time()
		if cmp( date, time.localtime( now )[ 0 : 3 ] ) != 0:	# ���컹ûι��������
			expUpper = formulas.getAbsorbExpUpper( epitome.getAttr( "level" ) )
			self.absorbDate = time.time()						# ������ȡ������Ч��
		else:
			expUpper = epitome.getAttr( "absorbableEXP" )
			if expUpper == 0:
				self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_LIMIT, value )
				return
		expMax = PetLevelEXP.getEXPMax( epitome.getAttr( "level" ) )
		tempValue = expMax -  epitome.getAttr( "EXP" )
		if value <= tempValue:
			tempValue = value
		if tempValue > expUpper:
			tempValue = expUpper
		absorbableEXP = expUpper - tempValue

		def onUpdatePetAttrs( res ) :
			if res < 0 :
				self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_FAIL_UNKNOW, tempValue )
			elif res == 0 :
				self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_FAIL_NOT_EXIST, tempValue )
			else :
				self.cell.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_SUCCESS, tempValue )

		newEXP = epitome.getAttr( "EXP" ) + tempValue
		if newEXP >= expMax:
			self.statusMessage( csstatus.PET_TRAIN_LEVEL_LIMIT )
		attrs = { "EXP" : newEXP, "absorbableEXP":absorbableEXP, "absorbDate":now }
		epitome.updateByDict( attrs, self, onUpdatePetAttrs )

	def ptn_trainCharge( self, gold ):
		"""
		Exposed method.
		������ʯ��ֵ

		@param gold : �����Ԫ��
		@type gold : UINT32
		"""
		if self.getUsableGold() < gold:
			self.statusMessage( csstatus.PET_TRAIN_CHARGE_FAIL_LACK_GOLD )
			return

		self.freezeGold( gold )
		self.cell.ptn_trainCharge( gold )

	def ptn_trainChargeCB( self, gold, state ):
		"""
		Define method.
		������ʯ��ֵ�ص�

		@param gold : ��ֵ��Ԫ��ֵ
		@type gold : UINT32
		@param state : ��ֵ�ĵĽ�����Ƿ�ɹ�
		@type state : BOOL
		"""
		self.thawGold( gold )
		if state:
			self.payGold( gold, csdefine.CHANGE_GOLD_PTN_TRAINCHARGE )
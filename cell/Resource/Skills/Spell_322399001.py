# -*- coding: gb18030 -*-
"""
���㼼�� 2009-01-09 SongPeifang & LinQing
"""
import csstatus
import csdefine
import random
import sys
from Spell_Item import Spell_Item
from bwdebug import *
from Love3 import g_rewards
from VehicleHelper import getCurrVehicleID
import SkillTargetObjImpl

class Spell_322399001( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._validSunTime = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 			# ÿ��ĺϷ��չ�ԡʱ��
		self._fishingRange = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 ) 			# ���뺣�߶�Զ���Ե���
		self._escapeRate = float( dict[ "param4" ] if len( dict[ "param4" ] ) > 0 else 0.0 ) 		# �����ѹ��ļ���

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		receiver = caster
		a = random.random()
		if a <= 1 - self._escapeRate:
			# ����������
			awarder = g_rewards.fetch( csdefine.RCG_FISH, caster )
			kitbagState = receiver.checkItemsPlaceIntoNK_( awarder.items )
			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				# �����ռ䲻��װ��������
				receiver.statusMessage( csstatus.CIB_MSG_ITEMBAG_SPACE_NOT_ENOUGH )
				return
			awarder.award( caster, csdefine.ADD_ITEM_FISHING )
		else:
			# �ѹ����������ʾ������ѹ�
			receiver.statusMessage( csstatus.SKILL_FISH_RUN_AWAY )

		# ���㾭�齱��
		gainExp = int( 31.42 + 6.28 * pow( receiver.level, 1.2 ) )
		receiver.addExp ( gainExp, csdefine.CHANGE_EXP_FISHING )

		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		if caster.getState() == csdefine.ENTITY_STATE_FIGHT:
			caster.end_body_changing( caster.id, "" )	# ȡ������
			return csstatus.SKILL_USE_TELEPORT_ON_FIGHTING
		uid = caster.queryTemp( "item_using" )
		caster.setTemp( "current_yugan_index", uid )
		receiver = caster

		# ���״̬�²��������
		if receiver.vehicle or getCurrVehicleID( receiver ):
			return csstatus.SKILL_CAST_FISH_NO_VEHICLE

		# �ж��Ƿ��ڵ��������
		if len( receiver.entitiesInRangeExt( self._fishingRange, "SpecialHideEntity", receiver.position ) ) < 1:
			receiver.end_body_changing( receiver.id, "" )	# ȡ������
			return csstatus.SKILL_CAST_NOT_SUN_FISH_PLACE

		# �ж�����Ƿ�ʣ�е���ʱ��
		if not receiver.queryTemp( "has_fishing_time", False ):
			if receiver.getState() == csdefine.ENTITY_STATE_CHANGING:
				receiver.changeState( csdefine.ENTITY_STATE_FREE )	# ����Ϊ��ͨ״̬
				receiver.currentModelNumber == ""
			return csstatus.SKILL_CAST_NOT_SUN_FISH_TIME

		state = Spell_Item.useableCheck( self, caster, target)

		if caster.getState() == csdefine.ENTITY_STATE_CHANGING and \
			caster.currentModelNumber != 'fishing' and caster.currentModelNumber != '':
				return csstatus.SKILL_CAST_CANT_FISH_IN_BC

		if state == csstatus.SKILL_GO_ON:
			# ֪ͨ��������ģ�ͣ������ǵ���ģ��
			if caster.getState() != csdefine.ENTITY_STATE_CHANGING:
				caster.begin_body_changing( 'fishing', 1.0 )
		return state

	def updateItem( self , caster ):
		"""
		������Ʒʹ��
		"""
		Spell_Item.updateItem( self , caster )
		uid = caster.queryTemp( "current_yugan_index" )
		item = caster.getByUid( uid )
		# ���������Ʒ�������Զ�ʹ�ø���Ʒ
		if item is None:
			caster.statusMessage( csstatus.CIB_MSG_FISHING_ROD_BROKEN ) # ���ĥ�����أ��Ѿ�����ʹ���ˣ�����ֹͣ��
			caster.end_body_changing( caster.id, "" )					# ȡ������
		else:
			casterObj = SkillTargetObjImpl.createTargetObjEntity( caster )
			caster.useItem( caster.id, item.uid, casterObj )			# ����ʹ�ø���͵��㣬�������������Ч��

	def onSpellInterrupted( self, caster ):
		"""
		��ʩ�������ʱ��ʱ�򣬸ı����״̬Ϊ����״̬
		"""
		caster.removeTemp( "current_yugan_index" )
		Spell_Item.onSpellInterrupted( self, caster )
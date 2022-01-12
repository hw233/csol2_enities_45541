# -*- coding: gb18030 -*-
#



import csstatus
import cschannel_msgs
import ShareTexts as ST
import csdefine
import sys

class RoleGem:
	"""
	��Ҿ���ʯ
	"""
	def __init__( self ):
		"""
		"""
		pass

	def gem_charge( self, gold ):
		"""
		Exposed method.
		��Ҹ�������ʯ��ֵ

		@param gold : ��ֵ��Ԫ��ֵ
		@type gold : UINT32
		"""
		if self.getUsableGold() < gold:
			self.statusMessage( csstatus.PET_TRAIN_CHARGE_FAIL_LACK_GOLD )
			return

		self.freezeGold( gold )
		self.cell.gem_charge( gold )

	def gem_chargeCB( self, gold, state ):
		"""
		Define method.
		��Ҹ�����ʯ��ֵ�ص�

		@param gold : ��ֵ��Ԫ��ֵ
		@type gold : UINT32
		@param state : ��ֵ�ĵĽ�����Ƿ�ɹ�
		@type state : BOOL
		"""
		self.thawGold( gold )
		if state:
			self.payGold( gold, csdefine.CHANGE_GOLD_GEM_CHARGE )
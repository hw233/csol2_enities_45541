# -*- coding: gb18030 -*-

"""
�����NPCȫ��ʵ��������
"""

import Language
from bwdebug import *
import csdefine
import NPC


class LivingTrainer( NPC.NPC ):
	"""
	�����NPCȫ��ʵ�������� for cell��

	@ivar      attrSkills: �����б�
	@type      attrSkills dict
	"""

	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )

	def load( self, confSection ):
		"""
		��ȡ�����б������ļ�

		@param confSection: �����ļ���section
		@type  confSection: Language.PyDataSection
		@return: 		��
		"""
		NPC.NPC.load( self, confSection )	# �ȼ��ػ��������

	def validLearn( self, player, skillID ):
		"""
		�Ƿ��ѧĳ�������
		"""
		lvskill = player.livingskill
		if lvskill.has_key( skillID ) or len( lvskill ) >= csdefine.LIVING_SKILL_MAX:
			return False
		return True

	def validLevelUp( self, player, skillID ):
		"""
		�Ƿ������ĳ�������
		"""
		lvskill = player.livingskill
		isMaxLevel = player.liv_isMaxLevel( skillID )
		if lvskill.has_key( skillID ) and not isMaxLevel: return True
		return False
		
	def payMoney( self, player, skillID ):
		"""
		�������ܸ�Ǯ
		"""
		reqMoney = player.getReqLevelUpMoney( skillID )
		return player.payMoney( reqMoney, csdefine.CHANGE_MONEY_LIVING_LEVEL_UP_SKILL )
		
# livingTrainer.py

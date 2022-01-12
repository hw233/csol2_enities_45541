# -*- coding:gb18030 -*-

import BigWorld
from SpellBase import *

class Spell_TDBNotifyCure( Spell ):
	"""
	��ħ��սͳ���˺�������
	"""
	def __init__( self ):
		Spell.__init__( self )
		
	def springOnCure( self, caster, receiver, cureHP ):
		"""
		���������Ʋ�������ʱ�Ļص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		"""
		if caster.id == receiver.id:		# �����Լ���ͳ��
			return
		BigWorld.globalData["TaoismAndDemonBattleMgr"].recordCureData( caster.playerName, caster.getLevel(), caster.getCamp(), caster.base, caster.tongName, cureHP )
	
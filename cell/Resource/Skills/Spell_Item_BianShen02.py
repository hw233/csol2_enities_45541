# -*- coding: gb18030 -*-
#
# �����ܻ��� 2009-04-02 SPF
#

from SpellBase import *
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csdefine
import csconst
from VehicleHelper import getCurrVehicleID


class Spell_Item_BianShen02( Spell_ItemBuffNormal ):
	"""
	�����ܻ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemBuffNormal.__init__( self )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""

		# ���״̬�²��������
		if target.getObject().vehicle or getCurrVehicleID( target.getObject() ):
			return csstatus.SKILL_CAST_CHANGE_NO_VEHICLE

		# �жϽ�ɫ�Ƿ���������
		if target.getObject().actionSign( csdefine.ACTION_ALLOW_DANCE ):
			return csstatus.SKILL_CAST_CHANGE_NO_DANCE

		# �жϽ�ɫ�Ƿ��������
		if target.getObject().getState() == csdefine.ENTITY_STATE_DANCE or target.getObject().getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			return csstatus.SKILL_IN_FIGHT
		
		# �жϽ�ɫ�Ƿ���ͨ״̬
		if target.getObject().getState() != csdefine.ENTITY_STATE_FREE:
			return csstatus.SKILL_IN_FREE

		return Spell_ItemBuffNormal.useableCheck( self, caster, target)
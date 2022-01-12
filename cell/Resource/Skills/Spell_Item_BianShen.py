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

class Spell_Item_BianShen( Spell_ItemBuffNormal ):
	"""
	�����ܻ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemBuffNormal.__init__( self )
		self.spaceLimited = "fengming"

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		"""
		��������ʱ��ɾ�����߻��п����ָ�Ϊ��ָ�����긽��ʹ��
		self.param1 = dict[ "param1" ]
		positionStr = dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else '0, 0, 0'
		posArr = positionStr.replace( " ", "" ).split( "," )
		self.param2 = ( float( posArr[0] ), float( posArr[1] ), float( posArr[2] ) )
		self.param3 = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 )
		"""

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell_ItemBuffNormal.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		# ������ڶ�Ӧ������λ�ø�������ʹ�ñ���ֽ��
		if self.spaceLimited != "" and caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) != self.spaceLimited:
			return csstatus.CIB_MSG_ITEM_NOT_USED_IN_HERE

		# ���״̬�²��������
		if caster.vehicle or getCurrVehicleID( caster ):
			return csstatus.SKILL_CAST_CHANGE_NO_VEHICLE

		# �жϽ�ɫ�Ƿ���������
		if caster.actionSign( csdefine.ACTION_ALLOW_DANCE ):
			return csstatus.SKILL_CAST_CHANGE_NO_DANCE

		# �жϽ�ɫ�Ƿ��������
		if caster.getState() == csdefine.ENTITY_STATE_DANCE or caster.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			return csstatus.SKILL_IN_FIGHT
		
		# �жϽ�ɫ�Ƿ���������
		if caster.getState() == csdefine.ENTITY_STATE_FIGHT:
			return csstatus.SKILL_IN_FIGHT

		return Spell_ItemBuffNormal.useableCheck( self, caster, target)
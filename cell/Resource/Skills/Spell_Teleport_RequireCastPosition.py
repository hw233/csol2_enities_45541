# -*- coding: gb18030 -*-

from SpellBase import *
from Spell_Item import Spell_Item
from Spell_TeleportBase import Spell_TeleportBase
import csstatus
import csconst
import csarithmetic

class Spell_Teleport_RequireCastPosition( Spell_Item,Spell_TeleportBase ):
	"""
	���ͼ���,Ҫ����ָ��λ����Χʩ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_TeleportBase.__init__( self )
		self.source_map = "" #��ͼ����
		self.source_position = ( 0.0, 0.0, 0.0 ) #Ҫ��ʩ��λ��
		self.range = 0	#��ʩ��λ�õĺϷ�����
		self.object_map = ""
		self.object_position = ( 0.0, 0.0, 0.0 )
		self.object_direction = ( 0.0, 0.0, 0.0 ) #����
		Spell_Item.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell_TeleportBase.init( self, dict )
		self.source_map = dict["param1"]
		self.source_position = tuple( [ float( i ) for i in dict["param2"].split(" ") ] )
		self.range = 3.0
		self.object_map = dict["param3"]
		self.object_position = tuple( [ float( i ) for i in dict["param4"].split(" ") ] )
		self.object_direction = tuple( [ float( i ) for i in dict["param5"].split(" ") ] )
		
	def useableCheck( self, caster, target ) :
		"""
		"""
		map = caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if map != self.source_map:
			return csstatus.CIB_MSG_WRONG_POSITION
		distance = csarithmetic.distancePP3( self.source_position, caster.position )
		if distance > self.range:
			return csstatus.CIB_MSG_WRONG_POSITION
		
		state = Spell_TeleportBase.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
			
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if self.object_map in csconst.COPY_REVIVE_PREVIOUS:
			receiver.setCurPosRevivePos()
			
		receiver.gotoSpace( self.object_map, self.object_position, self.object_direction )

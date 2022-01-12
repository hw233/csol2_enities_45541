# -*- coding: gb18030 -*-
#


from SpellBase import *
from Skill_Normal import Skill_Normal
import csdefine
import random

class Skill_400026( Skill_Normal ):
	"""
	������������������ֵ�൱�ڣ�����+���ݣ�*1%��

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Skill_Normal.__init__( self )
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self._param = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0.0 ) 	
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		val = int( ( ownerEntity.strength + ownerEntity.dexterity ) * self._param )
		ownerEntity.damage_min_value += val
		ownerEntity.damage_max_value += val
		ownerEntity.calcDamageMin()
		ownerEntity.calcDamageMax()
		
	def detach( self, ownerEntity ):
		"""
		virtual method
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		val = int( ( ownerEntity.strength + ownerEntity.dexterity ) * self._param )
		ownerEntity.damage_min_value -= val
		ownerEntity.damage_max_value -= val
		ownerEntity.calcDamageMin()
		ownerEntity.calcDamageMax()
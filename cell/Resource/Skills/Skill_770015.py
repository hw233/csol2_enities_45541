# -*- coding: gb18030 -*-
#

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *

from SpellBase import *
from Skill_Normal import Skill_Normal


class Skill_770015( Skill_Normal ):
	"""
	��輼�� ��������ǿ��,����:���˼����˵ĳ�ս������������ļ������2%��
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param = 0


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self.param = int( float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  * 100.0 )


	def attach( self, ownerEntity ):
		"""
		virtual method
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.affectPropValue( "magic_double_hit_probability_value", self.param * ownerEntity.queryTemp( "vehicleJoyancyEffect", 0.0 ), "calcMagicDoubleHitProbability" )

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.affectPropValue( "magic_double_hit_probability_value", -self.param * ownerEntity.queryTemp( "vehicleJoyancyEffect", 0.0 ), "calcMagicDoubleHitProbability" )

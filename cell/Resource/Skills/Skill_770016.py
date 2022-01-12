# -*- coding: gb18030 -*-
#

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *

from SpellBase import *
from Skill_Normal import Skill_Normal


class Skill_770016( Skill_Normal ):
	"""
	��輼�� �̱���Ԫ:���˼����˵ĳ�ս������5%�Ļ������ʼӳɡ�
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
		self.param = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  * 100.0


	def attach( self, ownerEntity ):
		"""
		virtual method
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.affectPropValue( "corporeity_percent", self.param * ownerEntity.queryTemp( "vehicleJoyancyEffect", 0.0 ), "calcDynamicProperties" )


	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.affectPropValue( "corporeity_percent", -self.param * ownerEntity.queryTemp( "vehicleJoyancyEffect", 0.0 ), "calcDynamicProperties" )


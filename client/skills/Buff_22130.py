# -*- coding: gb18030 -*-

"""
BUFF�����ࡣ
"""
from bwdebug import *
from SpellBase import *
import BigWorld
import skills as Skill

class Buff_22130( Buff ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
#		target.switchFlyWater( True )

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
#		target.switchFlyWater( False )

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_22130()
		obj.__dict__.update( self.__dict__ )
		obj.param = data["param"]
		return obj
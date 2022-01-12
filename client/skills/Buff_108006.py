# -*- coding: gb18030 -*-
#
# $Id: Buff_108006.py,v 1.8 2010-07-17 04:08:27 pengju Exp $

"""
BUFF�����ࡣ
"""
from bwdebug import *
from SpellBase import *
import BigWorld
import skills as Skill
import math
import Math

class Buff_108006( Buff ):
	"""
	example:����֮�� BUFF	��ɫ�ڴ��ڼ䲻�ᱻ������ ���ᱻ��ҿ��ƣ� �������ģ��
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

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		yaw = 0
		if target.id == BigWorld.player().id:
			yaw = target.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			pos = target.position + direction
			ma = Math.Matrix()
			ma.setTranslate( pos ) 
			target.turnaround( ma, None)

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_108006()
		obj.__dict__.update( self.__dict__ )
		obj.param = data["param"]
		return obj

#
# $Log: not supported by cvs2svn $
#
#
# -*- coding: gb18030 -*-
#
# ʵ��ģ�͵�����edit by wuxo 2012-3-10

"""
BUFF�����ࡣ
"""


from SpellBase import Buff
from gbref import rds

class Buff_299035( Buff ):
	"""
	ģ������
	"""
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )
		self._scale = 1.0
		self._lastTime = 1.0
		self._endLastTime = 1.0
		self._modelScale =(1,1,1)
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )
		self._scale = float( dict[ "Param1" ] )
		self._lastTime = float( dict[ "Param2" ] )
		self._endLastTime = float( dict[ "Param3" ] )
		
	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		model = target.getModel()
		self._modelScale = model.scale
		if model:
			rds.effectMgr.scaleModel( model, (self._scale, self._scale,self._scale), self._lastTime )
		
	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		model = target.getModel()
		if model:
			rds.effectMgr.scaleModel( model, self._modelScale, self._endLastTime )
		
		
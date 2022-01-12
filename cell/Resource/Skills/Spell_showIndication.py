# -*- coding: gb18030 -*-

import csdefine
from SpellBase import SystemSpell


class Spell_showIndication( SystemSpell ) :
	"""
	显示屏幕中间的道具/技能使用提示
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		SystemSpell.__init__( self )
		self.indicationIds = []										# 提示的ID

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		self.indicationIds = [eval( idtId ) for idtId in dict["param1"].split(" ")]	# 获取提示ID

	def receive( self, caster, receiver ) :
		"""
		virtual method.
		技能实现的目的
		"""
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):		# 只对玩家施放（不包括宠物）
			return
			
		for idtIdList in self.indicationIds :
			receiver.client.showCastIndicator( idtIdList )

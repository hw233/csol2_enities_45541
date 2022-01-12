# -*- coding: gb18030 -*-


from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus
import random

from SpellBase import *

class Spell_drawTrap( Spell ):
	"""
	扔到陷阱里（油锅）
	"""
	def __init__( self ):
		Spell.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.radius = float( dict[ "param1" ] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		entityList = caster.entitiesInRangeExt( self.radius, "MonsterTrap", caster.position )		# 找到范围内的所有油锅
		usedIDList = caster.queryTemp( "usedIDList", [] )	# 已经用过的油锅，不再用
		for e in entityList:
			if e.id in usedIDList:
				entityList.remove( e )
		
		if len( entityList ) > 0:
			entity = random.choice( entityList )	# 随机选中一个油锅
			receiver.position = entity.position		# 把receiver扔到油锅中
			usedIDList.append( entity.id )
			caster.setTemp( "usedIDList", usedIDList )
#
# -*- coding: gb18030 -*-
#
# 制作卷轴配方使用

from bwdebug import *
from Spell_Item import Spell_Item
import random
import csstatus

MIN = 2
MAX = 5


class Spell_ItemScroll( Spell_Item ):
	"""
	使用
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
	
	def useableCheck( self, caster, target ):
		"""
		"""
		targetObject = target.getObject()
		if hasattr( targetObject, "sc_canLearnSkill" ):
			if not targetObject.sc_canLearnSkill():
				caster.statusMessage( csstatus.SKILL_SPELL_SCROLL_SKILL_FULL )
				return csstatus.SKILL_NO_MSG
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not caster:
			return
			
		# 只有在caster为real的时候才执行， 因为这个模块会被其他一些模块使用
		# 而往往其他模块会存在receiver.receiveOnReal( caster.id, self )导致receive调用时caster为ghost
		if not caster.isReal():
			return
		
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		raFixedAttr = []
		for k, v in item.getExtraEffect().items():
			raFixedAttr.append( (k,v) )
		
		# 在这里不管是自己还是别人施法 caster都是real因此可以这么做
		caster.sc_learnSkill( {"itemID":item.id, "raFixedAttr":raFixedAttr, "maxCount":random.randint(MIN,MAX),"quality":item.getQuality()} )


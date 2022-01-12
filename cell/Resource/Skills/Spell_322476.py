# -*- coding:gb18030 -*-

from bwdebug import *
from Spell_Magic import Spell_Magic

class Spell_322476( Spell_Magic ):
	"""
	涂毒箭
	
	射出带有毒素的箭，如果目标身上有流血效果，
	则使对方身上作用新的DEBUFF——剧毒，该技能效果将每5秒消耗一次对方的生命值。（法术伤害）
	"""
	def __init__( self ):
		Spell_Magic.__init__( self )
		self.param1 = 0		# 影响的技能，此技能产生的buff才能被影响
		self.bleedingBuffID = 0
		
	def init( self, data ):
		"""
		"""
		Spell_Magic.init( self, data )
		self.param1 = int( data["param1"] if len( data["param1"] ) > 0 else 0 )
		self.bleedingBuffID = int( data["param2"] if len( data["param2"] ) > 0 else 0 )
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		存在流血射击产生的流血buff才能接收剧毒buff
		"""
		buffIndexs = receiver.findBuffsByBuffID( self.bleedingBuffID )
		if not buffIndexs:
			return
		haveBleedingBuff = False
		for index in buffIndexs:
			buff = receiver.getBuff( index )
			if buff["skill"].getID() / 100000 != self.param1:	# 去掉buff index、去掉技能级别
				continue
			haveBleedingBuff = True
			
		if not haveBleedingBuff:
			return
		# 接收buff，receive()会自动判断receiver是否为realEntity
		# 流血buff和剧毒buff是同一个buff编号，存在规则：级别高的buff会替换级别低的buff
		Spell_Magic.receiveLinkBuff( self, caster, receiver )
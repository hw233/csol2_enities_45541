# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在配置的position位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *
import random
import string

class Spell_trapPosition( Spell ):
	"""
	系统技能
	生成一个AreaRestrictTransducer的entity(陷阱功能entity)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.lifetime = 0				# 陷阱销毁时间
		self.radius = 0.0				# 陷阱半径
		self.enterSpell = 0				# 进入陷阱施放的技能
		self.leaveSpell = 0				# 离开陷阱施放的技能
		self.positionList = []			# 创建陷阱的position list
		self.modelNumber =  ""			# 陷阱对应的模型(带光效的)

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.lifetime = int( dict[ "param1" ] )
		self.radius = float( dict[ "param2" ] )
		spellStr = str( dict["param3"] )
		self.enterSpell = int( spellStr.split(";")[0] )
		self.leaveSpell = int( spellStr.split(";")[1] )
		positionStr = str( dict[ "param4" ] )
		positionStrList = positionStr.split(";")
		for e in positionStrList:
			pos = e.split(",")
			self.positionList.append( tuple( (string.atof(pos[0]), string.atof(pos[1]), string.atof(pos[2])) ) )
		self.modelNumber = str( dict[ "param5" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		if receiver.isReal():
			dict = { "radius" : self.radius, "enterSpell" : self.enterSpell, "leaveSpell" : self.leaveSpell, "destroySpell" : self.leaveSpell, "modelNumber" : self.modelNumber, "lifetime" : self.lifetime, "uname" : self.getName() }
			index = random.randrange(len(self.positionList))
			trap = caster.createEntityNearPlanes( "AreaRestrictTransducer", self.positionList[index], (0, 0, 0), dict )
			trap.setTemp( "trapArea", { 0:'a',1:'b',2:'c',3:'d',4:'e' }.get(index) )		# 创建陷阱的下标0 1 2 3 4有5个下标，必须按顺序对应
			caster.setTemp("trapPosition", self.positionList[index])	# 创建陷阱的位置，用于AI走到这个position位置上
		else:	# 加入对ghost的支持。17:31 2009-1-16，wsf
			receiver.receiveOnReal( caster.id, self )

# -*- coding: gb18030 -*-
#
# $Id: RequireDefine.py,v 1.16 2008-08-21 03:53:49 kebiao Exp $

"""
���������
"""

import BigWorld
import Language
import csstatus
from bwdebug import *
import csdefine

class Require:
	def __init__( self ):
		"""
		���캯����
		"""
		pass

	def load( self, args ):
		"""
		���ַ�����Ϊ�������أ�

		@param args: ���ַ������������ɸ��������Լ�����
		@type  args: STRING
		"""
		pass

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������

		@param caster: ʩ����
		@type  caster: Entity
		@param skillInstance: ʹ�õļ���ʵ��
		@type  skillInstance: Skill
		"""
		return csstatus.SKILL_UNKNOW

	def pay( self, caster, skillInstance ):
		"""
		֧��������

		@param caster: ʩ����
		@type  caster: Entity
		@param skillInstance: ʹ�õļ���ʵ��
		@type  skillInstance: Skill
		"""
		pass

class RequireNone:
	"""
	��Ҫ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		pass

	def load( self, args ):
		"""
		���ַ�����Ϊ�������أ�

		@param args: do no thing
		@type  args: STRING
		"""
		pass

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������
		"""
		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		֧��������
		"""
		pass

class Mana( Require ):

	def __init__( self ):
		"""
		���캯����
		"""
		Require.__init__( self )
		self.mana = 0

	def load( self, args ):
		"""
		���ַ�����Ϊ�������أ�

		@param args: format: int
		@type  args: STRING
		"""
		self.mana = int( args )

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������

		ע��������������ڡ�ʹ�ü���ʱ����$1%�ļ��ʡ����ӡ�$2%�ķ������ġ�ʱ�����ֲ�һ����ȷ��
		��Ϊ����û�а취��ȷ��������ġ����ӡ�
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.mana + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.MP < val:
			TRACE_MSG( "mana not enough" )
			return csstatus.SKILL_OUTOF_MANA

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		֧��������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.mana + caster.popTemp( "changeMana_extra", 0 ) + extraVal[0] ) * ( 1 + caster.popTemp( "changeMana_perent", 0.0 ) + extraVal[1] ) + caster.popTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		if caster.queryTemp( "NOT_NEED_MANA", False ): val = 0
		caster.setMP( caster.MP - val )

	def getPay( self, caster, skillInstance ):
		"""
		��ȡ������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.mana + caster.popTemp( "changeMana_extra", 0 ) + extraVal[0] ) * ( 1 + caster.popTemp( "changeMana_perent", 0.0 ) + extraVal[1] ) + caster.popTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		return val

class PercentMana( Require ):
	"""
	�����ħ��ֵһ����������ħ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Require.__init__( self )
		self.manaPercent = 0

	def load( self, args ):
		"""
		���ַ�����Ϊ�������أ�

		@param args: format: int
		@type  args: STRING
		"""
		self.manaPercent = int( args ) / 100.0

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������

		ע��������������ڡ�ʹ�ü���ʱ����$1%�ļ��ʡ����ӡ�$2%�ķ������ġ�ʱ�����ֲ�һ����ȷ��
		��Ϊ����û�а취��ȷ��������ġ����ӡ�
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.manaPercent * caster.MP_Max + extraVal[0] + caster.queryTemp( "changeMana_extra", 0 ) ) * ( 1 + extraVal[1] + caster.queryTemp( "changeMana_perent", 0.0 ) ) + caster.queryTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		if caster.MP < val:
			TRACE_MSG( "mana not enough" )
			return csstatus.SKILL_OUTOF_MANA

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		֧��������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.manaPercent * caster.MP_Max + caster.queryTemp( "changeMana_extra", 0 ) + extraVal[0] ) * ( 1 + caster.queryTemp( "changeMana_perent", 0.0 ) + extraVal[1] ) + caster.queryTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		if caster.queryTemp( "NOT_NEED_MANA", False ): val = 0
		caster.setMP( caster.MP - val )

	def getPay( self, caster, skillInstance ):
		"""
		��ȡ������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.manaPercent * caster.MP_Max + caster.queryTemp( "changeMana_extra", 0 ) + extraVal[0] ) * ( 1 + caster.queryTemp( "changeMana_perent", 0.0 ) + extraVal[1] ) + caster.queryTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		return val

class Item( Require ):

	def __init__( self ):
		"""
		���캯����
		"""
		Require.__init__( self )
		self.itemID = 0
		self.itemAmount = 0

	def load( self, args ):
		"""
		���ַ�����Ϊ�������أ�

		@param args: format: int
		@type  args: STRING
		"""
		if "'" in args:

			param = args.split( "'" )
			self.itemID = int( param[0] )
			self.itemAmount = int( param[1] )

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������

		ע��������������ڡ�ʹ�ü���ʱ����$1%�ļ��ʡ����ӡ�$2%�ķ������ġ�ʱ�����ֲ�һ����ȷ��
		��Ϊ����û�а취��ȷ��������ġ����ӡ�
		"""
		if not caster.checkItemFromNKCK_( self.itemID, self.itemAmount ):
			return csstatus.SKILL_ITEM_NOT_EXIST
		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		֧��������
		"""
		amount = self.itemAmount
		caster.removeItemTotal( self.itemID, amount, csdefine.DELETE_ITEM_PAY )

	def getPay( self, caster, skillInstance ):
		"""
		��ȡ������
		"""
		return 0

class CombatCount( Require ):
	"""
	���ĸ񶷵���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Require.__init__( self )
		self.combatCount = 0

	def load( self, args ):
		"""
		���ַ�����Ϊ�������أ�

		@param args: format: int
		@type  args: STRING
		"""
		self.combatCount = int( args )

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.combatCount + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.combatCount < val:
			TRACE_MSG( "combatCount not enough" )
			return csstatus.SKILL_OUTOF_CombatCount

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		֧��������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.combatCount + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		caster.calCombatCount( -val )

	def getPay( self, caster, skillInstance ):
		"""
		��ȡ������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.combatCount + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		return val
		
class Vitality( Require ):
	"""
	��������ֵ
	"""

	def __init__( self ):
		"""
		���캯����
		"""
		Require.__init__( self )
		self.vitality = 0

	def load( self, args ):
		"""
		���ַ�����Ϊ�������أ�

		@param args: format: int
		@type  args: STRING
		"""
		self.vitality = int( args )

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������

		ע��������������ڡ�ʹ�ü���ʱ����$1%�ļ��ʡ����ӡ�$2%���������ġ�ʱ�����ֲ�һ����ȷ��
		��Ϊ����û�а취��ȷ��������ġ����ӡ�
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.vitality + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.energy < val:
			TRACE_MSG( "vitality not enough" )
			return csstatus.SKILL_OUTOF_VITALITY

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		֧��������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.vitality + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		caster.calEnergy( -val )

	def getPay( self, caster, skillInstance ):
		"""
		��ȡ������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.vitality + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		return val

class HP( Require ):
	"""
	��������ֵ
	"""

	def __init__( self ):
		"""
		���캯����
		"""
		Require.__init__( self )
		self.hp = 0

	def load( self, args ):
		"""
		���ַ�����Ϊ�������أ�

		@param args: format: int
		@type  args: STRING
		"""
		self.hp = int( args )

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������

		ע��������������ڡ�ʹ�ü���ʱ����$1%�ļ��ʡ����ӡ�$2%���������ġ�ʱ�����ֲ�һ����ȷ��
		��Ϊ����û�а취��ȷ��������ġ����ӡ�
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.hp + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.HP < val:
			TRACE_MSG( "HP not enough" )
			return csstatus.SKILL_OUTOF_HP

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		֧��������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.hp + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		caster.setHP( caster.HP - val )

	def getPay( self, caster, skillInstance ):
		"""
		��ȡ������
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.hp + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		return val

class RequireDefine( Require ):

	def __init__( self ):
		"""
		���캯����
		"""
		Require.__init__( self )
		self._requires = []

	def load( self, pyDat ):
		"""
		���ַ�����Ϊ�������أ�

		@param dictDat: python data
		"""
		reqs = \
		{
			0	     	:	Mana,
			1			:   Item,
			2			: 	PercentMana,
			3			:	CombatCount,
			4			:	Vitality,
			5			:	HP,
		}
		for i in xrange( len( pyDat ) ):
			dat = pyDat[ i ]
			instance = reqs[ dat[ "requireType" ] ]()
			instance.load( dat[ "value" ] )
			self._requires.append( instance )

	def validObject( self, caster, skillInstance ):
		"""
		У������Ƿ���������

		ע��������������ڡ�ʹ�ü���ʱ����$1%�ļ��ʡ����ӡ�$2%�ķ������ġ�ʱ�����ֲ�һ����ȷ��
		��Ϊ����û�а취��ȷ��������ġ����ӡ�
		"""
		for r in self._requires:
			state = r.validObject( caster, skillInstance )
			if state != csstatus.SKILL_GO_ON:
				return state
		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		֧��������
		"""
		for r in self._requires:
			r.pay( caster, skillInstance )

		for r in self._requires:
			if r.getPay( caster, skillInstance ) > 0:			
				# ����Ҫ����ħ�������һ�ξ�û��
				caster.detachNotNeedManaEffect()
				return

def newInstance( dictDat ):
	"""
	��ȡ����ʵ����
		���ַ�����Ϊ�������أ�

		@param dictDat: python data
	"""
	inst = RequireDefine()
	if dictDat:
		inst.load( dictDat )
	return inst



# -*- coding: gb18030 -*-
#
# $Id: Spell_Dispersion.py,v 1.26 2008-08-14 01:11:36 kebiao Exp $

"""
驱散法术。
"""

from SpellBase import *
from Resource import DispersionTable
import csdefine
import csstatus

class Spell_Dispersion( Spell ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		#self._dispelType = []
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		self._dispelAmount = int( dict.get( "param1" , 0 ) )			# 最多可驱散个数 DispelAmount
		#st = dict.readString( "param2" )						# 可驱散法术性质 良性 恶性...
		#for t in st.split(";"):
		#	if len( t ) <= 0: continue
		#	t = int( t )
		#	if t == 0:
		#		self._dispelType.append( csdefine.SKILL_EFFECT_STATE_BENIGN )
		#	elif t == 1:
		#		self._dispelType.append( csdefine.SKILL_EFFECT_STATE_MALIGNANT )
		#	elif t == 2:
		#		self._dispelType.append( csdefine.SKILL_RAYRING_EFFECT_STATE_BENIGN )
		#	elif t == 3:
		#		self._dispelType.append( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT )
		#self._dispelBuffType = section.readInt( "param3" )		# 可驱散的BUFF类别
		""" 作为基础 他只处理 BUFF的性质   至于驱散到具体的类型 应该去继承实现
		t = section.readInt( "param2" )
		self._dispellTable = DispersionTable.instance()[t]			# 可驱散法术列表 DispelTable
		"""
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method.
		接受法术之前所要做的事情
		"""
		# 磨损
		#caster.equipAbrasion()
		pass

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#处理沉默等一类技能的施法判断
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell.useableCheck( self, caster, target )

	def canDispel( self, caster, receiver, buffData ):
		"""
		可否驱散
		"""
		skill = buffData["skill"]
		"""
		if self._dispelBuffType != 0 and skill.getBuffType() != self._dispelBuffType:
			return False
		if skill.getEffectState() in self._dispelType and skill.getLevel() < self.getLevel():# 只能驱散比自己级别底的BUFF
			return True
		"""
		if skill.getLevel() < self.getLevel():# 只能驱散比自己级别底的BUFF
			if skill.cancelBuff( self._triggerBuffInterruptCode ):
				return True
		return False

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 驱散目标身上的buff
		rmb = []
		count = 0
		for index, buff in enumerate( receiver.getBuffs() ):
			if self.canDispel( caster, receiver, buff ):
				rmb.append( index )
				count += 1
				if count >= self._dispelAmount:
					break

		# 反向
		rmb.reverse()
		for index in rmb:
			receiver.removeBuff( index, self._triggerBuffInterruptCode )

class Spell_EffectDispersion( Spell ):
	"""
		战士有冰封驱散。 :1
		法师有眩晕驱散。 :2
		剑客有减速驱散。 :3
		射手有昏睡驱散。 :4
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		#self._dispelType = []
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		self._dispelAmount = int( dict.get( "param1" , 0 ) )			# 最多可驱散个数 DispelAmount
		"""
		驱散类型
		战士有冰封驱散。 :EFFECT_STATE_VERTIGO
		法师有眩晕驱散。 :EFFECT_STATE_VERTIGO
		剑客有减速驱散。 :EFFECT_STATE_VERTIGO
		射手有昏睡驱散。 :EFFECT_STATE_VERTIGO
		"""
		type = dict.get( "param2" , "" )
		if len( type ) > 0:
			self._effectType = eval( "csdefine." + type )
		else:
			self._effectType = -1

		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method.
		接受法术之前所要做的事情
		"""
		# 磨损
		#caster.equipAbrasion()
		pass

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#处理沉默等一类技能的施法判断
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		if self._effectType != csdefine.EFFECT_STATE_VERTIGO and caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if self._effectType != csdefine.EFFECT_STATE_SLEEP and caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if self._effectType != csdefine.EFFECT_STATE_HUSH_MAGIC and caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell.useableCheck( self, caster, target )

	def canDispel( self, caster, receiver, buffData ):
		"""
		可否驱散
		"""
		skill = buffData["skill"]
		if skill.getLevel() < self.getLevel():# 只能驱散比自己级别底的BUFF
			if skill.cancelBuff( self._triggerBuffInterruptCode ):
				return True
		return False

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.clearBuff( self._triggerBuffInterruptCode )


class Spell_DispelAndTeleport( Spell_Dispersion ) :
	"""
	驱散玩家的buff同时将玩家传送到某个指定位置，使用判断按照
	驱散技能的流程判断，不能驱散则不能传送
	"""
	def __init__( self ) :
		Spell_Dispersion.__init__( self )
		self.spaceName = ""
		self.position = None
		self.direction = None

	def init( self, dict ) :
		Spell_Dispersion.init( self, dict )
		self.spaceName = dict["param2"].strip()
		self.position = tuple( [ float( i ) for i in dict["param3"].split(" ") ] )
		self.direction = tuple( [ float( i ) for i in dict["param4"].split(" ") ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		Spell_Dispersion.receive( self, caster, receiver )
		receiver.gotoSpace( self.spaceName, self.position, self.direction )



# $Log: not supported by cvs2svn $
# Revision 1.25  2008/08/13 02:24:55  kebiao
# 修正BUFF中断失效问题
#
# Revision 1.24  2008/07/15 04:06:26  kebiao
# 将技能配置修改到datatool相关初始化需要修改
#
# Revision 1.23  2008/06/02 06:39:09  kebiao
# no message
#
# Revision 1.22  2008/05/28 05:59:47  kebiao
# 修改BUFF的清除方式
#
# Revision 1.21  2008/01/02 07:29:49  kebiao
# 调整技能部分结构与接口
#
# Revision 1.20  2007/12/20 09:09:23  kebiao
# 添加新的中断类型
#
# Revision 1.19  2007/12/18 04:15:42  kebiao
# 调整onReceiveBefore参数位置
#
# Revision 1.18  2007/12/17 01:36:36  kebiao
# 调整PARAM0为param1
#
# Revision 1.17  2007/12/13 01:47:26  kebiao
# 添加按BUFFTYPE驱散支持
#
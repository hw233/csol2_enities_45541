# -*- coding: gb18030 -*-
#
# $Id: Spell_Item.py,v 1.22 2008-08-13 07:55:41 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
import random
import csdefine
import csstatus
from bwdebug import *

class Spell_Item( Spell ):
	"""
	使用物品技能基础
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_ITEM

	def onSpellInterrupted( self, caster ):
		"""
		当施法被打断时的通知；
		打断后需要做一些事情
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Player(%s) cannot find the item form uid[%s]." %(caster.playerName, uid ) )
			return
		item.unfreeze()
		caster.removeTemp( "item_using" )
		Spell.onSpellInterrupted( self, caster )

	def setCooldownInUsed( self, caster ):
		"""
		virtual method.
		给施法者设置法术本身的cooldown时间 (技能使用后 吟唱开始时)

		@return: None
		"""
		Spell.setCooldownInUsed( self, caster )
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Player(%s) cannot find the item form uid[%s]." %(caster.playerName, uid ) )
			return
		item.onSetCooldownInUsed( caster )

	def setCooldownInIntonateOver( self, caster ):
		"""
		virtual method.
		给施法者设置法术本身的cooldown时间(技能吟唱结束时)

		@return: None
		"""
		Spell.setCooldownInIntonateOver( self, caster )
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Player(%s) cannot find the item form uid[%s]." %(caster.playerName, uid ) )
			return
		item.onSetCooldownInIntonateOver( caster )

	def use( self, caster, target ):
		"""
		virtual method.
		请求对 target/position 施展一个法术，任何法术的施法入口由此进。
		dstEntity和position是可选的，不用的参数用None代替，具体看法术本身是对目标还是位置，一般此方法都是由client调用统一接口后再转过来。
		默认啥都不做，直接返回。
		注：此接口即原来旧版中的cast()接口
		@param   caster: 施法者
		@type    caster: Entity

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.doOnUseSkill( self )	# 触发技能使用时的列表 处理其他导致 吟唱时间 或 XX 消耗的改变
		Spell.use( self, caster, target )

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 引导技能检测
		#根据策划需求 喝药不打断引导modify by wuxo2012-5-7
		#caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		
		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )
		
		self.onArrive( caster, target )
		#更新物品 只有物品成功使用之后才可以对物品的消减进行操作
		self.updateItem( caster ) #在这里写这个操作是因为此时可以保证caster为real,因为使用物品可能会对宠物等使用，因此不能使用receiver

	def updateItem( self , caster ):
		"""
		更新物品使用
		"""
		uid = caster.popTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Player(%s) cannot find the item form uid[%s]." %(caster.playerName, uid ) )
			return
		item.onSpellOver( caster )
		caster.removeTemp( "item_using" )

	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		主要是屏蔽信息，避免不能使用物品时提示使用技能
		"""
		# 防止其他原因导致的不可施法
		if caster.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
			if caster.getState() == csdefine.ENTITY_STATE_PENDING:
				return csstatus.CIB_MSG_PENDING_CANT_USE_ITEM
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		# 施法需求检查
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 施法者检查
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查目标是否符合法术施展
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		return csstatus.SKILL_GO_ON

# $Log: not supported by cvs2svn $
# Revision 1.21  2008/05/31 03:01:19  yangkai
# 物品获取接口改变
#
# Revision 1.20  2008/03/26 08:28:45  kebiao
# 修改错误提示信息
#
# Revision 1.19  2008/03/01 06:24:00  yangkai
# 物品系统对使用次数做了处理，调用接口onSpellOver
#
# Revision 1.18  2008/01/18 06:35:05  zhangyuxing
# 修改：移除物品方式改变
#
# Revision 1.17  2008/01/03 03:34:11  kebiao
# add:from bwdebug import *
#
# Revision 1.16  2007/12/18 09:32:43  kebiao
# 添加中断通知接口
#
# Revision 1.15  2007/12/18 09:23:33  kebiao
# 修改物品索引的判断方式
#
# Revision 1.14  2007/12/18 09:05:23  kebiao
# 调整中断接口
#
# Revision 1.13  2007/12/18 08:33:16  kebiao
# 添加吟唱中断 物品使用失败后解锁
#
# Revision 1.12  2007/12/18 07:49:45  kebiao
# 修改使用物品BUG 增加注释
#
# Revision 1.11  2007/12/11 08:36:48  kebiao
# 增加物品消耗判断
#
# Revision 1.10  2007/12/11 08:22:36  kebiao
# 修正一个BUG
#
# Revision 1.9  2007/12/11 06:35:13  kebiao
# 添加技能通知物品去冷却自身
#
# Revision 1.8  2007/12/04 08:31:07  kebiao
# 修改消耗方式
#
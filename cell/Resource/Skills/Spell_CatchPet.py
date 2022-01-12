# -*- coding: gb18030 -*-
#
# $Id: Spell_CatchPet.py,v 1.20 2008-07-04 03:50:57 kebiao Exp $

"""
"""

from SpellBase import *
import csstatus
import csdefine
import csconst
from Spell_Item import Spell_Item

class Spell_CatchPet( Spell_Item ):
	"""
	使用：抓获宠物
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
		self.isResetLevel = dict.get( "param2", 1 )	# 默认会重置宠物等级

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_MAGIC

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
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0 or caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			
		if caster.pcg_isFull():
			return csstatus.SKILL_MISSING_FULL_PET

		monsterScript = target.getObject().getScript()			# 将怪物和宠物的映射表改为让怪物配置中设置其映射的宠物( hyw -- 2008.10.28 )
		if monsterScript.mapPetID == "" :								# 如果怪物没有映射的宠物，则返回不能捕捉( hyw -- 2008.10.28 )
			return csstatus.SKILL_MISSING_NOT_CATCH_PET

		if caster.level < monsterScript.takeLevel:
			return csstatus.PET_CATCH_FAIL_LESS_TAKE_LEVEL

		if t.level - csconst.PET_CATCH_OVER_LEVEL > caster.level:
			return csstatus.SKILL_MISSING_NOT_CATCH_PET_LEVEL

		return Spell_Item.useableCheck( self, caster, target )

	def getCatchType( self ):
		"""
		获得捕获类型。19:22 2009-2-27，wsf
		"""
		return csdefine.PET_GET_CATCH

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		level = receiver.level
		if self.isResetLevel:
			needResetLevel = True
		else:
			needResetLevel = False
		caster.pcg_catchPet( receiver.className, level, receiver.modelNumber, self.getCatchType(), True, needResetLevel )
		receiver.destroy()

# $Log: not supported by cvs2svn $
# Revision 1.19  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.18  2008/05/26 08:02:39  huangyongwei
# 修改了等级判断
#
# Revision 1.17  2008/05/26 05:54:21  huangyongwei
# 添加了捕捉等级判断
#
# Revision 1.16  2008/04/01 05:22:59  zhangyuxing
# 招宠物等级调整为允许招和自己等级一样的宠物
#
# Revision 1.15  2008/02/29 04:03:56  kebiao
# 捕兽改为物品技能
#
# Revision 1.14  2008/02/01 02:46:11  kebiao
# 修正宠物攻击的怪物不能捕捉问题
#
# Revision 1.13  2008/01/09 06:40:49  kebiao
# 添加怪物所有权判断
#
# Revision 1.12  2008/01/09 04:11:50  kebiao
# 添加队伍判断
#
# Revision 1.11  2007/12/25 03:09:16  kebiao
# 调整效果记录属性为effectLog
#
# Revision 1.10  2007/12/25 01:45:50  kebiao
# 修改沉没属性
#
# Revision 1.9  2007/12/18 10:42:06  huangyongwei
# no message
#
# Revision 1.8  2007/12/12 07:32:43  kebiao
# 调整中断信息
#
# Revision 1.7  2007/12/12 04:20:30  kebiao
# 修改眩晕等状态判断
#
# Revision 1.6  2007/12/06 02:51:48  kebiao
# 填加判断当前是否允许施法的判定
#
# Revision 1.5  2007/12/05 02:11:41  kebiao
# 修改BUG
#
# Revision 1.4  2007/12/04 10:17:52  kebiao
# no message
#
# Revision 1.3  2007/12/04 09:24:33  kebiao
# no message
#
# Revision 1.2  2007/12/04 08:31:46  kebiao
# 修改错误
#
# Revision 1.1  2007/12/03 07:45:38  kebiao
# no message
#
#
# -*- coding: gb18030 -*-
#
# $Id: Spell_313100002.py,v 1.12 2008-04-16 08:26:45 zhangyuxing Exp $

"""
"""

from SpellBase import *
import csstatus
import csdefine

class Spell_313100002( Spell ):
	"""
	点火把
	启动火把类场景物件，播放动画，完成任务条件
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
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# 受术者对象，其中包括受术者的一些合法性判断
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# 施展目标类型，see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )
		
	def getIntonateTime( self , caster ):
		"""
		virtual method.
		获取技能自身的吟唱时间，此吟唱时间如果有必要，可以根据吟唱者决定具体的时长。

		@param caster:	使用技能的实体。用于以后扩展，如某些天赋会影响某些技能的默认吟唱时间。
		@type  caster:	Entity
		@return:		释放时间
		@rtype:			float
		"""
		return caster.queryTemp( "quest_box_intone_time", 0.0 )
		
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
		return csstatus.SKILL_GO_ON

	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None or entity.isDestroyed:
			return []
		return [ entity ]
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		# 施法者可能找不到 参见receiveOnReal接口
		if not caster:
			return
					
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		# 回调以让箱子自己执行某些事情，因为下面的方面与此方法的设计目的不一样，因此下面的方法不能取消
		receiver.onReceiveSpell( caster, self )
		
		#通知玩家此任务目标已经完成
		receiver.onIncreaseQuestTaskState( caster.id )
		
# $Log: not supported by cvs2svn $
# Revision 1.11  2007/12/27 02:00:39  phw
# method modified: getIntonateTime(), popTemp -> queryTemp
#
# Revision 1.10  2007/12/22 08:23:09  kebiao
# 修改导入模块
#
# Revision 1.9  2007/12/22 08:10:18  kebiao
# 因为该行为是固定的 所以强制了一些条件
#
# Revision 1.8  2007/12/22 03:26:01  kebiao
# 修正吟唱
#
# Revision 1.7  2007/12/22 01:06:12  phw
# method modified: receive(), 对receiver进行回调onReceiveSpell()
#
# Revision 1.6  2007/12/19 04:15:59  kebiao
# 调整onIncreaseQuestTaskState相关接口 去掉索引参数
#
# Revision 1.5  2007/12/19 04:03:46  kebiao
# no message
#
# Revision 1.4  2007/12/19 03:41:26  kebiao
# < 		receiver.onSetQuestTaskComplete( caster.id, 0 )
# to:
# > 		receiver.onIncreaseQuestTaskState( caster.id, 0 )
#
# Revision 1.3  2007/12/19 02:26:45  kebiao
# 添加：onSetTaskComplete完成某个任务目标
#
# Revision 1.2  2007/12/18 05:57:56  kebiao
# 覆盖了一些基础类接口， 因为此技能为固定情况下才会使用的东西不会有这些需求存在
#
# Revision 1.1  2007/12/18 04:16:30  kebiao
# no message
#
#
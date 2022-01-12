# -*- coding: gb18030 -*-
#
# $Id: Spell_Face.py,v 1.28 2009-07-29 07:55:41 pengju Exp $

"""
播放表情
2009.07.29: by pengju
"""
import csdefine
import csstatus
from SpellBase import *
from bwdebug import *

class Spell_Face( Spell ) :
	def __init__( self ) :
		Spell.__init__( self )
		self.__face = [] # 保存配置中的表情

	def init( self, dict ) :
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.__face.append( dict[ "param1" ] )
		if dict["param2"] != "" :
			self.__face.append( dict[ "param2" ] )

	def getType( self ) :
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_ACTION

	def useableCheck( self, caster, target ) :
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
		state = caster.getState()
		if state != csdefine.ENTITY_STATE_FREE or self.__face == caster.queryTemp("Temp_Face") : # 不允许在非空闲状态或正在播同样表情时播放
			return csstatus.SKILL_CAN_NOT_PLAY_FACE
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ) :
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		caster.curActionSkillID = self.getID()
		caster.playFaceAction( self.__face )

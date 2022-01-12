# -*- coding: gb18030 -*-
#
# $Id: EffectState.py,v 1.9 2008-05-20 06:41:56 kebiao Exp $

"""
技能效果性质
"""

import BigWorld
import Language
import csstatus
import csdefine
from bwdebug import *
from Domain_Fight import g_fightMgr

class EffectState:
	def __init__( self ):
		"""
		构造函数。
		"""
		self._effectState = csdefine.SKILL_EFFECT_STATE_NONE		# 该SKILL的状态：恶性、中庸(无状态)、良性
		self._enmity = 0											# 法术造成的敌意

	def init( self, dictDat ):
		"""
		以字符串作为参数加载；
		@param dictDat: 各字符串具体意义由各派生类自己定义
		@type  dictDat: STRING
		"""
		try:
			self._enmity = dictDat[ "Enmity" ]  #int type
		except:
			self._enmity = 0

		try:
			self._effectState = dictDat[ "EffectState" ] #int type
		except:
			self._effectState = 0

	def getEffectState( self ):
		"""
		获取技能效果状态
		"""
		return self._effectState

	def isRayRingEffect( self ):
		"""
		是否为光环效果
		"""
		return self._effectState in [ csdefine.SKILL_RAYRING_EFFECT_STATE_BENIGN, csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ]

	def isBenign( self ):
		"""
		virtual method.
		判断法术效果是否为良性
		"""
		return self._effectState in [ csdefine.SKILL_EFFECT_STATE_BENIGN, csdefine.SKILL_RAYRING_EFFECT_STATE_BENIGN ]

	def isMalignant( self ):
		"""
		virtual method.
		判断法术效果是否为恶性
		"""
		return self._effectState in [ csdefine.SKILL_EFFECT_STATE_MALIGNANT, csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ]

	def isNeutral( self ):
		"""
		virtual method.
		判断法术效果是否是中性技能
		"""
		return self._effectState == csdefine.SKILL_EFFECT_STATE_NONE
		
	def canCancel( self ):
		"""
		virtual method.
		判断当前法术是否允许取消
		"""
		return self._effectState == csdefine.SKILL_EFFECT_STATE_BENIGN		# 只有良性效果才能取消

	def getEnmity( self ):
		"""
		获得仇恨
		"""
		return self._enmity

	def receiveEnemy( self, caster, receiver ):
		"""
		一个法术生效后向所有对受术者有意见的怪物仇恨列表添加施法者的仇恨
		如果受术者是怪物直接添加本技能BUFF的仇恨值
		@param   caster: 施法者，如果没有施法者则为None
		@type    caster: Entity
		@param receiver: 受术者
		@type  receiver: Entity
		"""
		if self._effectState == csdefine.SKILL_EFFECT_STATE_NONE or \
			not hasattr( receiver, "getState" ) or receiver.getState() == csdefine.ENTITY_STATE_DEAD or \
			not hasattr( caster, "getState" ) or caster.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if self.isBenign():
				receiver.cureToEnemy( caster , self._enmity )
		else:
			if self.isMalignant():
				g_fightMgr.buildEnemyRelation( receiver, caster )
				
				if caster.isEntityType( csdefine.ENTITY_TYPE_PET ) :
					owner = caster.getOwner()
					g_fightMgr.buildEnemyRelation( receiver, owner.entity )


#
# $Log: not supported by cvs2svn $
# Revision 1.7  2008/04/17 07:29:16  kebiao
# 调整战斗列表相关BUG 如 宠物攻击 角色不进入战斗状态，修正
# BUFF增益技能和治疗列表的关系
#
# Revision 1.6  2008/04/15 07:07:12  kebiao
# 修改战斗列表相关
#
# Revision 1.5  2008/01/15 04:14:05  kebiao
# 添加宠物攻击时，怪物也对主人产生仇恨
#
# Revision 1.4  2007/12/20 07:14:46  kebiao
# 添加光环效果判断
#
# Revision 1.3  2007/12/14 03:28:22  kebiao
# 修改添加仇恨接口中角色的判断方式
#
# Revision 1.2  2007/11/20 08:19:26  kebiao
# 战斗系统第2阶段调整
#
# Revision 1.1  2007/07/20 06:53:14  kebiao
# 技能效果
#
#
#

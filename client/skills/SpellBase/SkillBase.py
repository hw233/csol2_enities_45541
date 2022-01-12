# -*- coding: gb18030 -*-
#
# $Id: SkillBase.py,v 1.16 2008-08-06 06:09:32 qilan Exp $

"""
技能（包括被动技能）、Buff的基础类。
"""
import BigWorld
import csstatus
import csdefine
from SpellPose import SpellPose
from event.EventCenter import *
from gbref import rds

class SkillBase:
	def __init__( self ):
		self.pose = 0				    # 技能动作效果
		self._datas = {}
		self._uid = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			引用一份python 字典数据
		@type dict:				python dict， like {"key":value,...}
		"""
		self._datas = dict
		self.pose = SpellPose()

	def getID( self ):
		return self._datas["ID"]

	def getUID( self ):
		return self._uid

	def getName( self ):
		return self._datas["Name"]

	def getLevel( self ):
		return self._datas["Level"]

	def getMaxLevel( self ):
		"""
		获取此技能的最大等级

		@return: int
		"""
		return self._datas["MaxLevel"]

	def getType( self ):
		"""
		获得技能类型。
		"""
		return self._datas["Type"]

	def setUID( self, uid ):
		"""
		uid禁止被手动设置，
		"""
		self._uid = uid

	def getIcon( self ):
		return rds.spellEffect.getIcon( self.getID() )

	def getDescription( self ):
		return self._datas["Description"]

	def getPosture( self ) :
		"""
		获取需求的心法
		"""
		return csdefine.ENTITY_POSTURE_NONE

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return csstatus.SKILL_UNKNOW

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "id" : self.getID(), "param" : None, "uid" : self.getUID() }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		return self

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		接受技能处理

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#这里会出错误的原因是 在服务器上一个entity对另一个entity施法 服务器上是看的到施法者的
				#而客户端可能会因为某原因 如：网络延迟 而在本机没有更新到AOI中的那个施法者entity所以
				#会产生这种错误 written by kebiao.  2008.1.8
				return

		# 回调伤害信息 不一定伤害到HP 可能是0 被闪躲了 但仍然算伤害
		target.onReceiveDamage( casterID, self, damageType, damage  )
		# 动作光效部分
		self._skillAE( player, target, caster, damageType, damage  )
		# 通知伤害统计模块
		rds.damageStatistic.receiveDamage( self, caster, target, damageType, damage  )

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		技能产生伤害时的动作效果等处理
		@param player:			玩家自己
		@type player:			Entity
		@param target:			Spell施放的目标Entity
		@type target:			Entity
		@param caster:			Buff施放者 可能为None
		@type castaer:			Entity
		@param damageType:		伤害类型
		@type damageType:		Integer
		@param damage:			伤害数值
		@type damage:			Integer
		"""
		pass




# $Log: not supported by cvs2svn $
# Revision 1.15  2008/08/06 03:31:16  kebiao
# 调整receiveDamage接口参数 skill.receiveSpell 去掉skillID
#
# Revision 1.14  2008/08/05 02:02:15  qilan
# 将函数_receiveDamageAE()改名为_SkillAE()
# 去掉系统信息相关的两个函数_receiveDamageSysInfo()/_receiveDamageFlyText()
# 注：伤害系统信息放到受法者的entity中
#
# Revision 1.13  2008/07/22 08:54:35  qilan
# method modify：_receiveDamageSysInfo。

#
# Revision 1.12  2008/07/22 07:08:42  qilan
# method modify：_receiveDamageSysInfo。玩家A攻击玩家B，假如B躲闪了A的攻击，战斗信息提示为A躲闪了B的攻击。修改方式：将“你闪躲了XX的XX”和“XX闪躲了你的XX”位置调换
#
# Revision 1.11  2008/07/21 03:04:31  huangyongwei
# caster.pcg_getOutPet(),
# 改为
# caster.pcg_getActPet(),
#
# Revision 1.10  2008/07/15 06:54:32  kebiao
# 技能参数统一使用section 因为python变量会产生大量的内存，Language.section
# 是C结构存储 将会降低内存消耗
#
# Revision 1.9  2008/07/09 01:33:35  kebiao
# 添加伤害回调函数
#
# Revision 1.8  2008/07/08 09:20:09  yangkai
# 修正了 光效配置加载方式
#
# Revision 1.7  2008/07/04 01:06:43  zhangyuxing
# 怪物死亡后，不在提示信息
#
# Revision 1.6  2008/06/30 06:20:09  kebiao
# 修正    self._receiveDamageAE( player, target, caster, param1, param2, skillID )
# UnboundLocalError: local variable 'caster' referenced before assignment
#
# Revision 1.5  2008/04/01 01:11:54  kebiao
# 增加角色受攻击时的 伤害显示
#
# Revision 1.4  2008/03/31 09:05:00  kebiao
# 修改receiveDamage和通知客户端接受某技能结果分开
# 技能通过receiveSpell通知客户端去表现，支持各技能不同的表现
#
# Revision 1.3  2008/03/18 07:52:11  kebiao
# 修正了宠物攻击的相关提示信息
#
# Revision 1.2  2008/02/28 08:33:24  kebiao
# 因为skill技能和BUFF也会产生伤害导致信息提示,因此把部分接口转移到skillbase
# 作为虚接口
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# 调整技能结构，目录结构
#
#

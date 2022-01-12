# -*- coding: gb18030 -*-
#
# $Id: Skill_RandomDodge.py,v 1.2 2008-02-28 08:25:56 kebiao Exp $

"""
"""
from Function import newUID
from SpellBase import *
from Skill_Normal import Skill_Normal

class Skill_RandomDodge( Skill_Normal ):
	"""

	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Skill_Normal.__init__( self )
		self._param = 0
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )

	def springOnCombatCalc( self, caster, receiver, skill ):
		"""
		virtual method.
		在战斗计算时...；意思是每当被施展的技能到达目标对象时将要进入战斗计算，都会调用attach在“到达时被触发”的技能列表中的每一个技能的此方法。

		适用于：当被近身普通攻击或者近身攻击技能攻击时，闪避加值+40
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   skill: 技能实例
		@type    skill: Entity
		"""
		pass
			
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.HP_Max_value += self._param[0]
		ownerEntity.calcHPMax()
		ownerEntity.appendAttackerCombatCalc( self )
		
	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.HP_Max_value -= self._param[0]
		ownerEntity.calcHPMax()
		ownerEntity.removeAttackerCombatCalc( self.getUID() )
		
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。
		
		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self._param }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		obj = Skill_RandomDodge()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
			
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/08/23 01:53:03  kebiao
# 随机技能
#
# 
#
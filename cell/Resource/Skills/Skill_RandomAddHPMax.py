# -*- coding: gb18030 -*-
#
# $Id: Skill_RandomAddHPMax.py,v 1.2 2007-08-23 01:32:36 kebiao Exp $

"""
"""
from Function import newUID
from SpellBase import *
from Skill_Normal import Skill_Normal

class Skill_RandomAddHPMax( Skill_Normal ):
	"""
	1001	生命上限 +$1	150	50	10.00%	50	90

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
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.MP_Max_value += self._param
		ownerEntity.calcMPMax()
		
	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.MP_Max_value -= self._param
		ownerEntity.calcMPMax()
		
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
		obj = Skill_RandomAddHPMax()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
			
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/08/15 04:58:55  kebiao
# 随机技能
#
# 
#
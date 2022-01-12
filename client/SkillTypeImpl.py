# -*- coding: gb18030 -*-
#
# $Id: SkillTypeImpl.py,v 1.1 2007-06-27 02:05:01 phw Exp $

"""
设计思路：
	1.cell/base/client/db有各自的SkillTypeImpl.py模块，此模块为FIXED_DICT SKILL的实现模块；
	2.各模块根据实际需要去实现 getDictFromObj()、createObjFromDict()、getDictFromObj() 方法；
	3.各模块实现时必须考虑数据在各部份中传输时的一致性，即执行cell -> base或db -> base等传输时，能保证数据的还原；
"""
from bwdebug import *
import skills

class SkillTypeImpl:
	"""
	实现cell部份的skill数据创建、还原
	"""
	def __init__( self ):
		self.defaultValue = { "id" : 0, "uid" : 0, "param" : None }	# 用来表示没有技能的默认值
		
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		# 如果obj为None，则表示其没有附上skill，为了使FIXED_DICT能正常保存（如果有必要），我们返回id值为0的字典
		if obj is None:
			return self.defaultValue
		return obj.addToDict()
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		# 如果skillID为0，则我们认为其没有附上skill，因此直接返回None
		if dict["id"] == 0:
			return None
			
		try:
			sk = skills.getSkill( dict["id"] )
		except KeyError:
			ERROR_MSG( "skill %i not found." % dict["id"] )
			return None
		
		skill = sk.createFromDict( dict )
		if dict["uid"] > 0: 
			skill.setUID( dict["uid"] ) 
						
		return skill
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		# 我假设（且也只允许）这个方法只有在服务器传送数据过来的时候才调用，
		# 我认为服务器的数据一定是正确的，因此我直接返回True
		return True


# 自定义类型实现实例
instance = SkillTypeImpl()


# SkillTypeImpl.py

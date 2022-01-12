# -*- coding: gb18030 -*-
import Role
import weakref


"""
Role 的组件类接口，组件类是用于将Role的职责分散并归类而专门设定的类。这些组件类用于将目前杂乱无章的Role代码
按照职责相关度归类。如果Role将某个方法代理给某一个组件类，那么，以后对此方法的相关修改应该在组件类中实施，
以求实现组件类内部的高内聚。 by mushuang
"""


class RoleComponent( object ):
	def __init__( self, role ):
		assert isinstance( role, Role.Role ), "Role instance is needed!"
		
		self.__roleRef = weakref.ref( role ) # 这里必须做弱引用，以免内存泄漏，目前引擎的python解析器不支持回收循环引用的对象
		
	@property
	def role( self ):
		"""
		只读属性，所有对Role的引用必须通过此属性，否则无法提供必要的运行时检查
		"""
		role = self.__roleRef()
		assert role, "Role instance is destroyed unexpectedly!"
		
		return role
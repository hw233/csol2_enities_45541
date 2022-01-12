# -*- coding: gb18030 -*-

class ZhengDaoInterface:
	"""
	证道系统接口
	"""
	def __init__( self ):
		"""
		"""
		pass

	def wieldDaofa( self, daofa ):
		"""
		define method
		装备道法
		"""
		self.equipedDaofa.append( daofa )
		daofa.wield( self )

	def unwieldDaofa( self, daofa ):
		"""
		define method
		卸载道法
		"""
		for df in self.equipedDaofa:
			if df.getUID() == daofa.getUID():
				daofa.tmpExtra = df.tmpExtra
				self.equipedDaofa.remove(df)
		daofa.unwield( self )

# -*- coding: gb18030 -*-

class ZhengDaoInterface:
	"""
	֤��ϵͳ�ӿ�
	"""
	def __init__( self ):
		"""
		"""
		pass

	def wieldDaofa( self, daofa ):
		"""
		define method
		װ������
		"""
		self.equipedDaofa.append( daofa )
		daofa.wield( self )

	def unwieldDaofa( self, daofa ):
		"""
		define method
		ж�ص���
		"""
		for df in self.equipedDaofa:
			if df.getUID() == daofa.getUID():
				daofa.tmpExtra = df.tmpExtra
				self.equipedDaofa.remove(df)
		daofa.unwield( self )

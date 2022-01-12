# -*- coding: gb18030 -*-
import Role
import weakref


"""
Role �������ӿڣ�����������ڽ�Role��ְ���ɢ�������ר���趨���ࡣ��Щ��������ڽ�Ŀǰ�������µ�Role����
����ְ����ضȹ��ࡣ���Role��ĳ�����������ĳһ������࣬��ô���Ժ�Դ˷���������޸�Ӧ�����������ʵʩ��
����ʵ��������ڲ��ĸ��ھۡ� by mushuang
"""


class RoleComponent( object ):
	def __init__( self, role ):
		assert isinstance( role, Role.Role ), "Role instance is needed!"
		
		self.__roleRef = weakref.ref( role ) # ��������������ã������ڴ�й©��Ŀǰ�����python��������֧�ֻ���ѭ�����õĶ���
		
	@property
	def role( self ):
		"""
		ֻ�����ԣ����ж�Role�����ñ���ͨ�������ԣ������޷��ṩ��Ҫ������ʱ���
		"""
		role = self.__roleRef()
		assert role, "Role instance is destroyed unexpectedly!"
		
		return role
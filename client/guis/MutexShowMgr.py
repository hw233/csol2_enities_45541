# -*- coding: gb18030 -*-
#
# written by ganjinxing 2010-05-24
#
# ���ⴰ�ڹ�����������Ĵ�����ӵ�һ�������ķ��顣���磺
# ����A,B,C,D֮���ǻ���ģ����ڴ�������ʵ��ʱ����
# addMutexRoot ���� addRootToMutexGroups �ӿڽ�ʵ�����
# ���������м��ɡ����뽫���ڴӻ�������ȥ����Ӧ����
# removeMutexPyGui �ӿڡ�
# ע�⣺Ŀǰ��֧�ּ̳���RootGUI�Ĵ���֮��Ļ��⡣
# ʾ�����£�
#
# class A :
#	def __init__( self ) :
#		...
#		rds.mutexShowMgr.addMutexRoot( self, "mutexGroup0" )
#		...

# class B :
#	def __init__( self ) :
#		...
#		rds.mutexShowMgr.addMutexRoot( self, "mutexGroup0" )
#		...
#
# C��Dʵ��Ҳ���ϣ�����A��B��C��D�ͱ���ӵ���һ����ͬ�Ļ��������
# �����κ�һ����ʾ���ᴥ�����������������ڵĲ�����


from Weaker import WeakSet
from AbstractTemplates import Singleton


class MutexShowMgr( Singleton ) :

	def __init__( self ) :
		self.__mutexGroups = {}


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addMutexRoot( self, pyRoot, groupID ) :
		"""
		���һ��RootUI��������
		@param		pyRoot	: �ű���UIʵ��
		@param		groupID	: �������ʶ
		@type		groupID	: int or str
		"""
		mutexGroup = self.__mutexGroups.get( groupID )
		if mutexGroup is not None :
			mutexGroup.add( pyRoot )
		else :
			mutexGroup = WeakSet()
			mutexGroup.add( pyRoot )
			self.__mutexGroups[ groupID ] = mutexGroup
		if hasattr( pyRoot, "mtxMgr_mutexGroups" ) :
			pyRoot.mtxMgr_mutexGroups.add( groupID )
		else :
			pyRoot.mtxMgr_mutexGroups = set( [ groupID, ] )
			pyRoot.onBeforeShow.bind( self.__onBeforeRootShow )				# �󶨴�����ʾ�¼�

	def addRootToMutexGroups( self, pyRoot, groupList ) :
		"""
		@param		pyRoot	: �ű���UIʵ��
		@param		groupID	: �������ʶ
		@type		groupID	: list of int or str
		"""
		for groupID in groupList :
			self.addMutexRoot( pyRoot, groupID )

	def removeMutexRoot( self, pyRoot, groupID ) :
		"""
		@param		pyRoot	: �ű���UIʵ��
		@param		groupID	: �������ʶ
		@type		groupID	: int or str
		"""
		mutexGroup = self.__mutexGroups.get( groupID )
		if mutexGroup and pyRoot in mutexGroup :
			mutexGroup.remove( pyRoot )
			pyRoot.mtxMgr_mutexGroups.remove( groupID )
			if not len( pyRoot.mtxMgr_mutexGroups ) :
				del pyRoot.mtxMgr_mutexGroups


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onBeforeRootShow( self, pyRoot ) :
		"""
		������ʾ֮ǰ����
		"""
		self.__doRootMutexShow( pyRoot )

	def __doRootMutexShow( self, pyRoot ) :
		"""
		ĳ��������ʾʱ��ִ�д������ڻ�����Ļ������
		"""
		for groupID in pyRoot.mtxMgr_mutexGroups :
			mutexGroup = self.__mutexGroups.get( groupID )
			if mutexGroup and pyRoot in mutexGroup :
				for pyMutexUI in mutexGroup :
					if pyMutexUI.visible and pyMutexUI != pyRoot :
						pyMutexUI.hide()
			elif mutexGroup is None  :
				raise IndexError( "No such group of No: %s!" % groupID )
			else :
				raise ValueError( "%s is not in group %s !" % ( str( pyRoot ), groupID ) )


mutexShowMgr = MutexShowMgr()

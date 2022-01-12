# -*- coding: gb18030 -*-
#
# $Id: ITool.py,v 1.1 2008-08-01 02:11:10 huangyongwei Exp $
#
"""
implement tool's interface
2008/07/29: created by huangyongwei
"""

from AbstractTemplates import AbstractClass

# --------------------------------------------------------------------
# ע�⣺��ӵ��������еĹ��߱���ʵ�����µ� ITool �ӿ�
# --------------------------------------------------------------------
class ITool( AbstractClass ) :
	__abstract_methods = set()

	def __init__( self ) :
		"""
		ǿ��ʵ�ֽӿ�
		"""
		pass


	# ----------------------------------------------------------------
	# virtual methods
	# ----------------------------------------------------------------
	def getCHName( self ) :
		"""
		��ȡ���ߵ���������
		"""
		return ""

	# -------------------------------------------------
	def getHitUIs( self, pyRoot, mousePos ) :
		"""
		�ṩһ�� UI �б��û�ѡ��pyRoot �������е����ϲ��Ǹ� UI: ( ��ʾ�ڲ˵��б��ϵ����֣�UI )
		"""
		return []

	def getHitUI( self, pyRoot, mousePos ) :
		"""
		�û�ѡȡ��ĳ�� UI��pyRoot �������е����ϲ��Ǹ� UI������Ҳ����򷵻� None
		"""
		return None

	def show( self, pyUI ) :
		"""
		��ʾ����
		"""
		pass

	def hide( self ) :
		"""
		���ع���
		"""
		pass

	# -------------------------------------------------
	def preKeyEvent( self, down, key, mods ) :
		"""
		���������¼�
		"""
		return False

	__abstract_methods.add( getCHName )
	__abstract_methods.add( getHitUIs )
	__abstract_methods.add( getHitUI )
	__abstract_methods.add( show )
	__abstract_methods.add( hide )

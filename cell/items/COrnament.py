# -*- coding: gb18030 -*-

# $Id: COrnament.py,v 1.4 2008-09-04 07:44:43 kebiao Exp $

"""
װ�������ģ��
"""
from bwdebug import *
from CEquip import *
import csconst

class COrnament( CEquip ):
	"""
	��Ʒ�������ڽ�ָ������
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def wield( self, owner, update = True ):
		"""
		װ������

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		# ��װ���������ٴ�װ���������Ч���Ƿ�������⣬��װ��Ҫ�󳶲��ϣ���˲�����onWield��
		if not CEquip.wield( self, owner, update ):
			return False
		return True

	def unWield( self, owner, update = True ):
		"""
		ж��װ��

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		if not self.isAlreadyWield(): return	# ���û��װ��Ч������unwield
		CEquip.unWield( self, owner, update )
		return

### end of class: COrnament ###


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/02/22 01:37:59  yangkai
# �Ƴ��ɵ����θ������Դ���
#
# Revision 1.2  2007/01/23 04:16:04  kebiao
# ���� rndBonus ֧��
#
# Revision 1.1  2006/08/18 06:54:01  phw
# no message
#
#

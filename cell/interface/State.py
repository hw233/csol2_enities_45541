# -*- coding: gb18030 -*-
#
# $Id: State.py,v 1.21 2008-07-04 03:49:47 kebiao Exp $

"""
״̬ģ��
"""

from bwdebug import *
import csdefine
import csconst

class State:
	"""
	"""
	def __init__( self ):
		"""
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		self.actCounter = [0] * len( csconst.ACTFBLIST )
		self.effectCounter = [0] * len( csconst.EFFECT_STATE_LIST )
		"""
		self.actCounter = []
		for tmp in csconst.ACTFBLIST:
			self.actCounter.append( 0 )
		#self.actCounter = [0, 0, 0, 0, 0, 0, 0]		# ��������ʾδ��ʼ�����Ե�ʱ��ʹ��append����������
		"""
		self.actWord = 0
		self.effect_state = 0
		self.lastState = 0 # ������һ�ε�״̬
		
		if self.state < 0 or self.state >= csdefine.ENTITY_STATE_MAX:
			self.state = csdefine.ENTITY_STATE_FREE

		self.actCounterInc( csconst.ACTFBMASK[self.state] )		# �ָ����̹���״̬����

	def changeState( self, newState ):
		"""
		�ı�״̬��
			@param newState	:	�µ�״̬
			@type newState	:	integer
		"""
		#if newState == csdefine.ENTITY_STATE_FREE:
		#	print "++++++ restoring to pending state... "
		#	import msdebug
		#	msdebug.printStackTrace()
			
		
		
		if self.state == newState:
			return

		old = self.state
		
		# phw 2009-12-22: ��û��ʲô��������£�״̬�л�����д��־��������־����̫���ˣ�ʲôʱ����Ҫ���Ե�ʱ���ٴ򿪰�
		#TRACE_MSG( self.id, " State ", self.state, " => ", newState )
		
		# ����ԭ״̬����Ϊ���Ƽ���
		self.actCounterDec( csconst.ACTFBMASK[self.state] )
		self.state = newState
		# ������״̬����Ϊ���Ƽ���
		self.actCounterInc( csconst.ACTFBMASK[newState] )
		
		# phw 2009-12-22: ��û��ʲô��������£�״̬�л�����д��־��������־����̫���ˣ�ʲôʱ����Ҫ���Ե�ʱ���ٴ򿪰�
		#TRACE_MSG( self.id, " actCounter = ", self.actCounter )

		self.onStateChanged( old, self.state )

	def actCounterInc( self, stateWord ):
		"""
		������������һ����ά���������ơ�
			@param stateWord	:	����״̬��
			@type stateWord		:	integer
		"""
		for i, act in enumerate( csconst.ACTFBLIST ):
			if stateWord & act:
				if self.actCounter[i] == 0:
					self.actWord |= act
					self.onActWordChanged( act, True )
				self.actCounter[i] += 1		# Counter���ô���255

	def actCounterDec( self, stateWord ):
		"""
		������������һ����ά���������ơ�
			@param stateWord	:	����״̬��
			@type stateWord		:	integer
		"""
		for i, act in enumerate( csconst.ACTFBLIST ):
			if stateWord & act:
				if self.actCounter[i] - 1 >= 0:
					self.actCounter[i] -= 1
					if self.actCounter[i] == 0:
						self.actWord &= ~act
						self.onActWordChanged( act, False )
				else:
					ERROR_MSG( "Asymmetric call of actCounterInc/actCounterDec!" )
	
	def getActCounter( self, actBit ):
		"""
		��ȡ��Ϊ��������ֵ
		"""
		for i, act in enumerate( csconst.ACTFBLIST ):
			if actBit == act:
				return self.actCounter[ i ]
		
		ERROR_MSG( "No such act bit!" )
		return 0

	def getState( self ):
		"""
		��ȡ״̬��
			@return :	��ǰ״̬
			@rtype	:	integer
		"""
		return self.state
		
	def getLastState( self ):
		"""
		��ȡ��ǰ״̬֮ǰ��״̬
		"""
		return self.lastState
		

	def isState( self, state ) :
		"""
		�ж��Ƿ���ĳ��״̬��( hyw )
		@param			state : MACRO DEFINATION
		@type			state : states defined in csdefine.py
		@rtype				  : bool
		@return				  : ��ָ��״̬���򷵻� True
		"""
		return state == self.state

	def getActWord( self ):
		"""
		��ȡ�������ơ�Ӧ�ú����ã�һ���ʹ��actionSign()�������Ƿ�������
			@return	:	��ǰ��������
			@rtype	:	integer
		"""
		return self.actWord

	def actionSign( self, signWord ):
		"""
		�Ƿ���ڱ�ǡ�
			@return	:	�����
			@rtype	:	bool
		"""
		return self.actWord & signWord != 0

	def onStateChanged( self, old, new ):
		"""
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		self.lastState = old

	def onActWordChanged( self, act, disabled ):
		"""
		�������Ƹı�.
			@param act		:	������ʶ(�����)
			@type act		:	integer
			@param disabled	:	�����Ƿ񱻽�ֹ
			@param disabled	:	bool
		"""
		pass

	# ----------------------------------------------------------------------------------------------------
	# Ч��״̬
	# EFFECT_STATE_SLEEP						= 0x00000001		# ��˯Ч��
	# EFFECT_STATE_VERTIGO						= 0x00000002		# ѣ��Ч��
	# EFFECT_STATE_FIX							= 0x00000004		# ����Ч��
	# EFFECT_STATE_HUSH_PHY						= 0x00000008		# �����ĬЧ��
	# EFFECT_STATE_HUSH_MAGIC					= 0x00000010		# ������ĬЧ��
	# EFFECT_STATE_INVINCIBILITY				= 0x00000020		# �޵�Ч��
	# EFFECT_STATE_NO_FIGHT					= 0x00000040			# ��սЧ��
	# EFFECT_STATE_PROWL						= 0x00000080			# Ǳ��Ч��
	# EFFECT_STATE_FOLLOW					= 0x00000100			# ���棨��Ҵ�����Ӹ����У�
	# EFFECT_STATE_LEADER						= 0x00000200			# ��������Ҵ�����������У�
	# ----------------------------------------------------------------------------------------------------
	
	def effectStateChanged( self, estate, disabled ):
		"""
		Ч���ı�.
			@param estate		:	Ч����ʶ(�����)
			@type estate		:	integer
			@param disabled		:	Ч���Ƿ���Ч
			@param disabled		:	bool
		"""
		pass
		
	def effectStateInc( self, estate ):
		"""
		���һ��Ч��״̬��������
		"""
		for i, es in enumerate( csconst.EFFECT_STATE_LIST ):
			if estate & es:
				if self.effectCounter[i] == 0:
					self.effect_state |=  estate
					self.effectStateChanged( estate, True )
				self.effectCounter[i] += 1		# Counter���ô���255
				
	def effectStateDec( self, estate ):
		"""
		ɾ��һ��Ч��״̬��������
		"""
		for i, es in enumerate( csconst.EFFECT_STATE_LIST ):
			if estate & es:
				self.effectCounter[i] -= 1
				if self.effectCounter[i] == 0:
					self.effect_state &= ~estate
					self.effectStateChanged( estate, False )
					
	
	# ---------------------------------------------------------------------------------
	# posture
	# ---------------------------------------------------------------------------------
	def changePosture( self, posture ):
		"""
		�ı���̬
		
		@param posture : Ŀ����̬
		@type posture : UINT16
		"""
		self.beforePostureChange( posture )
		oldPosture = self.posture
		self.posture = posture
		self.afterPostureChange( oldPosture )
		
	def isPosture( self, posture ):
		"""
		�Ƿ���ĳ����̬
		
		@param posture : ��̬
		@type posture : UINT16
		"""
		return self.posture == posture
		
	def getPosture( self ):
		return self.posture
		
	def beforePostureChange( self, newPosture ):
		"""
		��̬�ı���
		
		@param oldPosture : �ı�ǰ����̬
		@param newPosture : �ı�����̬
		"""
		pass
		
	def afterPostureChange( self, oldPosture ):
		"""
		��̬�ı���
		
		@param oldPosture : �ı�ǰ����̬
		@param newPosture : �ı�����̬
		"""
		pass
#
# $Log: not supported by cvs2svn $
# Revision 1.20  2007/12/14 08:20:06  huangyongwei
# ����� isState ����
#
# Revision 1.19  2007/06/14 09:46:25  huangyongwei
# ɾ���� validAction ����
#
# Revision 1.18  2006/09/13 02:51:03  phw
# modify method: changeState(); ״̬�ı���־�����������״̬�ı��ߵ�ID��
#
# Revision 1.17  2006/05/29 10:53:28  phw
# ����״̬����ACTION_CANFIGHT��ΪACTION_FORBID_FIGHT��ͳһ���ж��嶼��Ĭ��Ϊ���ԣ��޸���ش���
#
# Revision 1.16  2005/12/28 11:28:23  wanhaipeng
# Fix skill bugs.
#
# Revision 1.15  2005/12/09 03:37:22  xuning
# no message
#
# Revision 1.14  2005/12/01 06:38:22  xuning
# ����
#
# Revision 1.13  2005/09/02 03:58:05  xuning
# ������Buff
# ���������Կ���
# �����˾���,����,���Լ���,״̬���Ƶȵ�,���»�����ģ���ϵ.
#
# Revision 1.12  2005/07/04 12:28:00  xuning
# ȥ����״̬����
#
# Revision 1.11  2005/07/04 08:18:56  xuning
# ����������ᵽL3Define.py
#
# Revision 1.10  2005/06/29 08:37:11  xuning
# no message
#
# Revision 1.9  2005/06/29 02:46:03  xuning
# no message
#
# Revision 1.8  2005/06/20 07:35:13  xuning
# �޸�����������״̬�л���BUG
#
# Revision 1.7  2005/06/17 05:08:04  xuning
# �����ͼ��ܻ���,�޸�
#
# Revision 1.6  2005/06/17 04:20:42  xuning
# �����ͼ��ܻ���
#
# Revision 1.5  2005/05/09 04:42:49  panguankong
# �޸��˳���״̬�ķ���
#
# Revision 1.4  2005/03/29 10:02:29  panguankong
# ����˴���ע�ͣ��޸��˱�����Сд
#

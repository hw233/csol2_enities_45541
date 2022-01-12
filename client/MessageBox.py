# -*- coding: gb18030 -*-
#
# $Id: MessageBox.py,v 1.11 2008-08-11 07:20:00 huangyongwei Exp $


import BigWorld
from Function import Functor
from config.client.msgboxtexts import Datas
messagebox = None

# --------------------------------------------------------------------
# �Ի��򷵻�ֵ
# --------------------------------------------------------------------
RS_OK			= 0x01						# �����ȷ����ť
RS_CANCEL		= 0x02						# �����ȡ����ť
RS_YES			= 0x04						# ������ǰ�ť
RS_NO			= 0x08						# ����˷�ť
RS_SPE_CANCEL	= 0x10						# ����������ȡ����ť
RS_SPE_OK       = 0x20						# ������������Ͱ�ť
RS_SPE_CAN		= 0x40						# �����ȡ�����Ͱ�ť

# --------------------------------------------------------------------
# �Ի���ťֵ
# --------------------------------------------------------------------
MB_OK					= RS_OK							# ��ʾ��ȷ����ť
MB_CANCEL				= RS_CANCEL						# ��ʾ��ȡ����ť
MB_SPE_CANCEL			= RS_SPE_CANCEL					# ��ʾ������ȡ����ť
MB_OK_CANCEL			= RS_OK | RS_CANCEL				# ��ʾ��ȷ����ȡ����ť
MB_YES_NO				= RS_YES | RS_NO				# ��ʾ���ǡ���ť
MB_YES_NO_CANCEL		= RS_YES | RS_NO | RS_CANCEL	# ��ʾ���ǡ���ȡ����ť
MB_SPE_OK_CANCEL		= RS_SPE_OK | RS_SPE_CAN        # ��ʾ���������͡�ȡ�����Ͱ�ť

# --------------------------------------------------------------------
# ��ʾ��Ϣ��
# --------------------------------------------------------------------
def showMessage( msgID, title, btns, callback = lambda rsbtn : rsbtn, pyOwner = None, gstStatus = None ) :
	"""
	@type		msgID	 : int/str
	@param		msgID	 : ��Ϣ ID ����Ϣ�ı�
	@type		title	 : str
	@param		title	 : ��Ϣ����
	@type		btns	 : MACRO DEFINATION
	@param		btns	 : ��ʾ��ť( MB_OK / MB_CANCEL / MB_OK_CANCEL / MB_YES_NO / MB_NONE )
	@type		callback : functor
	@param		callback : �ص���������һ�����������Ա�ʾ������ĸ���ť��RS_OK / RS_CANCEL / RS_YES / RS_NO
	@type		pyOwner	 : python ui
	@param		pyOwner	 : ����������ʵ��
	@type		gstStatus: MACRO Definations
	@param		gstStatus: ��ָ��״̬����ʾ�������ǰ����������״̬������ȵ���״̬���ֺ����ʾ���� Define.py �ж��壺GST_XXX��
	@return				 : None
	"""
	msg = Datas.get( msgID, msgID )
	global messagebox
	if not messagebox :
		messagebox = __import__( "guis/tooluis/messagebox" )
	if btns == MB_OK :
		return messagebox.showOk( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_CANCEL :
		return messagebox.showCancel( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_SPE_CANCEL :
		return messagebox.showSpecialCancel( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_OK_CANCEL :
		return messagebox.showOkCancel( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_YES_NO :
		return messagebox.showYesNo( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_YES_NO_CANCEL :
		return messagebox.showYesNoCancel( msg, title, callback, pyOwner, gstStatus )
	elif btns == MB_SPE_OK_CANCEL:
		return messagebox.showSpecialOkCancel( msg, title, callback, pyOwner, gstStatus )

# --------------------------------------------------------------------
# ��ʾ��Ϣ�򣨳���ָ����һ��ʱ����Զ��������Ĭ�ϰ�ť�رգ�
# --------------------------------------------------------------------
__cbids = {}

def _agentCallback( delayOrder, callback, resID ) :
	"""
	callback ��ת
	"""
	callback( resID )
	BigWorld.cancelCallback( __cbids.pop( delayOrder ) )

def __delayOption( pyBox ) :
	"""
	message box ����ʾʱ�䵽��
	"""
	pyBox.hide()

def showAutoHideMessage( lastTime, msgID, title, btns = MB_OK, callback = lambda rsbtn : rsbtn, pyOwner = None, gstStatus = None ) :
	"""
	@type		lastTime : int
	@param		lastTime : ����ʱ��( �� )
	@type		msgID	 : int/str
	@param		msgID	 : ��Ϣ ID ����Ϣ�ı�
	@type		title	 : str
	@param		title	 : ��Ϣ����
	@type		btns	 : MACRO DEFINATION
	@param		btns	 : ��ʾ��ť( MB_OK / MB_OK_CANCEL / MB_YES_NO / MB_NONE )
	@type		callback : functor
	@param		callback : �ص���������һ�����������Ա�ʾ������ĸ���ť��RS_OK / RS_CANCEL / RS_YES / RS_NO
	@type		pyOwner	 : python ui
	@param		pyOwner	 : ����������ʵ��
	@return				 : None
	"""
	delayOrder = 0
	while delayOrder in __cbids : delayOrder += 1
	agentCallback = Functor( _agentCallback, delayOrder, callback )
	pyBox = showMessage( msgID, title, btns, agentCallback, pyOwner, gstStatus )
	__cbids[delayOrder] = BigWorld.callback( lastTime, Functor( __delayOption, pyBox ) )
	return pyBox

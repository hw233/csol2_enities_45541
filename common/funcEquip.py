# -*- coding: gb18030 -*-

"""
װ��λ����غ���
"""

from bwdebug import *
from ItemTypeEnum import *

# $Id: funcEquip.py,v 1.6 2008-02-19 09:26:26 kebiao Exp $

# װ�����ͺ�װ����λ�õ�ӳ�䣬���ӳ��Ӧ�ú��������Щ�жϺ�����ʹ�õ�һ��
# ��Ӧ����һ��tuple����tuple��ԭ������ĳЩװ�����ܿ����ڼ���λ�õ�����λ��װ�������ָ
m_cwt2cel = {
		CWT_HEAD        : ( CEL_HEAD, ),
		CWT_NECK        : ( CEL_NECK, ),
		CWT_BODY        : ( CEL_BODY, ),
		CWT_BREECH      : ( CEL_BREECH, ),
		CWT_VOLA        : ( CEL_VOLA, ),
		CWT_LEFTHAND    : ( CEL_LEFTHAND, ),
		CWT_RIGHTHAND   : ( CEL_RIGHTHAND, ),
		CWT_FEET        : ( CEL_FEET, ),
		CWT_LEFTFINGER  : ( CEL_LEFTFINGER, ),
		CWT_RIGHTFINGER : ( CEL_RIGHTFINGER, ),
		CWT_TWOHAND     : ( CEL_RIGHTHAND, ),
		CWT_HANDS       : ( CEL_LEFTHAND, CEL_RIGHTHAND ),
		CWT_TWOFINGER   : ( CEL_RIGHTFINGER, ),
		CWT_FINGERS     : ( CEL_LEFTFINGER, CEL_RIGHTFINGER ),
		CWT_RIGHTORTWO  : ( CEL_RIGHTHAND, ),
		CWT_HAUNCH		: ( CEL_HAUNCH, ),
		CWT_CUFF		: ( CEL_CUFF, ),
		CWT_CIMELIA		: ( CEL_CIMELIA, ),
		CWT_TALISMAN	: ( CEL_TALISMAN, ),
		CWT_FASHION1	: ( CEL_FASHION1, ),
		CWT_FASHION2	: ( CEL_POTENTIAL_BOOK, ),
	}

def wieldOnHead( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_HEAD --> CEL_HEAD
	order, = m_cwt2cel[CWT_HEAD]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnNeck( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_NECK --> CEL_NECK
	order, = m_cwt2cel[CWT_NECK]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnBody( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_BODY --> CEL_BODY
	order, = m_cwt2cel[CWT_BODY]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnBreech( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_BREECH --> CEL_BREECH
	order, = m_cwt2cel[CWT_BREECH]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnVola( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_VOLA --> CEL_VOLA
	order, = m_cwt2cel[CWT_VOLA]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnLeftHand( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_LEFTHAND --> CEL_LEFTHAND
	# װ�������֣����CWT_TWOHAND������ͻ�����Ա���Ҫ�ж�û��װ��λ��ΪCWT_TWOHAND��װ��
	# �ȼ��װ��λ���Ƿ���װ��
	order, = m_cwt2cel[CWT_LEFTHAND]
	if order != dstLocation:
		raise AssertionError, "location not match."
	order2, = m_cwt2cel[CWT_TWOHAND]
	if order == order2:
		if equipKitbag.orderHasItem( order ):
			return ( order, )
	else:
		if equipKitbag.orderHasItem( order ):
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOHAND:
				return ( order, order2 )
			return ( order, )
		else:
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOHAND:
				return ( order, order2 )
	return ()

def wieldOnRightHand( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_RIGHTHAND --> CEL_RIGHTHAND
	# װ�������֣����CWT_TWOHAND������ͻ�����Ա���Ҫ�ж�û��װ��λ��ΪCWT_TWOHAND��װ��
	order, = m_cwt2cel[CWT_RIGHTHAND]
	if order != dstLocation:
		raise AssertionError, "location not match."
	order2, = m_cwt2cel[CWT_TWOHAND]
	if order == order2:
		if equipKitbag.orderHasItem( order ):
			return ( order, )
	else:
		if equipKitbag.orderHasItem( order ):
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOHAND:
				return ( order, order2 )
			return ( order, )
		else:
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOHAND:
				return ( order, order2 )
	return ()

def wieldOnFeet( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_FEET --> CEL_FEET
	order, = m_cwt2cel[CWT_FEET]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnLeftFinger( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_LEFTFINGER --> CEL_LEFTFINGER
	# װ��������ָ�����CWT_TWOFINGER������ͻ�����Ա���Ҫ�ж�û��װ��λ��ΪCWT_TWOFINGER��װ��
	order, = m_cwt2cel[CWT_LEFTFINGER]
	if order == dstLocation:
		raise AssertionError, "location not match."
	order2, = m_cwt2cel[CWT_TWOFINGER]
	if order == order2:
		if equipKitbag.orderHasItem( order ):
			return ( order, )
	else:
		if equipKitbag.orderHasItem( order ):
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOFINGER:
				return ( order, order2 )
			return ( order, )
		else:
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOFINGER:
				return ( order, order2 )
	return ()

def wieldOnRightFinger( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_RIGHTFINGER --> CEL_RIGHTFINGER
	# װ��������ָ�����CWT_TWOFINGER������ͻ�����Ա���Ҫ�ж�û��װ��λ��ΪCWT_TWOFINGER��װ��
	order, = m_cwt2cel[CWT_RIGHTFINGER]
	if order != dstLocation:
		raise AssertionError, "location not match."
	order2, = m_cwt2cel[CWT_TWOFINGER]
	if order == order2:
		if equipKitbag.orderHasItem( order ):
			return ( order, )
	else:
		if equipKitbag.orderHasItem( order ):
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOFINGER:
				return ( order, order2 )
			return ( order, )
		else:
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOFINGER:
				return ( order, order2 )
	return ()

def wieldOnTwoHand( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_TWOHAND --> CEL_RIGHTHAND
	# ��Ҫ˫���յ�װ������Ҫ���ֺ����ֶ�û��װ��
	order, = m_cwt2cel[CWT_TWOHAND]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if order == CEL_RIGHTHAND:
		co = CEL_LEFTHAND
	else:
		co = CEL_RIGHTHAND
	if equipKitbag.orderHasItem( order ):				# ������װ��
		if equipKitbag.orderHasItem( co ):	# ������װ��
			return ( order, co )
		return ( order, )
	else:
		if equipKitbag.orderHasItem( co ):	# ������װ��
			return ( co, )
	return ()

def wieldOnHands( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_HANDS --> CEL_LEFTHAND, CEL_RIGHTHAND
	# �����ֿ������װ���ģ�����Ҫ����Ƿ���CWT_TWOHAND��װ��
	orderList = m_cwt2cel[CWT_HANDS]
	if dstLocation not in orderList:
		raise AssertionError, "location not match."
	order2, = m_cwt2cel[CWT_TWOHAND]
	if dstLocation == order2:
		if equipKitbag.orderHasItem( dstLocation ):
			return ( dstLocation, )
	else:
		if equipKitbag.orderHasItem( dstLocation ):
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOHAND:
				return ( dstLocation, order2 )
			return ( dstLocation, )
		else:
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOHAND:
				return ( dstLocation, order2 )
	return ()

def wieldOnTwoFinger( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_TWOFINGER --> CEL_RIGHTFINGER
	# ��Ҫ������ָ����װ��(��ָ��װ...)����Ҫ����ָ������ָ��û��װ��
	order, = m_cwt2cel[CWT_TWOFINGER]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if order == CEL_RIGHTFINGER:
		co = CEL_LEFTFINGER
	else:
		co = CEL_RIGHTFINGER
	if equipKitbag.orderHasItem( order ):				# ������װ��
		if equipKitbag.orderHasItem( co ):	# ������װ��
			return ( order, co )
		return ( order, )
	else:
		if equipKitbag.orderHasItem( co ):	# ������װ��
			return ( co, )
	return ()

def wieldOnFingers( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_FINGERS --> CEL_LEFTFINGER, CEL_RIGHTFINGER
	# ������ָ�������װ���ģ�����Ҫ����Ƿ���CWT_TWOFINGER��װ��
	orderList = m_cwt2cel[CWT_FINGERS]
	if dstLocation not in orderList:
		raise AssertionError, "location not match."
	order2, = m_cwt2cel[CWT_TWOFINGER]
	if dstLocation == order2:
		if equipKitbag.orderHasItem( dstLocation ):
			return ( dstLocation, )
	else:
		if equipKitbag.orderHasItem( dstLocation ):
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOHAND:
				return ( dstLocation, order2 )
			return ( dstLocation, )
		else:
			if equipKitbag.orderHasItem( order2 ) and equipKitbag.getByOrder( order2 ).query( "eq_wieldType" ) == CWT_TWOHAND:
				return ( dstLocation, order2 )
	return ()

def wieldOnRightOrTwo( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	# CWT_RIGHTORTWO --> CEL_RIGHTHAND
	# ��Ҫ���ֻ�˫���յģ���������ֵ�װ��û������Ҫ��������װ�������Ե�ʵ����
	return wieldOnRightHand( equipKitbag, dstLocation )

def wieldOnHaunch( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	order, = m_cwt2cel[CWT_HAUNCH]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnCuff( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	order, = m_cwt2cel[CWT_CUFF]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnCimelia( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	order, = m_cwt2cel[CWT_CIMELIA]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnTalisman( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	order, = m_cwt2cel[CWT_TALISMAN]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnFashion1( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	order, = m_cwt2cel[CWT_FASHION1]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

def wieldOnFashion2( equipKitbag, dstLocation ):
	"""
	���װ������λ�ã�ȷ����Ҫж�صĵ���λ�ã�
	�ú������Զ����װ������ص�λ�ã�������λ������װ���Һ����ڵ�װ����ʽ��ͻ������Ҫж�µ�װ��λ�÷���

	@param equipKitbag: װ��������
	@type  equipKitbag: KitbagType
	@param dstLocation: ��װ�����ĸ�λ�ã�ֵΪCEL_*���������������Ϊ��Щ�����ǿ����ڼ���λ��������ѡ��һ���������Ҫ�ɵ�����ָ����
	@type  dstLocation: UINT8
	@raise AssertionError: ���ָ����װ��λ���뵱ǰ����Ĭ�ϵ����Ͷ�Ӧ��λ�ò��������
	@return:            ������Ҫж�µ�װ����λ�õ��б����û����Ҫж��װ������б���Ϊ0��
	@rtype:             tuple of UINT8/None
	"""
	order, = m_cwt2cel[CWT_FASHION2]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

# ���ڵ�Ҫװ��ĳ�����͵�װ��ʱ���װ������Ҫж����Щλ�õ�װ��
m_unwieldCheck = {
		CWT_HEAD        : wieldOnHead,
		CWT_NECK        : wieldOnNeck,
		CWT_BODY        : wieldOnBody,
		CWT_BREECH      : wieldOnBreech,
		CWT_VOLA        : wieldOnVola,
		CWT_LEFTHAND    : wieldOnLeftHand,
		CWT_RIGHTHAND   : wieldOnRightHand,
		CWT_FEET        : wieldOnFeet,
		CWT_LEFTFINGER  : wieldOnLeftFinger,
		CWT_RIGHTFINGER : wieldOnRightFinger,
		CWT_TWOHAND     : wieldOnTwoHand,
		CWT_HANDS       : wieldOnHands,
		CWT_TWOFINGER   : wieldOnTwoFinger,
		CWT_FINGERS     : wieldOnFingers,
		CWT_RIGHTORTWO  : wieldOnRightOrTwo,
		CWT_HAUNCH		: wieldOnHaunch,
		CWT_CUFF		: wieldOnCuff,
		CWT_CIMELIA		: wieldOnCimelia,
		CWT_TALISMAN	: wieldOnTalisman,
		CWT_FASHION1	: wieldOnFashion1,
		CWT_FASHION2	: wieldOnFashion2,
	}

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2007/12/04 00:49:39  yangkai
# �������������װ��ת������
#
# Revision 1.4  2007/11/27 08:50:24  yangkai
# no message
#
# Revision 1.3  2007/11/24 03:16:13  yangkai
# ��Ʒϵͳ���������Ը���
# "wieldType" --> "eq_wieldType"
#
# Revision 1.2  2006/08/11 03:23:08  phw
# no message
#
# Revision 1.1  2006/08/09 08:21:01  phw
# no message
#
#

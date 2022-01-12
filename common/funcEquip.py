# -*- coding: gb18030 -*-

"""
装备位置相关函数
"""

from bwdebug import *
from ItemTypeEnum import *

# $Id: funcEquip.py,v 1.6 2008-02-19 09:26:26 kebiao Exp $

# 装备类型和装备栏位置的映射，这个映射应该和下面的那些判断函数所使用的一致
# 对应的是一个tuple，是tuple的原因在于某些装备可能可以在几个位置的任意位置装备，如戒指
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_LEFTHAND --> CEL_LEFTHAND
	# 装备在左手，会和CWT_TWOHAND产生冲突，所以必须要判断没有装备位置为CWT_TWOHAND的装备
	# 先检查装备位置是否有装备
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_RIGHTHAND --> CEL_RIGHTHAND
	# 装备在右手，会和CWT_TWOHAND产生冲突，所以必须要判断没有装备位置为CWT_TWOHAND的装备
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_LEFTFINGER --> CEL_LEFTFINGER
	# 装备在左手指，会和CWT_TWOFINGER产生冲突，所以必须要判断没有装备位置为CWT_TWOFINGER的装备
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_RIGHTFINGER --> CEL_RIGHTFINGER
	# 装备在右手指，会和CWT_TWOFINGER产生冲突，所以必须要判断没有装备位置为CWT_TWOFINGER的装备
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_TWOHAND --> CEL_RIGHTHAND
	# 需要双手握的装备，需要左手和右手都没有装备
	order, = m_cwt2cel[CWT_TWOHAND]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if order == CEL_RIGHTHAND:
		co = CEL_LEFTHAND
	else:
		co = CEL_RIGHTHAND
	if equipKitbag.orderHasItem( order ):				# 右手有装备
		if equipKitbag.orderHasItem( co ):	# 左手有装备
			return ( order, co )
		return ( order, )
	else:
		if equipKitbag.orderHasItem( co ):	# 左手有装备
			return ( co, )
	return ()

def wieldOnHands( equipKitbag, dstLocation ):
	"""
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_HANDS --> CEL_LEFTHAND, CEL_RIGHTHAND
	# 两个手可以随便装备的，必须要检查是否有CWT_TWOHAND的装备
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_TWOFINGER --> CEL_RIGHTFINGER
	# 需要两个手指戴的装备(介指套装...)，需要左手指和右手指都没有装备
	order, = m_cwt2cel[CWT_TWOFINGER]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if order == CEL_RIGHTFINGER:
		co = CEL_LEFTFINGER
	else:
		co = CEL_RIGHTFINGER
	if equipKitbag.orderHasItem( order ):				# 右手有装备
		if equipKitbag.orderHasItem( co ):	# 左手有装备
			return ( order, co )
		return ( order, )
	else:
		if equipKitbag.orderHasItem( co ):	# 左手有装备
			return ( co, )
	return ()

def wieldOnFingers( equipKitbag, dstLocation ):
	"""
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_FINGERS --> CEL_LEFTFINGER, CEL_RIGHTFINGER
	# 两个手指可以随便装备的，必须要检查是否有CWT_TWOFINGER的装备
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	# CWT_RIGHTORTWO --> CEL_RIGHTHAND
	# 需要右手或双手握的，这个和右手的装备没区别，主要区别在于装备后属性的实现上
	return wieldOnRightHand( equipKitbag, dstLocation )

def wieldOnHaunch( equipKitbag, dstLocation ):
	"""
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
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
	检查装备栏的位置，确定需要卸载的道具位置；
	该函数会自动检查装备栏相关的位置，如果相关位置上有装备且和现在的装备方式冲突则会把需要卸下的装备位置返回

	@param equipKitbag: 装备栏引用
	@type  equipKitbag: KitbagType
	@param dstLocation: 想装备在哪个位置，值为CEL_*；有这个参数是因为有些类型是可以在几个位置中任意选择一个，因此需要由调用者指定。
	@type  dstLocation: UINT8
	@raise AssertionError: 如果指定的装备位置与当前函数默认的类型对应的位置不符则产生
	@return:            代表需要卸下的装备的位置的列表，如果没有需要卸下装备则该列表长度为0，
	@rtype:             tuple of UINT8/None
	"""
	order, = m_cwt2cel[CWT_FASHION2]
	if order != dstLocation:
		raise AssertionError, "location not match."
	if equipKitbag.orderHasItem( order ):
		return ( order, )
	return ()

# 用于当要装备某种类型的装备时检查装备栏需要卸下哪些位置的装备
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
# 添加腰带，护腕装备转换函数
#
# Revision 1.4  2007/11/27 08:50:24  yangkai
# no message
#
# Revision 1.3  2007/11/24 03:16:13  yangkai
# 物品系统调整，属性更名
# "wieldType" --> "eq_wieldType"
#
# Revision 1.2  2006/08/11 03:23:08  phw
# no message
#
# Revision 1.1  2006/08/09 08:21:01  phw
# no message
#
#

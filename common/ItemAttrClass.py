# -*- coding: gb18030 -*-
# $Id: ItemAttrClass.py,v 1.82 2008-08-30 02:41:14 yangkai Exp $

"""
"""
import BigWorld
import cschannel_msgs
import ShareTexts as ST
import struct
from bwdebug import *
from ItemTypeEnum import *
from SmartImport import smartImport
from ItemSystemExp import EquipQualityExp
from ItemSystemExp import ItemTypeAmendExp
from ItemSystemExp import EquipIntensifyExp
from ItemSystemExp import SpecialComposeExp
from ItemSystemExp import PropertyPrefixExp
from ItemSystemExp import EquipExp

from FactionMgr import factionMgr
import items
import cPickle
import csdefine
import math
import csconst

from config.client.labels.items import lbs_CEquip
from config.client.labels.items import lbs_createEffect

def intensifyObeyCommonCalc( func ):
	"""
	@intensifyObeyCommonCalc：和装备强化、认主相关的公共计算
	@func: EquipExp中的公式计算方法
	@return: ( 属性总量，强化增量字符串描述，认主增量字符串描述 )
	"""
	exp = func.im_self # 根据绑定方法获取公式对象实例
	itemInstance = exp.equip
	reference = exp.owner

	calcIntensifyInc = lambda x = func : x( ignoreObey = True, ignoreZipPercent = True, ignoreWieldCalc = True ) - x( ignoreObey = True, ignoreIntensify = True, ignoreZipPercent = True, ignoreWieldCalc = True )
	calcObeyInc = lambda x = func: x( ignoreIntensify = True, ignoreZipPercent = True, ignoreWieldCalc = True ) - x( ignoreObey = True, ignoreObey = True, ignoreZipPercent = True, ignoreWieldCalc = True )
	calcTotal = lambda x = func: x( ignoreZipPercent = True, ignoreWieldCalc = True )

	total = calcTotal()

	# 灵魂锁链绑定附加属性
	addDes = ""
	addValue = 0
	if itemInstance.isObey():
		addValue = calcObeyInc()
		addDes = "(+%i)" % addValue

	# 装备强化附加属性
	intenDes = ""
	intenValue = 0
	intensify = itemInstance.getIntensifyLevel()
	if intensify != 0:
		intenValue = calcIntensifyInc()
		intenDes = "(+%i)" % intenValue

	return ( total, addDes, intenDes )

class IADefault:
	"""
	readFromConfig() 用于从配置文件中读取一个属性的值
	addToStream() 和 createFromStream() 方法主要用于从server发送更改消息给client用。但不排除将来会不会用来生成保存到数据库中的数据。
	"""
	@staticmethod
	def readFromConfig( attrDict, dict ):
		"""
		从一个配置文件的python dict里读取数据到attrDict中

		@param attrDict: where to save the section's data
		@type  attrDict: dict
		@param  dict: data want to read
		@type   dict: python dict
		@return:         no return
		"""
		raise "I can't do this. -- %s" % dict

	@staticmethod
	def addToStream( value ):
		"""
		transfer the value to string

		@param value: 每个类型的值都不一样,各接口自己确定
		@type  value: anything
		@return: string
		"""
		raise "I can't do this. --", value

	@staticmethod
	def createFromStream( stream ):
		"""
		@param stream: data want to convert
		@type  stream: string
		@return:       anything
		"""
		raise "I can't do this. --", stream

	@staticmethod
	def description( itemInstance, reference ):
		"""
		产生相关属性描述

		@param itemInstance: 继承于CItemBase的物品实例
		@type  itemInstance: CItemBase
		@param    reference: 玩家entity,表示以谁来做为生成描述的参照物
		@type     reference: Entity
		@return: string
		@rtype:  string
		"""
		return ""

class IAScript( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dict ):
		"""read the section's value to attrDict"""
		dynClassName = dict
		attrDict["dynClass"] = smartImport( "items." + dynClassName + ":" + dynClassName )

class IAKitbagClass( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dict ):
		"""read the dict's value to attrDict"""
		return
		#kitbagClass = section.asString
		#if kitbagClass == "": return
		#attrDict["kb_kitbagClass"] = smartImport( m_kitbagsMap[kitbagClass] )

class IAFlags( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, listDat ):
		"""read the section's value to attrDict"""
		flags = 0
		for flag in listDat:
			flags += 1 << flag
		if flags == 0: return
		attrDict["flags"] = flags

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAIcon( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		"""read the dat's value to attrDict"""
		if dat == "": return
		attrDict["icon"] = dat

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

class IAModel( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, model ):
		"""read the dat's value to attrDict"""
		if model == "": return
		valList = model.split(";")
		vs = ""
		for value in valList:
			val = value.split("-")
			try:
				v = int(val[0]) * 1000000
				v += int(val[1]) * 10000
				v += int(val[2])
			except Exception, errstr:
				ERROR_MSG( "'%s' is not right." % model )
				v = 0
			vs += str(v) + ";"
		v = vs.rstrip(";")
		attrDict["model"] = v

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAParticle( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, particle ):
		if particle == "": return
		attrDict["particle"] = particle

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		return cschannel_msgs.ITEMATTRCLASS_INFO_1

class IAType( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, type ):
		attrDict["type"] = type

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		itemtype = itemInstance.query( "type" )
		return m_classifyMap[itemtype]

class IAClasses( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, reqClasses ):
		if len( reqClasses ) == 0: return
		attrDict["reqClasses"] = [ k * 16 for k in reqClasses ]

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		m = itemInstance.query( "reqClasses", [] )
		s = ""
		sl = []
		if csdefine.CLASS_MAGE in m:
			sl.append( ST.PROFESSION_MAGIC )
		if csdefine.CLASS_ARCHER in m:
			sl.append( ST.PROFESSION_ARCHER )
		if csdefine.CLASS_SWORDMAN  in m:
			sl.append( ST.PROFESSION_SWORD )
		if csdefine.CLASS_FIGHTER  in m:
			sl.append( ST.PROFESSION_FIGHTER )
		if len(sl) == 4: return ""
		for index, k in enumerate( sl ):
			if index == 0:
				s += "%s" % k
			else:
				s += cschannel_msgs.ITEMATTRCLASS_INFO_2 % k
		return s

class IAReqGender( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, reqClasses ):
		if len( reqClasses ) == 0: return
		attrDict["reqGender"] = reqClasses

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		reqGender = itemInstance.query( "reqGender", [] )
		if len( reqGender ) != 1: return ""

		if csdefine.GENDER_MALE in reqGender:
			return cschannel_msgs.ITEMATTRCLASS_INFO_3
		return cschannel_msgs.ITEMATTRCLASS_INFO_4

class IACredit( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		"""
		<reqCredit>
			<item>
				<factionid>	14	</factionid>
				<value>	42000	</value>
			</item>
		</reqCredit>
		"""
		creditDict = {}
		for i in xrange( len( dat ) ):
			val = dat[ i ]
			creditDict[ val["factionid"] ] = val["value"]
		attrDict["reqCredit"] = creditDict

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def descriptionDict( itemInstance, reference ):
		"""
		返回物品声望需求的描述信息数据
		"""
		creditsDict = itemInstance.credit()
		recreditsDict = {}
		for key,creditsValue in creditsDict.iteritems():
			value = reference.getPrestige(key)	#玩家声望
			des = cschannel_msgs.ITEMATTRCLASS_INFO_5 + factionMgr.getName(key) + cschannel_msgs.ITEMATTRCLASS_INFO_6 + reference.getPretigeDes(creditsValue)	#获取描述信息的字符串 如 需要凤鸣声望崇拜
			if value is None or creditsValue > value:
				recreditsDict[ des ] = 0
			else:
				recreditsDict[ des ] = 1

		return recreditsDict

class IAPrice( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, price ):
		"""read the section's value to attrDict"""
		if price == 0: return
		attrDict["price"] = price

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]


	@staticmethod
	def description( itemInstance, reference ):
		price = itemInstance.getPrice()
		if price > 0:
			cschannel_msgs.ITEMATTRCLASS_INFO_7 % itemInstance.getPrice()
		return ""

class IALifeType( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lifeType ):
		if lifeType == 0: return
		attrDict["lifeType"] = lifeType

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		lifeType = itemInstance.getLifeType()
		if lifeType == CLTT_ON_WIELD:
			lifeTime = itemInstance.getLifeTime()
			if lifeTime == 0:
				des = cschannel_msgs.ITEMATTRCLASS_INFO_8
				return des
			if not itemInstance.getDeadTime():

				hour = lifeTime/3600
				min = ( lifeTime - hour * 3600 )/60
				sec = lifeTime%60
				day = int( hour / 24 )

				des = cschannel_msgs.ITEMATTRCLASS_INFO_9
				if day:
					des += cschannel_msgs.ITEMATTRCLASS_INFO_10 % day
				elif hour:
					des += cschannel_msgs.ITEMATTRCLASS_INFO_11 % hour
				elif min:
					des += cschannel_msgs.ITEMATTRCLASS_INFO_12 % min
				elif sec:
					des += cschannel_msgs.ITEMATTRCLASS_INFO_13 % sec
				return des

		return ""

class IALifeTime( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lifeTime ):
		if lifeTime == 0: return
		attrDict["lifeTime"] = lifeTime
		return

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		return ""

class IADeadTime( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, deadTime ):
		return

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IABindType( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, bindType ):
		if bindType == 0: return
		attrDict["bindType"] = bindType

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		des = ""
		bindType = itemInstance.getBindType()
		if itemInstance.isBinded():
			des = cschannel_msgs.ITEM_HAVEBIND_DES
		else:
			if bindType == CBT_PICKUP:
				des = cschannel_msgs.ITEM_PICKBIND_DES
			elif bindType == CBT_EQUIP:
				des = cschannel_msgs.ITEM_WIELDBIND_DES
			elif bindType == CBT_QUEST:
				des = cschannel_msgs.ITEM_QUESTBIND_DES
		return des

class IAUseDegree( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, useDegree ):
		"""read the section's value to attrDict"""
		if useDegree == 0: return
		attrDict["useDegree"] = useDegree

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]


	@staticmethod
	def description( itemInstance, reference ):
		useDegree = itemInstance.query( "useDegree",0 )
		if useDegree <= 1:
			return ""
		return cschannel_msgs.ITEMATTRCLASS_INFO_14 %useDegree

class IAName( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, name ):
		"""read the dict's value to attrDict"""
		attrDict["name"] = name

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		nameDes = itemInstance.fullName()

		intensifyLevel = itemInstance.query( "eq_intensifyLevel", 0 )
		if intensifyLevel and intensifyLevel >0: # 加上装备的强化等级显示 如 XX +9
			nameDes += ("  +%d"%intensifyLevel)
		return nameDes

class IACreator( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		creator = itemInstance.query( "creator", 0 )
		if creator:
			creator = cschannel_msgs.ITEMATTRCLASS_INFO_15 % creator
		return creator

class IAIntensifyValue( IADefault ):
	"""
	"""
	@staticmethod
	def readFromConfg( attrDict, secion ):
		"""
		read the section's value to attrDict
		"""
		pass

	@staticmethod
	def addToStream( value ):
		"""
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		"""
		return cPickle.loads( stream )

	@staticmethod
	def description( itemInstance, reference ):
		return ""


class IAStackable( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, stackable ):
		if stackable == 1: return
		# 默认叠加数量就是1，不需记录
		attrDict["stackable"] = stackable

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=h", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=h", stream )[0]

class IAAmount( IADefault ):
	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=h", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=h", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return cschannel_msgs.ITEMATTRCLASS_INFO_16 % itemInstance.getAmount()

class IALevel( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, level ):
		"""
		@return:         no return
		"""
		attrDict["level"] = level

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=B", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return:       anything
		"""
		return struct.unpack( "=B", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		"""
		@return: string
		@rtype:  string
		"""
		level = itemInstance.getLevel()
		if level > 0:
			return cschannel_msgs.ITEMATTRCLASS_INFO_17 % level
		return ""

class IAMaxSpace( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, maxSpace ):
		if maxSpace == 0: return
		attrDict["kb_maxSpace"] = maxSpace

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=B", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=B", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return cschannel_msgs.ITEMATTRCLASS_INFO_18 % itemInstance.query( "kb_maxSpace" )

class IAMaxHardiness( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, hardinessMax ):
		if hardinessMax <= 0: return
		attrDict["eq_hardinessMax"] = hardinessMax
		attrDict["eq_hardinessLimit"] = hardinessMax
		attrDict["eq_hardiness"] = hardinessMax

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=l", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=l", stream )[0]


class IAHardiness( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		"""read the python dict's value to attrDict"""
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=l", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=l", stream )[0]

	@staticmethod
	def calcuHardiness( value, maxValue ):
		"""
		取整计算 当value小于10000大于0时，显示为1,其它显示为value/10000
		这地方的公式改变的话需要再改DurabilityItem.py里面的耐久度公式，不然会造成不一致
		"""
		vmax = max( maxValue / csconst.EQUIP_HARDINESS_UPDATE_VALUE, 1 )
		if value % csconst.EQUIP_HARDINESS_UPDATE_VALUE == 0:
			value = value / csconst.EQUIP_HARDINESS_UPDATE_VALUE
		else:
			if value != 0:
				value = value / csconst.EQUIP_HARDINESS_UPDATE_VALUE + 1
				if value > vmax:
					value = vmax

		return value, vmax

	@staticmethod
	def description( itemInstance, reference ):
		if itemInstance.query( "eq_hardinessMax" ):
			return cschannel_msgs.ITEMATTRCLASS_INFO_19 % ( IAHardiness.calcuHardiness( itemInstance.query( "eq_hardiness" ),  itemInstance.query( "eq_hardinessLimit" )) )
		return ""

	@staticmethod
	def descriptionList( itemInstance, reference ):
		if itemInstance.query( "eq_hardinessMax" ):
			return [cschannel_msgs.ITEMATTRCLASS_INFO_20 ,"%i/%i" % ( IAHardiness.calcuHardiness( itemInstance.query( "eq_hardiness" ),  itemInstance.query( "eq_hardinessLimit" )) )]
		return ""


class IAHardinessLimit( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		"""read the python dict's value to attrDict"""
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=l", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=l", stream )[0]

class IAWieldType( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, wieldType ):
		"""read the python dict's value to attrDict"""
		attrDict["eq_wieldType"] = wieldType

	@staticmethod
	def description( itemInstance, reference ):
		wt = itemInstance.query( "eq_wieldType" )
		return m_wtNameMap.get( wt, "" )

class IAReqlevel( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, reqLevel ):
		if reqLevel == 0: return
		attrDict["reqLevel"] = reqLevel

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=B", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=B", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		level = itemInstance.query( "reqLevel", 0 )
		if level > 0:
			return cschannel_msgs.ITEMATTRCLASS_INFO_21 % level
		return ""

	@staticmethod
	def description_vehicle( itemInstance, reference ):
		"""
		该描述用于骑宠的描述信息
		注：之所以添加这个接口是因为物品的很多基础属性也会做为骑宠物品的基础属性，如果
		作为骑宠的物品属性在描述，就需要有不同的提示。使描述不至于被误解。
		"""
		level = itemInstance.query( "reqLevel", 0 )
		if level > 0:
			return cschannel_msgs.ITEMATTRCLASS_INFO_22 % level
		return ""

	@staticmethod
	def descriptionList( itemInstance, reference ):
		level = itemInstance.query( "reqLevel", 0 )
		if level > 0:
			return [cschannel_msgs.ITEMATTRCLASS_INFO_23, "%i" % level]
		return []

	@staticmethod
	def description_pet( itemInstance, reference ):
		"""
		该描述用于宠物的描述信息
		"""
		level = itemInstance.query( "reqLevel", 0 )
		if level > 0:
			return cschannel_msgs.ITEMATTRCLASS_INFO_48 % level
		return ""

class IAPrefix( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, prefix ):
		if prefix == 0: return
		attrDict["prefix"] = prefix

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=B", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=B", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return cschannel_msgs.ITEMATTRCLASS_INFO_24

class IApropertyPrefix( IADefault ):
	"""
	属性前缀，手写装备应该具有属性前缀，所以有readFromConfig模块
	"""
	@staticmethod
	def readFromConfig( attrDict, prefix ):
		if prefix == 0: return
		attrDict["propertyPrefix"] = prefix


	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream


class IAQuality( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, quality ):
		if quality <= 1: return
		attrDict["quality"] = quality

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=B", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=B", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return cschannel_msgs.ITEMATTRCLASS_INFO_25

class IABaseQualityRate( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, baseQualityRate ):
		baseQualityRate = baseQualityRate/100.0
		if ( baseQualityRate <= 0.000001 ) and ( baseQualityRate >= -0.000001 ): return
		attrDict["baseQualityRate"] = baseQualityRate

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

class IAExcQualityRate( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, excQualityRate ):
		# excQualityRate = excQualityRate/100.0

		# if ( excQualityRate <= 0.000001 ) and ( excQualityRate >= -0.000001 ): return

		# 这里和策划配置不一致，不用缩小100倍，updated by mushuang
		attrDict["excQualityRate"] = excQualityRate

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]


class IADescribe1( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		describe = dat.strip( " \t\r\n" )
		if describe =="": return
		attrDict["describe1"] = describe

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		return itemInstance.query( "describe1", "" )

class IADescribe2( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		describe = dat.strip( " \t\r\n" )
		if describe =="": return
		attrDict["describe2"] = describe

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		return itemInstance.query( "describe2", "" )

class IADescribe3( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		describe = dat.strip( " \t\r\n" )
		if describe =="": return
		attrDict["describe3"] = describe

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		return itemInstance.query( "describe3", "" )

class IARange( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, eq_range ):
		if ( eq_range <= 0.000001 ) and ( eq_range >= -0.000001 ): return
		attrDict["eq_range"] = eq_range

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		range = itemInstance.query( "eq_range" )
		if range == None:			#如果没有攻击距离，返回""
			return ""
		return cschannel_msgs.ITEMATTRCLASS_INFO_26 % range

	@staticmethod
	def descriptionList( itemInstance, reference ):
		range = itemInstance.query( "eq_range" )
		if range == None:			#如果没有攻击距离，返回""
			return []
		return [cschannel_msgs.ITEMATTRCLASS_INFO_27 , "%2.1f" % range ]


class IADelay( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, eq_delay ):
		if ( eq_delay <= 0.000001 ) and ( eq_delay >= -0.000001 ): return
		attrDict["eq_delay"] = eq_delay

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		delay = itemInstance.query( "eq_delay" )
		if delay == None:			#如果没有攻击速度，返回""
			return ""
		return cschannel_msgs.ITEMATTRCLASS_INFO_28 % delay

	@staticmethod
	def descriptionList( itemInstance, reference ):
		delay = itemInstance.query( "eq_delay" )
		if delay == None:			#如果没有攻击速度，返回""
			return []
		return [cschannel_msgs.ITEMATTRCLASS_INFO_29 , "%2.1f" % delay]

class IADPS( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, eq_DPS ):
		if ( eq_DPS <= 0.000001 ) and ( eq_DPS >= -0.000001 ): return
		attrDict["eq_DPS"] = eq_DPS

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return ""

	@staticmethod
	def descriptionList( itemInstance, reference ):
		return []

class IAMagicPower( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, magicPower ):
		if len( magicPower ) == 0: return
		magicPower = int( float( magicPower ) )
		if magicPower == 0: return
		attrDict["eq_magicPower"] = magicPower

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return ""

	@staticmethod
	def descriptionList( itemInstance, reference ):
		return []

class IAKaCount( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		dst = ""
		currentCount = itemInstance.query( "ka_count", 0 )
		totalCount = itemInstance.query( "ka_totalCount", 0 )
		if currentCount < totalCount:
			dst = cschannel_msgs.ITEMATTRCLASS_INFO_30 % ( currentCount, totalCount )
		else:
			dst = cschannel_msgs.ITEMATTRCLASS_INFO_31
		return dst

	@staticmethod
	def descriptionList( itemInstance, reference ):
		dst = []
		currentCount = itemInstance.query( "ka_count", 0 )
		totalCount = itemInstance.query( "ka_totalCount", 0 )
		if currentCount < totalCount:
			dst = [cschannel_msgs.ITEMATTRCLASS_INFO_32,"%i/%i"%(currentCount, totalCount )]
		else:
			dst = [cschannel_msgs.ITEMATTRCLASS_INFO_32,cschannel_msgs.ITEMATTRCLASS_INFO_33]
		return dst

class IAKaTotalCount( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ka_totalCount ):
		"""read the section's value to attrDict"""
		if ka_totalCount == 0: return
		attrDict["ka_totalCount"] = ka_totalCount

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAPetLife( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, pet_life ):
		if pet_life == 0: return
		attrDict["pet_life"] = pet_life

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAVehicleMoveSpeed( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, speed ):
		if speed == 0.0: return
		attrDict["vehicle_move_speed"] = speed

class IAVehicleMaxMount( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, mount ):
		if mount == 0: return
		attrDict["vehicle_max_mount"] = mount

class IAVehicleResistGiddy( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, mount ):
		if mount == 0.0: return
		attrDict["vehicle_resist_giddy"] = mount

class IAJoyancy( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, joyancy ):
		if joyancy == 0: return
		attrDict["joyancy"] = joyancy

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAFullDegree( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, fullDegree ):
		if fullDegree == 0: return
		attrDict["fullDegree"] = fullDegree

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IADPSArea( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, DPSArea ):
		if ( DPSArea <= 0.000001 ) and ( DPSArea >= -0.000001 ): return
		attrDict["eq_DPSArea"] = DPSArea

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

class IApDamageLose( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, pDamageLose ):
		if ( pDamageLose <= 0.000001 ) and ( pDamageLose >= -0.000001 ): return
		attrDict["eq_pDamageLose"] = pDamageLose

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		classlist = itemInstance.queryReqClasses()
		if not classlist: return ""
		exp = EquipExp( itemInstance, reference )

		return cschannel_msgs.ITEM_ARMOR_PER_DES % intensifyObeyCommonCalc( exp.getArmorBase )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		# 获取需要的职业列表
		classlist = itemInstance.queryReqClasses()
		if not classlist: return ""
		exp = EquipExp( itemInstance, reference )

		return [ cschannel_msgs.ITEM_ARMOR_VALUE_DES, "%i%s%s" % intensifyObeyCommonCalc( exp.getArmorBase ) ]

class IAsDamageLose( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, sDamageLose ):
		if ( sDamageLose <= 0.000001 ) and ( sDamageLose >= -0.000001 ): return
		attrDict["eq_sDamageLose"] = sDamageLose

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		# 获取需要的职业列表
		classlist = itemInstance.queryReqClasses()
		if not classlist: return ""
		exp = EquipExp( itemInstance, reference )

		return cschannel_msgs.ITEM_MAGICARMOR_PER_DES % intensifyObeyCommonCalc( exp.getMagicArmorBase )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		# 获取需要的职业列表
		classlist = itemInstance.queryReqClasses()
		if not classlist: return ""

		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_MAGICARMOR_PER_DES, "%i%s%s" % intensifyObeyCommonCalc( exp.getMagicArmorBase ) ]

class IASpell( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, spellID ):
		if  spellID == 0: return
		attrDict["spell"] = spellID

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=q", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=q", stream )[0]


class IAFreeze( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		"""read the python dict's value to attrDict"""
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]


class IAQuest( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, questID ):
		if questID == 0: return
		attrDict["questID"] = questID

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAID( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dict ):
		"""read the dict's value to attrDict"""
		pass	# 暂时啥都不做

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

class IAWieldStatus( IADefault ):
	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

class IASuitEffectState( IADefault ):
	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

class IAObey( IADefault ):
	@staticmethod
	def addToStream( value ):
		"""
		@return: string by 姜毅
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		dst = ""
		currentObey = itemInstance.query( "eq_obey", 0 )
		if currentObey:
			dst = cschannel_msgs.ITEMATTRCLASS_INFO_34
		else:
			dst = cschannel_msgs.ITEMATTRCLASS_INFO_35
		return dst

class IAMaxSlot( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, maxSlot ):
		if maxSlot == 0: return
		attrDict["eq_maxSlot"] = maxSlot

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

class IASlot( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		"""read the python dict's value to attrDict"""
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

class IALimitSlot( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, LimitSlot ):
		if LimitSlot == 0: return
		attrDict["eq_limitSlot"] = LimitSlot

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		eq_solt = itemInstance.query( "eq_limitSlot", 0 )
		if  eq_solt <= 0:
			return ""
		return cschannel_msgs.ITEMATTRCLASS_INFO_36 % eq_solt

class IABjExtraEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lstDat ):
		extraEffect = []
		for i in xrange( len( lstDat ) ):
			key = lstDat[i]["id"]
			if key == "": continue
			value = lstDat[i]["value"]
			if value == "": continue
			value = eval( value )
			extraEffect.append( ( key, value ) )
		if len( extraEffect ) == 0: return
		attrDict["bj_extraEffect"] = extraEffect

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		des = ""
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		extraEffect = itemInstance.query( "bj_extraEffect", [] )
		for data in extraEffect:
			effectClass = g_equipEffects.getEffect( data[0] )
			if effectClass is None: continue
			des += "@B" + effectClass.description( data[1] )
		return des

	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		des = []
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		extraEffect = itemInstance.query( "bj_extraEffect", [] )
		for data in extraEffect:
			effectClass = g_equipEffects.getEffect( data[0] )
			if effectClass is None: continue
			des.append( effectClass.descriptionList( data[1] ) )
		return des

	@staticmethod
	def descriptionListType( itemInstance, reference ):
		"""
		"""
		des = []
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		extraEffect = itemInstance.query( "bj_extraEffect", {} )
		for data in extraEffect:
			effectClass = g_equipEffects.getStonEffectType( data[0] )
			if effectClass is None: continue
			des.append( effectClass )
		return des


class IASlotOnly( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, slotOnly ):
		if slotOnly == 0: return
		attrDict["bj_slotOnly"] = slotOnly

class IASlotOrder( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, slotOrder ):
		if slotOrder == 0: return
		attrDict["bj_slotOrder"] = slotOrder

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

class IASlotLocation( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, slotLocation ):
		if len( slotLocation ) == 0: return
		attrDict["bj_slotLocation"] = slotLocation

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		bjSlotLocations = itemInstance.query( "bj_slotLocation", [] )
		if len( bjSlotLocations ) == 0: return ""
		des = [ m_classifyMap.get( k, "" ) for k in bjSlotLocations ]
		des = cschannel_msgs.ITEMATTRCLASS_INFO_47.join( des )
		if des == "": return ""
		return cschannel_msgs.ITEMATTRCLASS_INFO_37 % des

class IASpringUsedCD( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lstDat ):
		springUsedCD = {}
		for i in xrange( len( lstDat ) ):
			key = lstDat[i]["CDID"]
			value = lstDat[i]["CDTime"]
			springUsedCD[key] = value
		if len( springUsedCD ) == 0: return
		attrDict["springUsedCD"] = springUsedCD

class IASpringIntonateOverCD( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lstDat ):
		springIntonateOverCD = {}
		for i in xrange( len( lstDat ) ):
			key = lstDat[i]["CDID"]
			value = lstDat[i]["CDTime"]
			springIntonateOverCD[key] = value
		if len( springIntonateOverCD ) == 0: return
		attrDict["springIntonateOverCD"] = springIntonateOverCD

class IALimitCD( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, limitCD ):
		if len( limitCD ) == 0: return
		attrDict["limitCD"] = limitCD

class IATeleportRecord( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		list = dat.split(";")
		if len( list ) != 3: return
		position = tuple( [float(k) for k in list[1].split(",")] )
		yaw = tuple( [float(k) for k in list[2].split(",")] )
		value = ( list[0],  position, yaw )
		attrDict["ch_teleportRecord"]  = value

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		des = ""
		ch_teleportRecord = itemInstance.query( "ch_teleportRecord", None )
		if ch_teleportRecord is None: return des
		if len( ch_teleportRecord ) != 3: return des
		areaFullName = reference.getWholeAreaBySpaceLabel( ch_teleportRecord[0] )
		des += areaFullName
		x = int( ch_teleportRecord[1][0] )
		z = int( ch_teleportRecord[1][2] )
		des += str( ( x, z ) )
		return des

class IAIntensifyLevel( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=b", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=b", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		des = ""
		intensifyLevel = itemInstance.query( "eq_intensifyLevel", 0 )
		if intensifyLevel > 0 :
			des = intensifyLevel
		return des

class IAExtraEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lstDat ):
		extraEffect = {}
		for i in xrange( len( lstDat ) ):
			key = lstDat[i]["id"]
			if key == "": continue
			value = lstDat[i]["value"]
			if value == "": continue
			extraEffect[key] = eval( value )
		if len( extraEffect ) == 0: return
		attrDict["eq_extraEffect"] = extraEffect

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		efElems = []
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		extraEffect = itemInstance.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffects.getEffect( key )
			if effectClass is None: continue
			s = effectClass.description( value )
			efElems.append( s )
		return "@B".join( efElems )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		des = []
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		extraEffect = itemInstance.query( "eq_extraEffect", {} )
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffects.getEffect( key )
			if effectClass is None: continue
			maxValue = g_equipEffects.getEffectMax( itemInstance, key )
			desList = effectClass.descriptionList( value )
			desList.append( value >= maxValue )
			des.append( desList)
		return des

	@staticmethod
	def descriptionListType( itemInstance, reference ):
		"""
		"""
		des = []
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		extraEffect = itemInstance.query( "eq_extraEffect", {} )
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffects.getStonEffectType( key )
			if effectClass is None: continue
			des.append( effectClass.descriptionList( value ) )
		return des

class IACreateEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lstDat ):
		return

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		des = []
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		createEffect = itemInstance.getCreateEffect()
		for key, value in createEffect:
			if key == 0:
				des.append( [lbs_createEffect[1],"", False] )
				continue
			effectClass = g_equipEffects.getEffect( key )
			if effectClass is None: continue
			descriptList = effectClass.descriptionList( value )
			descriptList[1] += lbs_createEffect[2]
			maxValue = g_equipEffects.getEffectMax( itemInstance, key )
			descriptList.append( value >= maxValue )
			des.append( descriptList )
		return des


class IASuitEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lstDat ):
		suitEffect = {}
		for i in xrange( len( lstDat ) ):
			key = lstDat[i]["id"]
			if key == "": continue
			value = lstDat[i]["value"]
			if value == "": continue
			suitEffect[key] = eval( value )
		if len( suitEffect ) == 0: return
		attrDict["eq_suitEffect"] = suitEffect

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def description( itemInstance, reference ):
		"""
		"""
		des = ""
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		suitEffect = itemInstance.query( "eq_suitEffect", {} )
		for key, value in suitEffect.iteritems():
			effectClass = g_equipEffects.getEffect( key )
			if effectClass is None: continue
			des += "@B" + effectClass.description( value )
		return des


	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		des = []
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		suitEffect = itemInstance.query( "eq_suitEffect", {} )
		for key, value in suitEffect.iteritems():
			effectClass = g_equipEffects.getEffect( key )
			if effectClass is None: continue
			maxValue = g_equipEffects.getEffectMax( itemInstance, key )
			desList = effectClass.descriptionList( value )
			desList.append( value >= maxValue )
			des.append( desList )
		return des

class IAOnlyLimit( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, onlyLimit ):
		# 该属性为0时，表示可无限制获取
		if onlyLimit == 0: return
		attrDict["onlyLimit"] = onlyLimit
	
	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]	

	@staticmethod
	def description( itemInstance, reference ):
		isOnly = itemInstance.query( "onlyLimit" )
		if isOnly:return cschannel_msgs.ITEM_ONLY_LIMITED
					
class IAYuanbao( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		# 该属性为0时，表示可无限制获取
		pass


class IAGoldYuanbao( IADefault ):
	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]


	@staticmethod
	def description( itemInstance, reference ):
		return cschannel_msgs.ITEMATTRCLASS_INFO_38 % itemInstance.query("goldYuanbao")


class IASilverYuanbao( IADefault ):
	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]


	@staticmethod
	def description( itemInstance, reference ):
		return cschannel_msgs.ITEMATTRCLASS_INFO_39 % itemInstance.query("silverYuanbao")


class IAWarIntegral( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, warIntegral ):
		if warIntegral == 0: return
		attrDict["warIntegral"] = warIntegral

	@staticmethod
	def description( itemInstance, reference ):
		s = ""
		if itemInstance.query( "warIntegral", 0 ) > 0:
			s = cschannel_msgs.ITEMATTRCLASS_INFO_40 % itemInstance.query( "warIntegral", 0 )
		return s

class IAMaxPoint( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, sd_maxPoint ):
		if sd_maxPoint == 0: return
		attrDict["sd_maxPoint"] = sd_maxPoint
		attrDict["sd_currPoint"] = sd_maxPoint

class IACurrPoint( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		return

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		maxPoint = itemInstance.getMaxPoint()
		currPoint = itemInstance.getCurrPoint()
		return cschannel_msgs.ITEMATTRCLASS_INFO_41 % ( currPoint, maxPoint )

class IATmExp( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		return

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return ""

class IATmpotential( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		return

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return ""

class IATmGrade( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		return

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		itemtype = itemInstance.getGrade()
		des = ""
		if itemtype == TALISMAN_COMMON:
			des = cschannel_msgs.ITEM_TALISMAN_COMMON_DES
		elif itemtype == TALISMAN_DEITY:
			des = cschannel_msgs.ITEM_TALISMAN_IMMORTAL_DES
		elif itemtype == TALISMAN_IMMORTAL:
			des = cschannel_msgs.ITEM_TALISMAN_DEITY_DES
		return des

class IATmBaseEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, lstDat ):
		baseEffect = {}
		for i in xrange( len( lstDat ) ):
			key = lstDat[i]["id"]
			if key == "": continue
			value = lstDat[i]["value"]
			if value == "": continue
			baseEffect[key] = eval( value )
		if len( baseEffect ) == 0: return
		attrDict["tm_baseEffect"] = baseEffect

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def description( itemInstance, reference ):
		des = ""
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		tm_baseEffect = itemInstance.query( "tm_baseEffect", {} )
		for key, value in tm_baseEffect.iteritems():
			effectClass = g_equipEffects.getEffect( key )
			if effectClass is None: continue
			des += "@B" + effectClass.description( value )
		return des

	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		des = []
		g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
		tm_baseEffect = itemInstance.query( "tm_baseEffect", {} )
		for key, value in tm_baseEffect.iteritems():
			effectClass = g_equipEffects.getEffect( key )
			if effectClass is None: continue
			des.append( effectClass.descriptionList( value ) )
		return des

class IATmCommonEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		return []

class IATmDeityEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		return []

class IATmImmortalEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		return []

class IATmFlawEffect( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return cPickle.loads( stream )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		"""
		return []

class IAMaterial( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		pass


	@staticmethod
	def addToStream( value ):
		"""
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		"""
		return cPickle.loads( stream )


	@staticmethod
	def descriptionList( itemInstance, reference ):
		"""
		返回打造需要的材料
		"""
		return SpecialComposeExp._instance.getMaterials(itemInstance.id)

class IAParam1( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		# 该属性为0时，表示可无限制获取
		if param == "": return
		attrDict["param1"] = param

	@staticmethod
	def addToStream( value ):
		"""
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		"""
		return cPickle.loads( stream )

class IAParam2( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param2"] = param

	@staticmethod
	def addToStream( value ):
		"""
		"""
		return cPickle.dumps( value, 2 )

	@staticmethod
	def createFromStream( stream ):
		"""
		"""
		return cPickle.loads( stream )

class IAParam3( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param3"] = param

class IAParam4( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param4"] = param

class IAParam5( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param5"] = param

class IAParam6( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param6"] = param

class IAParam7( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param7"] = param

class IAParam8( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param8"] = param

class IAParam9( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param9"] = param

class IAParam10( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		if param == "": return
		attrDict["param10"] = param

class IATreasurePositon( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		treasure_position = dat.strip( " \t\r\n" )
		if treasure_position =="": return
		attrDict["treasure_position"] = treasure_position

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		return itemInstance.query( "treasure_position", "" )

class IATreasureSpace( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		treasure_space = dat.strip( " \t\r\n" )
		if treasure_space =="": return
		attrDict["treasure_space"] = treasure_space

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		return itemInstance.query( "treasure_space", "" )


class IAYinpiao( IADefault ):
	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]


	@staticmethod
	def description( itemInstance, reference ):
		price = itemInstance.getPrice()
		if price > 0:
			return cschannel_msgs.ITEMATTRCLASS_INFO_44 % itemInstance.getPrice()
		return ""

class IAHideMoney( IADefault ):		# 10:47 2009-1-15，wsf
	"""
	红包：隐藏的金钱
	"""
	@staticmethod
	def addToStream( value ):
		"""
		@return : STRING
		"""
		return struct.pack( "=i", value )


	@staticmethod
	def createFromStream( stream ):
		"""
		@return : 打包前的数据
		"""
		return struct.unpack( "=i", stream )[ 0 ]


	@staticmethod
	def description( itemInstance, reference ):
		return cschannel_msgs.ITEMATTRCLASS_INFO_45


class IAResistChenmo( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ResistChenmo ):
		if not ResistChenmo:
			return
		attrDict["eq_ResistChenmo"] = ResistChenmo

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		ResistChenmo = itemInstance.query( "eq_ResistChenmo", 0 )
		if ResistChenmo == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return cschannel_msgs.ITEM_RESISTCHENMO_PER_DES % intensifyObeyCommonCalc( exp.getResistMagicHushProb )


	@staticmethod
	def descriptionList( itemInstance, reference ):
		ResistChenmo = itemInstance.query( "eq_ResistChenmo", 0 )
		if ResistChenmo == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_RESISTCHENMO_VALUE_DES, "+%i%s%s" % intensifyObeyCommonCalc( exp.getResistMagicHushProb )]

class IAResistGiddy( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ResistGiddy ):
		if not ResistGiddy:
			return
		attrDict["eq_ResistGiddy"] = ResistGiddy

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]


	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ResistGiddy", 0 )
		if eqValue == 0: return ""
		exp = EquipExp( itemInstance, reference )
		return cschannel_msgs.ITEM_RESISTGIDDY_PER_DES % intensifyObeyCommonCalc( exp.getResistGiddyProb )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ResistGiddy", 0 )
		if eqValue == 0: return ""
		exp = EquipExp( itemInstance, reference )
		return [cschannel_msgs.ITEM_RESISTGIDDY_VALUE_DES,"+%i%s%s" %intensifyObeyCommonCalc( exp.getResistGiddyProb )]

class IAResistFix( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ResistFix ):
		if not ResistFix:
			return
		attrDict["eq_ResistFix"] = ResistFix

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ResistFix", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )


		return cschannel_msgs.ITEM_RESISTFIX_PER_DES % intensifyObeyCommonCalc( exp.getResistFixProb )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ResistFix", 0 )
		baseQualityRate = itemInstance.getBaseRate()
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_RESISTFIX_VALUE_DES, "+%i%s%s" %intensifyObeyCommonCalc( exp.getResistFixProb )]

class IAReduceTargetHit( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ReduceTargetHit ):
		if not ReduceTargetHit:
			return
		attrDict["eq_ReduceTargetHit"] = ReduceTargetHit

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ReduceTargetHit", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return cschannel_msgs.ITEM_REDUCETARGETHIT_PER_DES % intensifyObeyCommonCalc( exp.getReduceTargetHit )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ReduceTargetHit", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_REDUCETARGETHIT_VALUE_DES, "+%i%s%s" %intensifyObeyCommonCalc( exp.getReduceTargetHit )]


class IAResistSleep( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ResistSleep ):
		if not ResistSleep:
			return
		attrDict["eq_ResistSleep"] = ResistSleep

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ResistSleep", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )
		return cschannel_msgs.ITEM_RESISTSLEEP_PER_DES %intensifyObeyCommonCalc( exp.getResistSleepProb )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ResistSleep", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_RESISTSLEEP_VALUE_DES, "+%i%s%s" %intensifyObeyCommonCalc( exp.getResistSleepProb )]


class IAResistHit( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ResistHit ):
		if not ResistHit:
			return
		attrDict["eq_ResistHit"] = ResistHit

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ResistHit", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return cschannel_msgs.ITEM_RESISTHIT_PER_DES % intensifyObeyCommonCalc( exp.getResistHitProb )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ResistHit", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_RESISTHIT_VALUE_DES, "+%i%s%s" % intensifyObeyCommonCalc( exp.getResistHitProb )]


class IADodge( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, Dodge ):
		if not Dodge:
			return
		attrDict["eq_Dodge"] = Dodge

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_Dodge", 0 )
		if eqValue == 0: return ""
		exp = EquipExp( itemInstance, reference )


		return cschannel_msgs.ITEM_DODGE_PER_DES %intensifyObeyCommonCalc( exp.getDodgeProb )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_Dodge", 0 )
		if eqValue == 0: return ""
		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_DODGE_VALUE_DES, "+%i%s%s" %intensifyObeyCommonCalc( exp.getDodgeProb )]

#御敌	
class IAReduceRoleD( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ReduceRoleD ):
		if not ReduceRoleD:
			return
		attrDict["eq_ReduceRoleD"] = ReduceRoleD

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ReduceRoleD", 0.0 )
		if eqValue == 0.0: return ""
		exp = EquipExp( itemInstance, reference )


		return cschannel_msgs.ITEM_REDUCEROLED_PER_DES %intensifyObeyCommonCalc( exp.getReduceRoleD )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ReduceRoleD", 0.0 )
		if eqValue == 0.0: return ""
		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_REDUCEROLED_VALUE_DES, "+%i%s%s" %intensifyObeyCommonCalc( exp.getReduceRoleD )]
	
#破敌
class IAAddRoleD( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, AddRoleD ):
		if not AddRoleD:
			return
		attrDict["eq_AddRoleD"] = AddRoleD

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=f", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=f", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_AddRoleD", 0.0 )
		if eqValue == 0.0: return ""
		exp = EquipExp( itemInstance, reference )


		return cschannel_msgs.ITEM_ADDROLED_PER_DES %intensifyObeyCommonCalc( exp.getAddRoleD )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_AddRoleD", 0.0 )
		if eqValue == 0.0: return ""
		exp = EquipExp( itemInstance, reference )

		return  [cschannel_msgs.ITEM_ADDROLED_VALUE_DES, "+%i%s%s" % intensifyObeyCommonCalc( exp.getAddRoleD ) ]

class IAReduceTargetMagicHit( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ReduceTargetMagicHit ):
		if not ReduceTargetMagicHit:
			return
		attrDict["eq_ReduceTargetMagicHit"] = ReduceTargetMagicHit

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ReduceTargetMagicHit", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return cschannel_msgs.ITEM_REDUCETARGETMAGICHIT_PER_DES % intensifyObeyCommonCalc( exp.getReduceTargetMagicHit )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		eqValue = itemInstance.query( "eq_ReduceTargetMagicHit", 0 )
		if eqValue == 0: return ""

		exp = EquipExp( itemInstance, reference )

		return [cschannel_msgs.ITEM_REDUCETARGETMAGICHIT_VALUE_DES, "+%i%s%s" % intensifyObeyCommonCalc( exp.getReduceTargetMagicHit )]


class IAUpper( IADefault ):
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return value

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return stream

	@staticmethod
	def description( itemInstance, reference ):
		upper = itemInstance.query( "eq_upper", "" )
		if upper != "":
			upper = cschannel_msgs.ITEMATTRCLASS_INFO_46 % upper
		return upper


class IAUpFlag( IADefault ):
	def readFromConfig( attrDict, dat ):
		pass

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAPickUpType( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, pickUpType ):
		if pickUpType == 0: return
		attrDict["pickUpType"] = pickUpType

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAIsSystemItem( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, isSystemItem ):
		if isSystemItem < 0: return
		attrDict["isSystemItem"] = isSystemItem

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=B", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=B", stream )[0]
		
class IAYudieRealm( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, ydRealm ):
		if ydRealm == 0: return
		attrDict["ydRealm"] = ydRealm

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

class IAExpItem( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, dat ):
		return

	@staticmethod
	def addToStream( value ):
		"""
		@return: string
		"""
		return struct.pack( "=i", value )

	@staticmethod
	def createFromStream( stream ):
		"""
		@return: anything
		"""
		return struct.unpack( "=i", stream )[0]

	@staticmethod
	def description( itemInstance, reference ):
		return ""


m_wtNameMap = {
				CWT_HEAD						:	cschannel_msgs.ITEM_HEAD_DES,
				CWT_NECK						:	cschannel_msgs.ITEM_NECK_DES,
				CWT_BODY						:	cschannel_msgs.ITEM_BODY_DES,
				CWT_BREECH						:	cschannel_msgs.ITEM_BREECH_DES,
				CWT_VOLA						:	cschannel_msgs.ITEM_VOLA_DES,
				CWT_LEFTHAND					:	cschannel_msgs.ITEM_LEFTHAND_DES,
				CWT_RIGHTHAND					:	cschannel_msgs.ITEM_RIGHTHAND_DES,
				CWT_FEET						:	cschannel_msgs.ITEM_FEET_DES,
				CWT_HAUNCH						:	cschannel_msgs.ITEM_HAUNCH_DES,
				CWT_CUFF						:	cschannel_msgs.ITEM_CUFF_DES,
				CWT_LEFTFINGER					:	cschannel_msgs.ITEM_LEFTRING_DES,
				CWT_RIGHTFINGER					:	cschannel_msgs.ITEM_RIGHTRING_DES,
				CWT_TWOHAND						:	cschannel_msgs.ITEM_TWOHAND_DES,
				CWT_HANDS						:	cschannel_msgs.ITEM_HANDS_DES,
				CWT_TWOFINGER					:	cschannel_msgs.ITEM_FINGERS_DES,
				CWT_FINGERS						:	cschannel_msgs.ITEM_RING_DES,
				CWT_RIGHTORTWO					:	cschannel_msgs.ITEM_RIGHTORTWO_DES,
				CWT_TALISMAN					:	cschannel_msgs.ITEM_TALISMAN_DES,
				CWT_CIMELIA						:	cschannel_msgs.ITEM_CIMELIA_DES,
				CWT_FASHION1					: 	cschannel_msgs.ITEM_FASHION_DES,
				CWT_FASHION2					: 	cschannel_msgs.ITEM_ACMENT_DES,
			}
m_classifyMap = {
				ITEM_WEAPON_AXE1				:	cschannel_msgs.ITEM_AXE_DES,
				ITEM_WEAPON_SWORD1				:	cschannel_msgs.ITEM_SWORD_DES,
				ITEM_WEAPON_HAMMER1				:	cschannel_msgs.ITEM_HAMMER_DES,
				ITEM_WEAPON_SPEAR1				:	cschannel_msgs.ITEM_SPEAR_DES,
				ITEM_WEAPON_DAGGER				:	cschannel_msgs.ITEM_DAGGER_DES,
				ITEM_WEAPON_AXE2				:	cschannel_msgs.ITEM_TWOAXE_DES,
				ITEM_WEAPON_SWORD2				:	cschannel_msgs.ITEM_TWOSWORD_DES,
				ITEM_WEAPON_HAMMER2				:	cschannel_msgs.ITEM_TWOHAMMER_DES,
				ITEM_WEAPON_SPEAR2				:	cschannel_msgs.ITEM_TWOSPEAR_DES,
				ITEM_WEAPON_TWOSWORD			:	cschannel_msgs.ITEM_DOUBLESWORD_DES,
				ITEM_WEAPON_LONGBOW				:	cschannel_msgs.ITEM_TWOBOW_DES,
				ITEM_WEAPON_SHORTBOW			:	cschannel_msgs.ITEM_BOW_DES,
				ITEM_WEAPON_STAFF				:	cschannel_msgs.ITEM_STAFF_DES,
				ITEM_WEAPON_SHIELD				:	cschannel_msgs.ITEM_SHIELD_DES,
				ITEM_WEAPON_TRUMP				:	cschannel_msgs.ITEM_TRUMP_DES,
				ITEM_ARMOR_HEAD					:	cschannel_msgs.ITEM_ARMOR_HEAD_DES,
				ITEM_ARMOR_BODY					:	cschannel_msgs.ITEM_ARMOR_BODY_DES,
				ITEM_ARMOR_HAUNCH				:	cschannel_msgs.ITEM_ARMOR_HAUNCH_DES,
				ITEM_ARMOR_CUFF					:	cschannel_msgs.ITEM_ARMOR_CUFF_DES,
				ITEM_ARMOR_VOLA					:	cschannel_msgs.ITEM_ARMOR_HAND_DES,
				ITEM_ARMOR_BREECH				:	cschannel_msgs.ITEM_ARMOR_BREECH_DES,
				ITEM_ARMOR_FEET					:	cschannel_msgs.ITEM_ARMOR_FEET_DES,
				ITEM_ORNAMENT_NECKLACE			:	cschannel_msgs.ITEM_NECK_DES,
				ITEM_ORNAMENT_RING				:	cschannel_msgs.ITEM_RING_DES,
				ITEM_ORNAMENT_ACMENT			:	cschannel_msgs.ITEM_ACMENT_DES,
				ITEM_PROPERTY_MEDICINE			:	cschannel_msgs.ITEM_MEDICINE_DES,
				ITEM_PROPERTY_FOOD				:	cschannel_msgs.ITEM_FOOD_DES,
				ITEM_PROPERTY_DRUG				:	cschannel_msgs.ITEM_DRUG_DES,
				ITEM_PROPERTY_CHARM				:	cschannel_msgs.ITEM_CHARM_DES,
				ITEM_PROPERTY_COUP				:	cschannel_msgs.ITEM_COUP_DES,
				ITEM_NORMAL_SUNDRIES			:	cschannel_msgs.ITEM_SUNDRIES_DES,
				ITEM_VOUCHER_ITEM				:	cschannel_msgs.ITEM_VOUCHER_DES,
				ITEM_VOUCHER_QUEST				:	cschannel_msgs.ITEM_QUEST_DES,
				ITEM_SYSTEM_FUNC				:	cschannel_msgs.ITEM_SYSTEM_DES,
				ITEM_WAREHOUSE_KITBAG			:	cschannel_msgs.GMMGR_BEI_BAO,
				ITEM_WAREHOUSE_CASKET			:	cschannel_msgs.ITEM_CASKET_DES,
				ITEM_PRODUCE_STUFF				:	cschannel_msgs.ITEM_STUFF_DES,
				ITEM_QUEST_STUFF				:	cschannel_msgs.ITEM_QUESTSTUFF_DES,
				ITEM_PRODUCE_JEWELRY			:	cschannel_msgs.ITEM_JEWELRY_DES,
				ITEM_SYSTEM_KASTONE				:	cschannel_msgs.ITEM_CIMELIA_DES,
				ITEM_SYSTEM_TALISMAN			:	cschannel_msgs.ITEM_TALISMAN_DES,
				ITEM_SYSTEM_VEHICLE				:	cschannel_msgs.ITEM_VEHICLE_DES,
				ITEM_SYSTEM_VEHICLE_SADDLE		:	cschannel_msgs.ITEM_VEHICLESADDLE_DES,
				ITEM_SYSTEM_VEHICLE_HALTER		:	cschannel_msgs.ITEM_VEHICLEHALTER_DES,
				ITEM_SYSTEM_VEHICLE_NECKLACE	:	cschannel_msgs.ITEM_VEHICLENECK_DES,
				ITEM_SYSTEM_VEHICLE_CLAW		:	cschannel_msgs.ITEM_VEHICLECLAW_DES,
				ITEM_SYSTEM_VEHICLE_MANTLE		:	cschannel_msgs.ITEM_VEHICLEMANTLE_DES,
				ITEM_SYSTEM_VEHICLE_BREASTPLATE	:	cschannel_msgs.ITEM_VEHICLEBREASTPLATE_DES,
				ITEM_SYSTEM_FLYING_VEHICLE_SADDLE	: cschannel_msgs.ITEM_FLYING_VEHICLESADDLE_DES,
				ITEM_SYSTEM_FLYING_VEHICLE_HALTER	: cschannel_msgs.ITEM_FLYING_VEHICLEHALTER_DES,
				ITEM_SYSTEM_FLYING_VEHICLE_NECKLACE	: cschannel_msgs.ITEM_FLYING_VEHICLENECK_DES,
				ITEM_SYSTEM_FLYING_VEHICLE_CLAW		: cschannel_msgs.ITEM_FLYING_VEHICLECLAW_DES,
				ITEM_SYSTEM_FLYING_VEHICLE_MANTLE	: cschannel_msgs.ITEM_FLYING_VEHICLEMANTLE_DES,
				ITEM_SYSTEM_FLYING_VEHICLE_BREASTPLATE	: cschannel_msgs.ITEM_FLYING_VEHICLEBREASTPLATE_DES,
				ITEM_SUPER_DRUG_HP					:	cschannel_msgs.ITEM_SUPERDRUG_DES,
				ITEM_SUPER_DRUG_MP					:	cschannel_msgs.ITEM_SUPERDRUG_DES,
				ITEM_MONEY						:	cschannel_msgs.ROLERELATION_INFO_7,
				ITEM_EQUIPMAKE_SCROLL			:	cschannel_msgs.ITEM_SCROLL_DES,
				ITEM_PET_BOOK					:	cschannel_msgs.ITEM_PETBOOK_DES,
				ITEM_DRUG_ROLE_HP				:	cschannel_msgs.ITEM_DRUG_DES,
				ITEM_DRUG_ROLE_MP				:	cschannel_msgs.ITEM_DRUG_DES,
				ITEM_DRUG_PET_HP				:	cschannel_msgs.ITEM_PET_DRUG_DES,
				ITEM_DRUG_PET_MP				:	cschannel_msgs.ITEM_PET_DRUG_DES,
				ITEM_YAO_DING					:	cschannel_msgs.ITEM_YAODING_DES,
				ITEM_SYSTEM_GODSTONE			:	cschannel_msgs.ITEM_GODSTONE_DES,
				ITEM_YIN_PIAO					:	cschannel_msgs.ITEM_YUANBAO_DES,
				ITEM_FASHION1					:	cschannel_msgs.ITEM_FASHION_DES,
				ITEM_FASHION2					:	cschannel_msgs.ITEM_FASHION_DES,
				ITEM_POTENTIAL_BOOK				:	cschannel_msgs.ITEM_POTENTIAL_BOOK,
				ITEM_TREASUREMAP				:	cschannel_msgs.ITEM_SYSTEM_DES,
				ITEM_PET_SUPER_DRUG_HP			:	cschannel_msgs.ITEM_PET_SUPERDRUG_DES,
				ITEM_PET_SUPER_DRUG_MP			:	cschannel_msgs.ITEM_PET_SUPERDRUG_DES,
				ITEM_STILETTO					:	cschannel_msgs.ITEM_STILETTO_DES,
				ITEM_VEHICLE_BOOK				:	cschannel_msgs.ITEM_VEHICLEBOOK_DES,
				ITEM_NATURE_JADE				:	cschannel_msgs.ITEM_NATURE_JADE_DES,
				ITEM_PET_PROPERTY_CHARM			: 	cschannel_msgs.ITEM_PET_CHARM_DES,
				ITEM_PET_ITEM					:   cschannel_msgs.ITEM_PET_ITEM_DES,
				ITEM_ANIMAL_TRAPS				:   cschannel_msgs.ITEM_ANIMAL_TRAPS_DES,
				ITEM_PET_EGG					:	cschannel_msgs.ITEM_PET_EGG_DES,
				ITEM_VEHICLE_FD					:	cschannel_msgs.ITEM_VEHICLE_FD_DES,
				ITEM_VEHICLE_TURN				:	cschannel_msgs.ITEM_VEHICLE_TURN_DES,
			}
# convert db's section value
m_itemAttrMap = {
				# 直接访问
				"id"						:	IAID,				# 物品唯一标识
				"amount"					:	IAAmount,			# 当前数量

				# query 访问
				# 道具通用属性
				"script"					:	IAScript,			# 实例库
				"name"						:	IAName,				# 名称
				"creator"					:	IACreator,			# 打造者名字
				"intensifyValue"			:	IAIntensifyValue,	# 装备强化防御值
				"icon"						:	IAIcon,				# 图标
				"model"						:	IAModel,			# 模型
				"particle"					:	IAParticle,			# 光效
				"type"						:	IAType,				# 类型
				"reqClasses"				:	IAClasses,			# 职业要求
				"reqGender"					:	IAReqGender,		# 性别要求
				"reqCredit"					:	IACredit,			# 声望要求
				"level"						:	IALevel,			# 道具等级
				"reqLevel"					:	IAReqlevel,			# 使用等级需求
				"prefix"					:	IAPrefix,			# 道具前缀
				"propertyPrefix"			:	IApropertyPrefix,	# 道具的属性前缀名
				"quality"					:	IAQuality,			# 道具品质
				"baseQualityRate"			:	IABaseQualityRate,	# 基础属性品质比率
				"excQualityRate"			:	IAExcQualityRate, 	# 附加属性品质比率
				"lifeType"					:	IALifeType,			# 时间消耗类型
				"lifeTime"					:	IALifeTime,			# 最大时间消耗延迟
				"deadTime"					:	IADeadTime,			# 物品死亡时间
				"price"						:	IAPrice,			# 价格
				"bindType"					:	IABindType,			# 绑定类型
				"useDegree"					:	IAUseDegree,		# 使用次数
				"stackable"					:	IAStackable,		# 可叠加数量
				"questID"					:	IAQuest,			# 任务
				"spell"						:	IASpell,			# 技能ID
				"freeze"					:	IAFreeze,			# 冻结状态
				"describe1"					:	IADescribe1,		# 附加描述1
				"describe2"					:	IADescribe2,		# 附加描述2
				"describe3"					:	IADescribe3,		# 附加描述3

				# 道具标志
				"flags"						:	IAFlags,			# 标志：是否能卖、是否能捡等
				"onlyLimit"					:	IAOnlyLimit,		# 物品唯一限制数

				# 装备专用部分
				"eq_wieldType"				:	IAWieldType,		# 装备类型(位置)
				"eq_hardinessMax"			:	IAMaxHardiness,		# 最大耐久度上限
				"eq_maxSlot"				:	IAMaxSlot,			# 最大镶嵌槽上限

				"eq_wieldStatus"			:	IAWieldStatus,		# 装备状态(是否已装备上去)
				"eq_hardiness"				:	IAHardiness,		# 当前耐久度
				"eq_hardinessLimit"			:	IAHardinessLimit,	# 当前耐久度上限
				"eq_intensifyLevel"			:	IAIntensifyLevel,	# 装备当前强化等级

				"eq_extraEffect"			:	IAExtraEffect,		# 装备附加属性
				"eq_suitEffect"				:	IASuitEffect,		# 套装属性
				"eq_createEffect"			:	IACreateEffect,		# 装备灌注属性
				"eq_suitEffectStatus"		:	IASuitEffectState,	# 套装属性状态( 是否已经激活 )
				"eq_obey"					:	IAObey,				# 装备认主属性 by姜毅
				"eq_upper"					:	IAUpper,			# 装备升品人
				"eq_upFlag"					:	IAUpFlag,			# 装备已升品标志
				"eq_slot"					:	IASlot,				# 当前已镶嵌槽数量
				"eq_limitSlot"				:	IALimitSlot,		# 当前能镶嵌槽上限

				# 武器专用部分
				# 戒指在处理方面与武器相同
				"eq_DPS"					:	IADPS,				# 武器/戒指DPS
				"eq_DPSArea"				:	IADPSArea,			# 武器/戒指DPS波动
				"eq_range"					:	IARange,			# 攻击范围
				"eq_delay"					:	IADelay,			# 攻击延迟(也就是速度)
				"eq_magicPower"				:	IAMagicPower,		# 法术攻击力

				# 防具专用部分
				# 项链在处理方面与防具相同
				"eq_pDamageLose"			:	IApDamageLose,			# 防具/项链 物理防御减伤
				"eq_sDamageLose"			:	IAsDamageLose,			# 防具/项链 法术防御减伤
				"eq_ResistChenmo"			:	IAResistChenmo,			# 头盔		抵抗沉默
				"eq_ResistGiddy"			:	IAResistGiddy,			# 衣服		抵抗眩晕
				"eq_ResistFix"				:	IAResistFix,			# 裤子		抵抗定身
				"eq_ReduceTargetHit"		:	IAReduceTargetHit,		# 护腕		降低对方物理命中点数
				"eq_ResistSleep"			:	IAResistSleep,			# 腰带		抵抗昏睡
				"eq_ResistHit"				:	IAResistHit,			# 手套		招架点数
				"eq_Dodge"					:	IADodge,				# 鞋子		闪避点数
				"eq_ReduceTargetMagicHit"	:	IAReduceTargetMagicHit,	# 项链		降低对方法术命中点数
				"eq_ReduceRoleD"		:	IAReduceRoleD,           #御敌属性
				"eq_AddRoleD"		        :	IAAddRoleD,           #破敌属性
				
				# 属性道具专用部分
				"springUsedCD"				:	IASpringUsedCD,		# 物品使用后所引发的CD
				"springIntonateOverCD"		:	IASpringIntonateOverCD,# 物品吟唱后所引发的CD
				"limitCD"					:	IALimitCD,			# 该法术受限CD

				# 符咒道具专用部分
				"ch_teleportRecord"			:	IATeleportRecord,	# 传送记录

				# 宝石专用部分
				"bj_extraEffect"			:	IABjExtraEffect,	# 宝石附加属性
				"bj_slotOrder"				:	IASlotOrder,		# 镶嵌槽位(只能镶嵌在第几个孔上面)
				"bj_slotLocation"			:	IASlotLocation,		# 镶嵌位置(头盔，武器...)
				"bj_slotOnly"				:	IASlotOnly,			# 镶嵌唯一性(同一个位置只允许镶嵌这种宝石一个)

				#魂魄石专用部分
				"ka_count"					:	IAKaCount,			# 魂魄石所吸收到的魂魄数量
				"ka_totalCount"				:	IAKaTotalCount,		# 魂魄石魂魄总数量

				# 背包专用部份
				"kb_kitbagClass"			:	IAKitbagClass,		# 背包的实例化类，即当该物品变成背包时用什么类
				"kb_maxSpace"				:	IAMaxSpace,			# 最大可容纳空间

				# 增加宠物快乐度道具相关属性
				"joyancy"					:	IAJoyancy,			# 宠物道具中附带快乐度的数量
				"pet_life"					:	IAPetLife,			# 宠物道具中附带寿命的数量
				
				#增加骑宠饱腹度
				"fullDegree"                            :IAFullDegree,# 骑宠粮草
				
				# 骑宠物品相关
				"vehicle_move_speed"		:	IAVehicleMoveSpeed,	# 骑宠的移动速度、骑宠装备的附加速度
				"vehicle_max_mount"			:	IAVehicleMaxMount,	# 骑宠的装载人数、骑宠装备的附加装载人数
				"vehicle_resist_giddy"		:	IAVehicleResistGiddy,# 抵抗眩晕率,马鞍专有属性

				# ￥
				"yuanbao"					:	IAYuanbao,			# 元宝

				# 战场积分
				"warIntegral"				:	IAWarIntegral,		# 战场积分

				# 大额补药
				"sd_maxPoint"				:	IAMaxPoint,			# 拥有点数上限
				"sd_currPoint"				:	IACurrPoint,		# 当前拥有点数

				# 法宝
				"tm_exp"					:	IATmExp,			# 法宝经验值
				"tm_potential"				:	IATmpotential,		# 法宝技能经验
				"tm_grade"					:	IATmGrade,			# 法宝品级
				"tm_baseEffect"				:	IATmBaseEffect,		# 法宝基础属性
				"tm_commonEffect"			:	IATmCommonEffect,	# 法宝凡品附加属性
				"tm_deityEffect"			:	IATmDeityEffect,	# 法宝神品附加属性
				"tm_immortalEffect"			:	IATmImmortalEffect,	# 法宝仙品附加属性
				"tm_flawEffect"				:	IATmFlawEffect,		# 法宝破绽属性

				# 制作卷
				"em_material"				:	IAMaterial,			# 制作卷需要的制作材料

				# 扩展属性
				"param1"					:	IAParam1,			# 附加属性1
				"param2"					:	IAParam2,			# 附加属性2
				"param3"					:	IAParam3,			# 附加属性3
				"param4"					:	IAParam4,			# 附加属性4
				"param5"					:	IAParam5,			# 附加属性5
				"param6"					:	IAParam6,			# 附加属性6
				"param7"					:	IAParam7,			# 附加属性7
				"param8"					:	IAParam8,			# 附加属性8
				"param9"					:	IAParam9,			# 附加属性9
				"param10"					:	IAParam10,			# 附加属性10

				# 动态坐标储存记录
				"treasure_position"			:	IATreasurePositon,	# 宝藏位置坐标（不包括地图名）
				"treasure_space"			:	IATreasureSpace,	# 宝藏位置坐标（不包括地图名）

				# 红包相关属性
				"hide_money"				:	IAHideMoney,		# 红包。10:42 2009-1-15，wsf

				#银票
				"yinpiao"					:	IAYinpiao,			# 银票
				"goldYuanbao"				:	IAGoldYuanbao,		# 金元宝
				"silverYuanbao"				:	IASilverYuanbao,	# 银元宝\
				"pickUpType"				:	IAPickUpType,		# 拾取类型
				"isSystemItem"				:	IAIsSystemItem,		# 系统装备标志
				
				# 造化玉牒相关属性
				"ydRealm"					:	IAYudieRealm,		# 境界
				"exp_item"					:	IAExpItem,			# 经验丹
				}

# 这是个物品属性列表，为了优化通信方式，使用固定索引而不直接用属性名，能大大减少通信消耗 16:23 2008-3-21 yk
m_itemAttrSendMap = m_itemAttrMap.keys()


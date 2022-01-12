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
	@intensifyObeyCommonCalc����װ��ǿ����������صĹ�������
	@func: EquipExp�еĹ�ʽ���㷽��
	@return: ( ����������ǿ�������ַ������������������ַ������� )
	"""
	exp = func.im_self # ���ݰ󶨷�����ȡ��ʽ����ʵ��
	itemInstance = exp.equip
	reference = exp.owner

	calcIntensifyInc = lambda x = func : x( ignoreObey = True, ignoreZipPercent = True, ignoreWieldCalc = True ) - x( ignoreObey = True, ignoreIntensify = True, ignoreZipPercent = True, ignoreWieldCalc = True )
	calcObeyInc = lambda x = func: x( ignoreIntensify = True, ignoreZipPercent = True, ignoreWieldCalc = True ) - x( ignoreObey = True, ignoreObey = True, ignoreZipPercent = True, ignoreWieldCalc = True )
	calcTotal = lambda x = func: x( ignoreZipPercent = True, ignoreWieldCalc = True )

	total = calcTotal()

	# ��������󶨸�������
	addDes = ""
	addValue = 0
	if itemInstance.isObey():
		addValue = calcObeyInc()
		addDes = "(+%i)" % addValue

	# װ��ǿ����������
	intenDes = ""
	intenValue = 0
	intensify = itemInstance.getIntensifyLevel()
	if intensify != 0:
		intenValue = calcIntensifyInc()
		intenDes = "(+%i)" % intenValue

	return ( total, addDes, intenDes )

class IADefault:
	"""
	readFromConfig() ���ڴ������ļ��ж�ȡһ�����Ե�ֵ
	addToStream() �� createFromStream() ������Ҫ���ڴ�server���͸�����Ϣ��client�á������ų������᲻���������ɱ��浽���ݿ��е����ݡ�
	"""
	@staticmethod
	def readFromConfig( attrDict, dict ):
		"""
		��һ�������ļ���python dict���ȡ���ݵ�attrDict��

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

		@param value: ÿ�����͵�ֵ����һ��,���ӿ��Լ�ȷ��
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
		���������������

		@param itemInstance: �̳���CItemBase����Ʒʵ��
		@type  itemInstance: CItemBase
		@param    reference: ���entity,��ʾ��˭����Ϊ���������Ĳ�����
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
		������Ʒ���������������Ϣ����
		"""
		creditsDict = itemInstance.credit()
		recreditsDict = {}
		for key,creditsValue in creditsDict.iteritems():
			value = reference.getPrestige(key)	#�������
			des = cschannel_msgs.ITEMATTRCLASS_INFO_5 + factionMgr.getName(key) + cschannel_msgs.ITEMATTRCLASS_INFO_6 + reference.getPretigeDes(creditsValue)	#��ȡ������Ϣ���ַ��� �� ��Ҫ�����������
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
		if intensifyLevel and intensifyLevel >0: # ����װ����ǿ���ȼ���ʾ �� XX +9
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
		# Ĭ�ϵ�����������1�������¼
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
		ȡ������ ��valueС��10000����0ʱ����ʾΪ1,������ʾΪvalue/10000
		��ط��Ĺ�ʽ�ı�Ļ���Ҫ�ٸ�DurabilityItem.py������;öȹ�ʽ����Ȼ����ɲ�һ��
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
		��������������������Ϣ
		ע��֮�����������ӿ�����Ϊ��Ʒ�ĺܶ��������Ҳ����Ϊ�����Ʒ�Ļ������ԣ����
		��Ϊ������Ʒ����������������Ҫ�в�ͬ����ʾ��ʹ���������ڱ���⡣
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
		���������ڳ����������Ϣ
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
	����ǰ׺����дװ��Ӧ�þ�������ǰ׺��������readFromConfigģ��
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

		# ����Ͳ߻����ò�һ�£�������С100����updated by mushuang
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
		if range == None:			#���û�й������룬����""
			return ""
		return cschannel_msgs.ITEMATTRCLASS_INFO_26 % range

	@staticmethod
	def descriptionList( itemInstance, reference ):
		range = itemInstance.query( "eq_range" )
		if range == None:			#���û�й������룬����""
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
		if delay == None:			#���û�й����ٶȣ�����""
			return ""
		return cschannel_msgs.ITEMATTRCLASS_INFO_28 % delay

	@staticmethod
	def descriptionList( itemInstance, reference ):
		delay = itemInstance.query( "eq_delay" )
		if delay == None:			#���û�й����ٶȣ�����""
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
		# ��ȡ��Ҫ��ְҵ�б�
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
		# ��ȡ��Ҫ��ְҵ�б�
		classlist = itemInstance.queryReqClasses()
		if not classlist: return ""
		exp = EquipExp( itemInstance, reference )

		return cschannel_msgs.ITEM_MAGICARMOR_PER_DES % intensifyObeyCommonCalc( exp.getMagicArmorBase )

	@staticmethod
	def descriptionList( itemInstance, reference ):
		# ��ȡ��Ҫ��ְҵ�б�
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
		pass	# ��ʱɶ������

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
		@return: string by ����
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
		# ������Ϊ0ʱ����ʾ�������ƻ�ȡ
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
		# ������Ϊ0ʱ����ʾ�������ƻ�ȡ
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
		���ش�����Ҫ�Ĳ���
		"""
		return SpecialComposeExp._instance.getMaterials(itemInstance.id)

class IAParam1( IADefault ):
	@staticmethod
	def readFromConfig( attrDict, param ):
		# ������Ϊ0ʱ����ʾ�������ƻ�ȡ
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

class IAHideMoney( IADefault ):		# 10:47 2009-1-15��wsf
	"""
	��������صĽ�Ǯ
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
		@return : ���ǰ������
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

#����	
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
	
#�Ƶ�
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
				# ֱ�ӷ���
				"id"						:	IAID,				# ��ƷΨһ��ʶ
				"amount"					:	IAAmount,			# ��ǰ����

				# query ����
				# ����ͨ������
				"script"					:	IAScript,			# ʵ����
				"name"						:	IAName,				# ����
				"creator"					:	IACreator,			# ����������
				"intensifyValue"			:	IAIntensifyValue,	# װ��ǿ������ֵ
				"icon"						:	IAIcon,				# ͼ��
				"model"						:	IAModel,			# ģ��
				"particle"					:	IAParticle,			# ��Ч
				"type"						:	IAType,				# ����
				"reqClasses"				:	IAClasses,			# ְҵҪ��
				"reqGender"					:	IAReqGender,		# �Ա�Ҫ��
				"reqCredit"					:	IACredit,			# ����Ҫ��
				"level"						:	IALevel,			# ���ߵȼ�
				"reqLevel"					:	IAReqlevel,			# ʹ�õȼ�����
				"prefix"					:	IAPrefix,			# ����ǰ׺
				"propertyPrefix"			:	IApropertyPrefix,	# ���ߵ�����ǰ׺��
				"quality"					:	IAQuality,			# ����Ʒ��
				"baseQualityRate"			:	IABaseQualityRate,	# ��������Ʒ�ʱ���
				"excQualityRate"			:	IAExcQualityRate, 	# ��������Ʒ�ʱ���
				"lifeType"					:	IALifeType,			# ʱ����������
				"lifeTime"					:	IALifeTime,			# ���ʱ�������ӳ�
				"deadTime"					:	IADeadTime,			# ��Ʒ����ʱ��
				"price"						:	IAPrice,			# �۸�
				"bindType"					:	IABindType,			# ������
				"useDegree"					:	IAUseDegree,		# ʹ�ô���
				"stackable"					:	IAStackable,		# �ɵ�������
				"questID"					:	IAQuest,			# ����
				"spell"						:	IASpell,			# ����ID
				"freeze"					:	IAFreeze,			# ����״̬
				"describe1"					:	IADescribe1,		# ��������1
				"describe2"					:	IADescribe2,		# ��������2
				"describe3"					:	IADescribe3,		# ��������3

				# ���߱�־
				"flags"						:	IAFlags,			# ��־���Ƿ��������Ƿ��ܼ��
				"onlyLimit"					:	IAOnlyLimit,		# ��ƷΨһ������

				# װ��ר�ò���
				"eq_wieldType"				:	IAWieldType,		# װ������(λ��)
				"eq_hardinessMax"			:	IAMaxHardiness,		# ����;ö�����
				"eq_maxSlot"				:	IAMaxSlot,			# �����Ƕ������

				"eq_wieldStatus"			:	IAWieldStatus,		# װ��״̬(�Ƿ���װ����ȥ)
				"eq_hardiness"				:	IAHardiness,		# ��ǰ�;ö�
				"eq_hardinessLimit"			:	IAHardinessLimit,	# ��ǰ�;ö�����
				"eq_intensifyLevel"			:	IAIntensifyLevel,	# װ����ǰǿ���ȼ�

				"eq_extraEffect"			:	IAExtraEffect,		# װ����������
				"eq_suitEffect"				:	IASuitEffect,		# ��װ����
				"eq_createEffect"			:	IACreateEffect,		# װ����ע����
				"eq_suitEffectStatus"		:	IASuitEffectState,	# ��װ����״̬( �Ƿ��Ѿ����� )
				"eq_obey"					:	IAObey,				# װ���������� by����
				"eq_upper"					:	IAUpper,			# װ����Ʒ��
				"eq_upFlag"					:	IAUpFlag,			# װ������Ʒ��־
				"eq_slot"					:	IASlot,				# ��ǰ����Ƕ������
				"eq_limitSlot"				:	IALimitSlot,		# ��ǰ����Ƕ������

				# ����ר�ò���
				# ��ָ�ڴ�������������ͬ
				"eq_DPS"					:	IADPS,				# ����/��ָDPS
				"eq_DPSArea"				:	IADPSArea,			# ����/��ָDPS����
				"eq_range"					:	IARange,			# ������Χ
				"eq_delay"					:	IADelay,			# �����ӳ�(Ҳ�����ٶ�)
				"eq_magicPower"				:	IAMagicPower,		# ����������

				# ����ר�ò���
				# �����ڴ������������ͬ
				"eq_pDamageLose"			:	IApDamageLose,			# ����/���� �����������
				"eq_sDamageLose"			:	IAsDamageLose,			# ����/���� ������������
				"eq_ResistChenmo"			:	IAResistChenmo,			# ͷ��		�ֿ���Ĭ
				"eq_ResistGiddy"			:	IAResistGiddy,			# �·�		�ֿ�ѣ��
				"eq_ResistFix"				:	IAResistFix,			# ����		�ֿ�����
				"eq_ReduceTargetHit"		:	IAReduceTargetHit,		# ����		���ͶԷ��������е���
				"eq_ResistSleep"			:	IAResistSleep,			# ����		�ֿ���˯
				"eq_ResistHit"				:	IAResistHit,			# ����		�мܵ���
				"eq_Dodge"					:	IADodge,				# Ь��		���ܵ���
				"eq_ReduceTargetMagicHit"	:	IAReduceTargetMagicHit,	# ����		���ͶԷ��������е���
				"eq_ReduceRoleD"		:	IAReduceRoleD,           #��������
				"eq_AddRoleD"		        :	IAAddRoleD,           #�Ƶ�����
				
				# ���Ե���ר�ò���
				"springUsedCD"				:	IASpringUsedCD,		# ��Ʒʹ�ú���������CD
				"springIntonateOverCD"		:	IASpringIntonateOverCD,# ��Ʒ��������������CD
				"limitCD"					:	IALimitCD,			# �÷�������CD

				# �������ר�ò���
				"ch_teleportRecord"			:	IATeleportRecord,	# ���ͼ�¼

				# ��ʯר�ò���
				"bj_extraEffect"			:	IABjExtraEffect,	# ��ʯ��������
				"bj_slotOrder"				:	IASlotOrder,		# ��Ƕ��λ(ֻ����Ƕ�ڵڼ���������)
				"bj_slotLocation"			:	IASlotLocation,		# ��Ƕλ��(ͷ��������...)
				"bj_slotOnly"				:	IASlotOnly,			# ��ǶΨһ��(ͬһ��λ��ֻ������Ƕ���ֱ�ʯһ��)

				#����ʯר�ò���
				"ka_count"					:	IAKaCount,			# ����ʯ�����յ��Ļ�������
				"ka_totalCount"				:	IAKaTotalCount,		# ����ʯ����������

				# ����ר�ò���
				"kb_kitbagClass"			:	IAKitbagClass,		# ������ʵ�����࣬��������Ʒ��ɱ���ʱ��ʲô��
				"kb_maxSpace"				:	IAMaxSpace,			# �������ɿռ�

				# ���ӳ�����ֶȵ����������
				"joyancy"					:	IAJoyancy,			# ��������и������ֶȵ�����
				"pet_life"					:	IAPetLife,			# ��������и�������������
				
				#������豥����
				"fullDegree"                            :IAFullDegree,# �������
				
				# �����Ʒ���
				"vehicle_move_speed"		:	IAVehicleMoveSpeed,	# �����ƶ��ٶȡ����װ���ĸ����ٶ�
				"vehicle_max_mount"			:	IAVehicleMaxMount,	# ����װ�����������װ���ĸ���װ������
				"vehicle_resist_giddy"		:	IAVehicleResistGiddy,# �ֿ�ѣ����,��ר������

				# ��
				"yuanbao"					:	IAYuanbao,			# Ԫ��

				# ս������
				"warIntegral"				:	IAWarIntegral,		# ս������

				# ��ҩ
				"sd_maxPoint"				:	IAMaxPoint,			# ӵ�е�������
				"sd_currPoint"				:	IACurrPoint,		# ��ǰӵ�е���

				# ����
				"tm_exp"					:	IATmExp,			# ��������ֵ
				"tm_potential"				:	IATmpotential,		# �������ܾ���
				"tm_grade"					:	IATmGrade,			# ����Ʒ��
				"tm_baseEffect"				:	IATmBaseEffect,		# ������������
				"tm_commonEffect"			:	IATmCommonEffect,	# ������Ʒ��������
				"tm_deityEffect"			:	IATmDeityEffect,	# ������Ʒ��������
				"tm_immortalEffect"			:	IATmImmortalEffect,	# ������Ʒ��������
				"tm_flawEffect"				:	IATmFlawEffect,		# ������������

				# ������
				"em_material"				:	IAMaterial,			# ��������Ҫ����������

				# ��չ����
				"param1"					:	IAParam1,			# ��������1
				"param2"					:	IAParam2,			# ��������2
				"param3"					:	IAParam3,			# ��������3
				"param4"					:	IAParam4,			# ��������4
				"param5"					:	IAParam5,			# ��������5
				"param6"					:	IAParam6,			# ��������6
				"param7"					:	IAParam7,			# ��������7
				"param8"					:	IAParam8,			# ��������8
				"param9"					:	IAParam9,			# ��������9
				"param10"					:	IAParam10,			# ��������10

				# ��̬���괢���¼
				"treasure_position"			:	IATreasurePositon,	# ����λ�����꣨��������ͼ����
				"treasure_space"			:	IATreasureSpace,	# ����λ�����꣨��������ͼ����

				# ����������
				"hide_money"				:	IAHideMoney,		# �����10:42 2009-1-15��wsf

				#��Ʊ
				"yinpiao"					:	IAYinpiao,			# ��Ʊ
				"goldYuanbao"				:	IAGoldYuanbao,		# ��Ԫ��
				"silverYuanbao"				:	IASilverYuanbao,	# ��Ԫ��\
				"pickUpType"				:	IAPickUpType,		# ʰȡ����
				"isSystemItem"				:	IAIsSystemItem,		# ϵͳװ����־
				
				# �컯����������
				"ydRealm"					:	IAYudieRealm,		# ����
				"exp_item"					:	IAExpItem,			# ���鵤
				}

# ���Ǹ���Ʒ�����б�Ϊ���Ż�ͨ�ŷ�ʽ��ʹ�ù̶���������ֱ�������������ܴ�����ͨ������ 16:23 2008-3-21 yk
m_itemAttrSendMap = m_itemAttrMap.keys()


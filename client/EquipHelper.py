# -*- coding: gb18030 -*-

"""
���޿ͻ���ʹ�õ�װ����ֵ������ by mushuang
"""

# @calcIntensifyInc: ����ĳװ��������ǿ�����µļ�ֵ
# @x: EquipExp����İ󶨷���
# @return: װ����ǿ�����µļ�ֵ
calcIntensifyInc = lambda x: x( ignoreObey = True, ignoreZipPercent = True, ignoreWieldCalc = True ) - x( ignoreObey = True, ignoreIntensify = True, ignoreZipPercent = True, ignoreWieldCalc = True )

# @calcObeyInc: ����ĳװ���������������µļ�ֵ
# @x: EquipExp����İ󶨷���
# @return: װ�����������µļ�ֵ
calcObeyInc = lambda x: x( ignoreIntensify = True, ignoreZipPercent = True, ignoreWieldCalc = True ) - x( ignoreIntensify = True, ignoreObey = True, ignoreZipPercent = True, ignoreWieldCalc = True )

# @calcTotal: ����ĳװ�����Ե���ֵ�������������������Լ�ǿ��������֮��ļ�ֵ��
# @x: EquipExp����İ󶨷���
# @return: ĳװ�����Ե���ֵ
calcTotal = lambda x: x( ignoreZipPercent = True, ignoreWieldCalc = True )
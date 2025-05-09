# coding: utf-8
"""*****************************************************************************
* Copyright (C) 2019 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*****************************************************************************"""
import os
import glob

fileSymbolName = "CAL_FILE_SRC_TEST_"
numFileCntr = 0

_TEST_PATHS = ['atcacert/*', 'integration/*', 'jwt/*', 'api_atcab/*', 'api_calib/*', 'api_crypto/*', 'api_talib/*', 'hal/*', 'vectors/*']
_TEST_SOURCES = ['atca_test.c', 'atca_test_config.c', 'atca_test_console.c', 'atca_utils_atecc608.c', 'cmd-processor.c']
_TEST_HEADERS = ['atca_test.h', 'cbuf.h', 'cmd-processor.h']


def CALSecFileUpdate(symbol, event):
    symObj = event['symbol']
    selected_key = symObj.getSelectedKey()

    if selected_key == "SECURE":
        symbol.setSecurity("SECURE")
    elif selected_key == "NON_SECURE":
        symbol.setSecurity("NON_SECURE")


def add_value_to_list(symbol_list, value):
    values = list(symbol_list.getValues())
    if value not in values:
        symbol_list.addValue(value)


def del_value_from_list(symbol_list, value):
    values = list(symbol_list.getValues())
    if value in values:
        symbol_list.clearValues()
        values.remove(value)
        for v in values:
            symbol_list.addValue(v)


def AddFile(component, src_path, dest_path, proj_path, file_type = "SOURCE", isMarkup = False, enable=True):
    global fileSymbolName
    global numFileCntr
    srcFile = component.createFileSymbol(fileSymbolName + str(numFileCntr) , None)
    srcFile.setSourcePath(src_path)
    srcFile.setDestPath(dest_path)
    srcFile.setProjectPath(proj_path)
    srcFile.setType(file_type)
    srcFile.setOutputName(os.path.basename(src_path))
    srcFile.setMarkup(isMarkup)
    srcFile.setEnabled(enable)
    try:
        CALSecValue = Database.getComponentByID('cryptoauthlib').getSymbolByID('CAL_NON_SECURE').getValue()
        if CALSecValue == True:
            srcFile.setSecurity("SECURE")
    except:
        pass
    srcFile.setDependencies(CALSecFileUpdate, ["cryptoauthlib.CAL_NON_SECURE"])
    numFileCntr += 1


def AddFilesDir(component, base_path, search_pattern, destination_path, project_path, enable=True):
    modulePath = os.path.expanduser(Module.getPath())

    filelist = glob.iglob(modulePath + os.sep + base_path + os.sep + search_pattern)
    print(modulePath + os.sep + base_path + os.sep + search_pattern)

    for x in filelist:
        _, ext = os.path.splitext(x)
        if ext in ['.c','.h']:
            source_path = os.path.relpath(os.path.abspath(x), modulePath)
            file_path = str(os.path.dirname(os.path.relpath(source_path, base_path)))
            file_destination = destination_path + os.sep + file_path
            file_project = project_path + '/' + file_path
            AddFile(component, source_path, file_destination, file_project.replace('\\','/'),
                file_type='HEADER' if ext is 'h' else 'SOURCE', enable=enable)


def handleMessage(messageID, args):
    return {}


def onAttachmentConnected(source, target):
    pass

def onAttachmentDisconnected(source, target):
    pass

def instantiateComponent(calTestingApplication):
    # Makes sure the Library is included as well.
    Database.activateComponents(['cryptoauthlib'])

    configName = Variables.get("__CONFIGURATION_NAME")

    targetPath = '../src/config/' + configName + '/library/cryptoauthlib'

    # Append the include paths in MPLABX IDE
    defSym = calTestingApplication.createSettingSymbol("CAL_XC32_INCLUDE_DIRS", None)
    defSym.setCategory("C32")
    defSym.setKey("extra-include-directories")

    defSym.setValue('{0}/test'.format(targetPath))
    defSym.setAppend(True, ';')
    try:
        CALSecValue = Database.getComponentByID('cryptoauthlib').getSymbolByID('CAL_NON_SECURE').getValue()
        if CALSecValue == True:
            defSym.setSecurity("SECURE")
    except:
        pass
    defSym.setDependencies(CALSecFileUpdate, ["cryptoauthlib.CAL_NON_SECURE"])


    # Add core library files
    for search_path in _TEST_PATHS:
        AddFilesDir(calTestingApplication, 'test', search_path, 'library/cryptoauthlib/test',
            'config/{}/library/cryptoauthlib/test'.format(configName))
    for fname in _TEST_SOURCES:
        AddFile(calTestingApplication, 'test' + os.path.sep + fname, 'library/cryptoauthlib/test',
                'config/{}/library/cryptoauthlib/test'.format(configName))
    for fname in _TEST_HEADERS:
        AddFile(calTestingApplication, 'test' + os.path.sep + fname, 'library/cryptoauthlib/test',
                'config/{}/library/cryptoauthlib/test'.format(configName), file_type='HEADER')

    AddFilesDir(calTestingApplication, 'third_party/unity', '*', 'library/cryptoauthlib/third_party/unity', 'config/{}/library/cryptoauthlib/third_party/unity'.format(configName))

    calLibDevCfgFile = calTestingApplication.createFileSymbol("CAL_LIB_DEV_CFG_DATA", None)
    calLibDevCfgFile.setSourcePath("harmony/templates/atca_devcfg_list.h.ftl")
    calLibDevCfgFile.setOutputName("atca_devcfg_list.h")
    calLibDevCfgFile.setDestPath("library/cryptoauthlib")
    calLibDevCfgFile.setProjectPath("config/" + configName + "/library/cryptoauthlib/")
    calLibDevCfgFile.setType("HEADER")
    calLibDevCfgFile.setOverwrite(True)
    calLibDevCfgFile.setMarkup(True)
    calLibDevCfgFile.setDependencies(CALSecFileUpdate, ["cryptoauthlib.CAL_NON_SECURE"])

    calTester = calTestingApplication.createBooleanSymbol("MULTIPLE_IFACE_SELECTED", None)
    calTester.setLabel("TEST MULTIPLE INSTANCES")
    calTester.setDefaultValue(False)
    calTester.setVisible(True)

    calTesterCmnt = calTestingApplication.createCommentSymbol("MULTIPLE_IFACE_COMMENT", calTester)
    calTesterCmnt.setLabel("!! Set if Multiple devices and interfaces are selected !! ")
    calTesterCmnt.setVisible(True)

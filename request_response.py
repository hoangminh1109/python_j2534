#coding:utf-8
import J2534
from J2534.Define import *
from J2534.Error import *
import sys
import time

def printMsg(msg):
    dataBuffer = msg.Data
    dataBufferLen = msg.DataSize
    can_id = (dataBuffer[0] << 24) | (dataBuffer[1] << 16) | (dataBuffer[2] << 8) | dataBuffer[3]
    msgData = dataBuffer[4:dataBufferLen]
    if type(msg) is J2534.ptTxMsg:
        msgType = 'Tx'
    elif type(msg) is J2534.ptRxMsg:
        msgType = 'Rx'
    else:
        msgType = '--'
    print(f"{msgType} {can_id:08X} [{' '.join(f'{byte:02X}' for byte in msgData)}]")


J2534.SetErrorLog(False)


devices = J2534.getDevices()
try:
    index = int(sys.argv[1], base=10)
except:
    index = 0
J2534.setDevice(index)


REQUEST_ID = 0x7E2
RESPONSE_ID = 0x7EA

ret, deviceID = J2534.ptOpen()
ret, channelID = J2534.ptConnect(deviceID, ProtocolID.ISO15765, 0, BaudRate.B500K)

maskMsg = J2534.ptMskMsg(TxFlags.ISO15765_FRAME_PAD)
maskMsg.setID(0xFFFFFFFF)

patternMsg = J2534.ptPatternMsg(TxFlags.ISO15765_FRAME_PAD)
patternMsg.setID(RESPONSE_ID)

flowcontrolMsg = J2534.ptPatternMsg(TxFlags.ISO15765_FRAME_PAD)
flowcontrolMsg.setID(REQUEST_ID)

ret, fiterid = J2534.ptStartMsgFilter(channelID, FilterType.FLOW_CONTROL_FILTER,
                                      maskMsg, patternMsg, flowcontrolMsg)


reqMsg = J2534.ptTxMsg(ProtocolID.ISO15765, TxFlags.ISO15765_FRAME_PAD)
reqMsg.setIDandData(REQUEST_ID, [0x18, 0x00, 0xFF, 0x00])

ret = J2534.ptWtiteMsgs(channelID, reqMsg, 1, 100)
if ret == STATUS_NOERROR:
    printMsg(reqMsg)
    
respMsg = J2534.ptRxMsg(TxFlags.ISO15765_FRAME_PAD)

timeout = 2
start = time.time()
while (time.time() - start <= timeout):
    ret = J2534.ptReadMsgs(channelID, respMsg, 1, 100)
    if ret == STATUS_NOERROR and respMsg.RxStatus == 0:
        printMsg(respMsg)

ret = J2534.ptDisconnect(channelID)
ret = J2534.ptClose(deviceID)

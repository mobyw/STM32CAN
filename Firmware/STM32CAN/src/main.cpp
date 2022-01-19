#include <Arduino.h>
#include <ArduinoJson.h>
#include <eXoCAN.h>

//#define STM32_CAN_SERVER
#define STM32_CAN_NODE

// defines for tx mode
#ifdef STM32_CAN_NODE
#define STM32_CAN_ID 1
#define CAN_TX_DELAY 1000
#endif

#define switchBase PB8
#define ledBase PA0
#define analogIn PB0
#define relay_1 PA15
#define relay_2 PB1
#define relay_3 PC13
#define relay_4 PB3

int id, fltIdx;
uint32_t last = 0;
const uint8_t dataLen = 8;

uint8_t txData[dataLen] = {0};
uint8_t rxData[dataLen] = {0};

uint8_t key = 0xff;
uint8_t led = 0xff;
uint8_t relay = 0xff;
uint16_t analog = 0xfff;
String str = "";

#ifdef STM32_CAN_SERVER
uint8_t rxIndex = 0;
bool getSerialData = 0;
bool controlFlag = 0;
const uint8_t rxBufferLength = 24;
char rxBuffer[rxBufferLength];
#endif

eXoCAN can;
#ifdef STM32_CAN_SERVER
HardwareSerial Serial1(PA10, PA9);
#endif

#ifdef STM32_CAN_NODE
void formatBuff()
{
    txData[0] = highByte(analog);
    txData[1] = lowByte(analog);
    txData[2] = key;
    txData[3] = relay & 0X0f;
    txData[4] = 0;
    txData[5] = 0;
    txData[6] = 0;
    txData[7] = 0;
}
#endif

#ifdef STM32_CAN_SERVER
void clrBuffer(void)
{
    rxIndex = 0;
}

void serialRead()
{
    char chTemp;

    while (Serial1.available())
    {
        chTemp = Serial1.read();

        rxBuffer[rxIndex++] = chTemp;

        if (chTemp == '.')
        {
            getSerialData = 1;
        }
        else if(chTemp == '~')
        {
            clrBuffer();
        }

        if (rxIndex == rxBufferLength)
        {
            clrBuffer();
        }
        break;
    }
}

void parseBuffer()
{
    char *subString;
    char *subStringNext;

    if (getSerialData)
    {
        getSerialData = false;

        id = (rxBuffer[0] - '0') * 100 + (rxBuffer[1] - '0') * 10 + (rxBuffer[2] - '0');
        for(uint8_t i = 0; i < 4; i++)
        {
            bitWrite(relay, i, rxBuffer[4 + i] - '0');
        }

        controlFlag = true;
    }
}
#endif

void setup()
{
#ifdef STM32_CAN_SERVER
    Serial1.begin(115200);
#endif
    // 11b IDs, 250k bit rate, external transceiver IC, portA pins 11,12
    can.begin(STD_ID_LEN, BR250K, PORTA_11_12_XCVR);
    // filter bank 0, filter 0: don't pass any, flt 1: pass all msgs
    can.filterMask16Init(0, 0, 0x7ff, 0, 0);

    for (uint8_t i = 0; i < 8; i++)
    {
        pinMode(switchBase + i, INPUT_PULLUP);
        pinMode(ledBase + i, OUTPUT);
        digitalWrite(ledBase + i, HIGH);
    }
    pinMode(analogIn, INPUT_ANALOG);
    pinMode(relay_1, OUTPUT_OPEN_DRAIN);
    pinMode(relay_2, OUTPUT_OPEN_DRAIN);
    pinMode(relay_3, OUTPUT_OPEN_DRAIN);
    pinMode(relay_4, OUTPUT_OPEN_DRAIN);

    digitalWrite(relay_1, HIGH);
    digitalWrite(relay_2, HIGH);
    digitalWrite(relay_3, HIGH);
    digitalWrite(relay_4, HIGH);

    delay(100);
}

void loop()
{
#ifdef STM32_CAN_NODE
    // tx every CAN_TX_DELAY
    if (millis() / CAN_TX_DELAY != last)
    {
        last = millis() / CAN_TX_DELAY;

        analog = analogRead(analogIn);
        
        bitWrite(relay, 0, digitalRead(relay_1));
        bitWrite(relay, 1, digitalRead(relay_2));
        bitWrite(relay, 2, digitalRead(relay_3));
        bitWrite(relay, 3, digitalRead(relay_4));

        for (uint8_t i = 0; i < 8; i++)
        {
            bitWrite(key, i, digitalRead(switchBase + i));
        }

        led = key;
        for (uint8_t i = 0; i < 8; i++)
        {
            digitalWrite(ledBase + i, bitRead(led, i));
        }

        formatBuff();
        can.transmit(STM32_CAN_ID, txData, dataLen);
    }
#endif

#ifdef STM32_CAN_SERVER
    serialRead();
    parseBuffer();

    if(controlFlag)
    {
        controlFlag = false;
        
        txData[3] = relay;
        can.transmit((id | (1 << 5)), txData, dataLen);

        delay(500);
    }
#endif

    // poll for rx
    if (can.receive(id, fltIdx, rxData) > -1)
    {
#ifdef STM32_CAN_SERVER
        String str = "{\"id\":" + String(id) + 
                     ",\"analog\":" + String((uint16_t)rxData[0] * 256 + (uint16_t)rxData[1]) + 
                     ",\"key\":" + String(rxData[2]) + 
                     ",\"relay\":" + String(rxData[3] & 0x0f) + 
                     "}\n";
        Serial1.print(str);
#endif
#ifdef STM32_CAN_NODE
        if (id == (STM32_CAN_ID | (1 << 5)))
        {
            digitalWrite(relay_1, bitRead(rxData[3], 0));
            digitalWrite(relay_2, bitRead(rxData[3], 1));
            digitalWrite(relay_3, bitRead(rxData[3], 0));
            digitalWrite(relay_4, bitRead(rxData[3], 1));
        }
#endif
    }
}

/**
  ******************************************************************************
  * @file    usbd_cdc_if.c
  * @brief   USB CDC interface (media access layer) for AERIS-10.
  *
  *          HAND-WRITTEN CubeMX-EQUIVALENT FILE (BETA). Follows the CubeMX
  *          generator output for the CDC class and the ST template
  *          Middlewares/ST/STM32_USB_Device_Library/Class/CDC/Src/usbd_cdc_if_template.c.
  *
  *          BETA defect fix C4 (docs/STM32/STM32_PROJECT_RECONSTRUCTION.md STM-T04):
  *          the original repository defined CDC_Receive_FS in main.cpp but the
  *          CubeMX template binds its own static CDC_Receive_FS, so received data
  *          never reached USBHandler. Here CDC_Receive_FS forwards every OUT
  *          packet to AERIS_USB_OnReceive() (defined in main.cpp) before re-arming
  *          the endpoint.
  ******************************************************************************
  */

#include "usbd_cdc_if.h"

/* Received data over USB are stored in this buffer */
uint8_t UserRxBufferFS[APP_RX_DATA_SIZE];

/* Data to send over USB CDC are stored in this buffer */
uint8_t UserTxBufferFS[APP_TX_DATA_SIZE];

extern USBD_HandleTypeDef hUsbDeviceFS;

static int8_t CDC_Init_FS(void);
static int8_t CDC_DeInit_FS(void);
static int8_t CDC_Control_FS(uint8_t cmd, uint8_t *pbuf, uint16_t length);
static int8_t CDC_Receive_FS(uint8_t *pbuf, uint32_t *Len);
static int8_t CDC_TransmitCplt_FS(uint8_t *pbuf, uint32_t *Len, uint8_t epnum);

USBD_CDC_ItfTypeDef USBD_Interface_fops_FS =
{
  CDC_Init_FS,
  CDC_DeInit_FS,
  CDC_Control_FS,
  CDC_Receive_FS,
  CDC_TransmitCplt_FS
};

/* Line coding reported back to the host (CubeMX default: 115200 8N1) */
static USBD_CDC_LineCodingTypeDef linecoding =
{
  115200, /* baud rate */
  0x00,   /* stop bits-1 */
  0x00,   /* parity - none */
  0x08    /* nb. of bits 8 */
};

/**
  * @brief  Initializes the CDC media low layer over the FS USB IP
  */
static int8_t CDC_Init_FS(void)
{
  /* Set Application Buffers */
  USBD_CDC_SetTxBuffer(&hUsbDeviceFS, UserTxBufferFS, 0);
  USBD_CDC_SetRxBuffer(&hUsbDeviceFS, UserRxBufferFS);
  return (USBD_OK);
}

static int8_t CDC_DeInit_FS(void)
{
  return (USBD_OK);
}

/**
  * @brief  Manage the CDC class requests
  */
static int8_t CDC_Control_FS(uint8_t cmd, uint8_t *pbuf, uint16_t length)
{
  UNUSED(length);
  switch (cmd)
  {
    case CDC_SEND_ENCAPSULATED_COMMAND:
    case CDC_GET_ENCAPSULATED_RESPONSE:
    case CDC_SET_COMM_FEATURE:
    case CDC_GET_COMM_FEATURE:
    case CDC_CLEAR_COMM_FEATURE:
      break;

    /*******************************************************************************/
    /* Line Coding Structure                                                       */
    /*-----------------------------------------------------------------------------*/
    /* Offset | Field       | Size | Value  | Description                          */
    /* 0      | dwDTERate   |   4  | Number |Data terminal rate, in bits per second*/
    /* 4      | bCharFormat |   1  | Number | Stop bits  0:1 / 1:1.5 / 2:2         */
    /* 5      | bParityType |   1  | Number | Parity 0:None 1:Odd 2:Even 3:Mark 4:Space */
    /* 6      | bDataBits   |   1  | Number | Data bits (5, 6, 7, 8 or 16).        */
    /*******************************************************************************/
    case CDC_SET_LINE_CODING:
      linecoding.bitrate    = (uint32_t)(pbuf[0] | (pbuf[1] << 8) | (pbuf[2] << 16) | (pbuf[3] << 24));
      linecoding.format     = pbuf[4];
      linecoding.paritytype = pbuf[5];
      linecoding.datatype   = pbuf[6];
      break;

    case CDC_GET_LINE_CODING:
      pbuf[0] = (uint8_t)(linecoding.bitrate);
      pbuf[1] = (uint8_t)(linecoding.bitrate >> 8);
      pbuf[2] = (uint8_t)(linecoding.bitrate >> 16);
      pbuf[3] = (uint8_t)(linecoding.bitrate >> 24);
      pbuf[4] = linecoding.format;
      pbuf[5] = linecoding.paritytype;
      pbuf[6] = linecoding.datatype;
      break;

    case CDC_SET_CONTROL_LINE_STATE:
    case CDC_SEND_BREAK:
    default:
      break;
  }
  return (USBD_OK);
}

/**
  * @brief  Data received over USB OUT endpoint are forwarded to the application
  *         (AERIS_USB_OnReceive -> USBHandler::processUSBData) and the endpoint is
  *         re-armed for the next packet.
  * @note   Runs in OTG_FS interrupt context: the application hook must be short
  *         and must not block (USBHandler only copies into a 256-byte buffer).
  */
static int8_t CDC_Receive_FS(uint8_t *Buf, uint32_t *Len)
{
  AERIS_USB_OnReceive(Buf, *Len);
  USBD_CDC_SetRxBuffer(&hUsbDeviceFS, &Buf[0]);
  USBD_CDC_ReceivePacket(&hUsbDeviceFS);
  return (USBD_OK);
}

/**
  * @brief  Transmit data over the CDC IN endpoint (non-blocking; returns USBD_BUSY
  *         while the previous transfer is still in progress).
  */
uint8_t CDC_Transmit_FS(uint8_t *Buf, uint16_t Len)
{
  uint8_t result = USBD_OK;
  USBD_CDC_HandleTypeDef *hcdc = (USBD_CDC_HandleTypeDef *)hUsbDeviceFS.pClassData;
  if (hcdc == NULL)
  {
    return USBD_FAIL;
  }
  if (hcdc->TxState != 0)
  {
    return USBD_BUSY;
  }
  USBD_CDC_SetTxBuffer(&hUsbDeviceFS, Buf, Len);
  result = USBD_CDC_TransmitPacket(&hUsbDeviceFS);
  return result;
}

static int8_t CDC_TransmitCplt_FS(uint8_t *Buf, uint32_t *Len, uint8_t epnum)
{
  UNUSED(Buf);
  UNUSED(Len);
  UNUSED(epnum);
  return (USBD_OK);
}

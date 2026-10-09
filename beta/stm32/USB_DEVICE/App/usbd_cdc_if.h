/**
  ******************************************************************************
  * @file    usbd_cdc_if.h
  * @brief   Header for usbd_cdc_if.c (AERIS-10, HAND-WRITTEN CubeMX-EQUIVALENT, BETA)
  ******************************************************************************
  */
#ifndef __USBD_CDC_IF_H__
#define __USBD_CDC_IF_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "usbd_cdc.h"

/* Define size for the receive and transmit buffer over CDC (CubeMX defaults) */
#define APP_RX_DATA_SIZE  2048
#define APP_TX_DATA_SIZE  2048

/** CDC Interface callback. */
extern USBD_CDC_ItfTypeDef USBD_Interface_fops_FS;

/**
  * @brief  Transmit data over the CDC IN endpoint.
  * @param  Buf: data buffer
  * @param  Len: number of bytes
  * @retval USBD_OK / USBD_BUSY / USBD_FAIL
  */
uint8_t CDC_Transmit_FS(uint8_t *Buf, uint16_t Len);

/**
  * @brief  Application hook called from the CDC receive callback with every
  *         OUT packet (BETA fix for defect C4 - see DECISIONS.md D-10).
  *         Implemented in Core/Src/main.cpp with C linkage; forwards to
  *         USBHandler::processUSBData().
  */
void AERIS_USB_OnReceive(const uint8_t *Buf, uint32_t Len);

#ifdef __cplusplus
}
#endif

#endif /* __USBD_CDC_IF_H__ */

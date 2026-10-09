/**
  ******************************************************************************
  * @file    usb_device.c
  * @brief   USB Device application entry: FS core + CDC class + interface fops.
  *          HAND-WRITTEN CubeMX-EQUIVALENT FILE (BETA); mirrors the CubeMX
  *          generator output for USB_DEVICE middleware class CDC on OTG_FS.
  ******************************************************************************
  */

#include "usb_device.h"
#include "usbd_core.h"
#include "usbd_desc.h"
#include "usbd_cdc.h"
#include "usbd_cdc_if.h"

void Error_Handler(void);

/* USB Device Core handle declaration (referenced by main.cpp:129 as extern). */
USBD_HandleTypeDef hUsbDeviceFS;

/**
  * Init USB device Library, add supported class and start the library
  */
void MX_USB_DEVICE_Init(void)
{
  if (USBD_Init(&hUsbDeviceFS, &FS_Desc, DEVICE_FS) != USBD_OK)
  {
    Error_Handler();
  }
  if (USBD_RegisterClass(&hUsbDeviceFS, &USBD_CDC) != USBD_OK)
  {
    Error_Handler();
  }
  if (USBD_CDC_RegisterInterface(&hUsbDeviceFS, &USBD_Interface_fops_FS) != USBD_OK)
  {
    Error_Handler();
  }
  if (USBD_Start(&hUsbDeviceFS) != USBD_OK)
  {
    Error_Handler();
  }
}

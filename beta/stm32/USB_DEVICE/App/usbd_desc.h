/**
  ******************************************************************************
  * @file    usbd_desc.h
  * @brief   USB device descriptors header (AERIS-10, HAND-WRITTEN CubeMX-EQUIVALENT, BETA)
  ******************************************************************************
  */
#ifndef __USBD_DESC__H__
#define __USBD_DESC__H__

#ifdef __cplusplus
extern "C" {
#endif

#include "usbd_def.h"

#define DEVICE_ID1 (UID_BASE)
#define DEVICE_ID2 (UID_BASE + 0x4)
#define DEVICE_ID3 (UID_BASE + 0x8)

#define USB_SIZ_STRING_SERIAL 0x1A

/** Descriptor for the USB Device (full-speed core). */
extern USBD_DescriptorsTypeDef FS_Desc;

#ifdef __cplusplus
}
#endif

#endif /* __USBD_DESC__H__ */

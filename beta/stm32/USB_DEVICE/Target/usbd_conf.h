/**
  ******************************************************************************
  * @file    usbd_conf.h
  * @brief   USB Device library low-level configuration (AERIS-10, STM32F746ZGT7,
  *          OTG_FS device-only, CDC class).
  *
  *          HAND-WRITTEN CubeMX-EQUIVALENT FILE (BETA). Content follows the
  *          STM32CubeMX "USB_DEVICE/Target/usbd_conf.h" generator output for a
  *          Device_Only OTG_FS + CDC project and the ST template
  *          Middlewares/ST/STM32_USB_Device_Library/Core/Inc/usbd_conf_template.h.
  *          Replace by the CubeMX-generated file once the .ioc is regenerated
  *          (see beta/stm32/CUBEMX_SETTINGS.md).
  ******************************************************************************
  */
#ifndef __USBD_CONF__H__
#define __USBD_CONF__H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "main.h"
#include "stm32f7xx.h"
#include "stm32f7xx_hal.h"

/*---------- -----------*/
#define USBD_MAX_NUM_INTERFACES     1U
/*---------- -----------*/
#define USBD_MAX_NUM_CONFIGURATION  1U
/*---------- -----------*/
#define USBD_MAX_STR_DESC_SIZ       512U
/*---------- -----------*/
#define USBD_DEBUG_LEVEL            0U
/*---------- -----------*/
#define USBD_LPM_ENABLED            0U
/*---------- -----------*/
#define USBD_SELF_POWERED           1U

/****************************************/
/* #define for FS and HS identification */
#define DEVICE_FS                   0

/* Memory management macros: static single allocation (CubeMX default) */
#define USBD_malloc         (void *)USBD_static_malloc
#define USBD_free           USBD_static_free
#define USBD_memset         memset
#define USBD_memcpy         memcpy
#define USBD_Delay          HAL_Delay

/* DEBUG macros */
#if (USBD_DEBUG_LEVEL > 0)
#define USBD_UsrLog(...)    printf(__VA_ARGS__);\
                            printf("\n");
#else
#define USBD_UsrLog(...)
#endif

#if (USBD_DEBUG_LEVEL > 1)
#define USBD_ErrLog(...)    printf("ERROR: ") ;\
                            printf(__VA_ARGS__);\
                            printf("\n");
#else
#define USBD_ErrLog(...)
#endif

#if (USBD_DEBUG_LEVEL > 2)
#define USBD_DbgLog(...)    printf("DEBUG : ") ;\
                            printf(__VA_ARGS__);\
                            printf("\n");
#else
#define USBD_DbgLog(...)
#endif

/* Exported functions */
void *USBD_static_malloc(uint32_t size);
void USBD_static_free(void *p);

#ifdef __cplusplus
}
#endif

#endif /* __USBD_CONF__H__ */

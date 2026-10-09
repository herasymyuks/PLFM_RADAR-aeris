#ifndef ADF4382A_MANAGER_H
#define ADF4382A_MANAGER_H

#include "main.h"
#include "adf4382.h"
#include "no_os_spi.h"
#include "stm32_spi.h"

// GPIO Definitions
// BETA (DECISIONS.md D-04): the original header hard-coded PG0..PG9, which main.h
// (schematic nets) assigns to the PA/clock power enables. All ADF4382 control
// lines are now aliases of the main.h macros (PG6..PG15).
#define TX_CE_Pin           ADF4382_TX_CE_Pin        /* PG15 */
#define TX_CE_GPIO_Port     ADF4382_TX_CE_GPIO_Port
#define TX_CS_Pin           ADF4382_TX_CS_Pin        /* PG14 */
#define TX_CS_GPIO_Port     ADF4382_TX_CS_GPIO_Port
#define TX_DELADJ_Pin       ADF4382_TX_DELADJ_Pin    /* PG13 */
#define TX_DELADJ_GPIO_Port ADF4382_TX_DELADJ_GPIO_Port
#define TX_DELSTR_Pin       ADF4382_TX_DELSTR_Pin    /* PG12 */
#define TX_DELSTR_GPIO_Port ADF4382_TX_DELSTR_GPIO_Port
#define TX_LKDET_Pin        ADF4382_TX_LKDET_Pin     /* PG11 */
#define TX_LKDET_GPIO_Port  ADF4382_TX_LKDET_GPIO_Port

#define RX_CE_Pin           ADF4382_RX_CE_Pin        /* PG9  */
#define RX_CE_GPIO_Port     ADF4382_RX_CE_GPIO_Port
#define RX_CS_Pin           ADF4382_RX_CS_Pin        /* PG10 */
#define RX_CS_GPIO_Port     ADF4382_RX_CS_GPIO_Port
#define RX_DELADJ_Pin       ADF4382_RX_DELADJ_Pin    /* PG7  */
#define RX_DELADJ_GPIO_Port ADF4382_RX_DELADJ_GPIO_Port
#define RX_DELSTR_Pin       ADF4382_RX_DELSTR_Pin    /* PG8  */
#define RX_DELSTR_GPIO_Port ADF4382_RX_DELSTR_GPIO_Port
#define RX_LKDET_Pin        ADF4382_RX_LKDET_Pin     /* PG6  */
#define RX_LKDET_GPIO_Port  ADF4382_RX_LKDET_GPIO_Port

// Frequency definitions
#define REF_FREQ_HZ      300000000ULL  // 300 MHz
#define TX_FREQ_HZ       10500000000ULL // 10.5 GHz
#define RX_FREQ_HZ       10380000000ULL // 10.38 GHz
#define SYNC_CLOCK_FREQ  60000000ULL   // 60 MHz sync clock

// SPI Configuration
#define ADF4382A_SPI_DEVICE_ID  4      // Using SPI4 (no-OS bus table slot; AD9523 uses slot 0)
#define ADF4382A_SPI_SPEED_HZ   10000000  // 10 MHz

// Phase delay configuration
#define DELADJ_MAX_DUTY_CYCLE   1000   // Maximum duty cycle for DELADJ PWM (1000 = 100%)
#define DELADJ_PULSE_WIDTH_US   10     // Width of DELSTR pulse in microseconds
#define PHASE_SHIFT_MAX_PS      10000  // Maximum phase shift in picoseconds

// Error code definitions
#define ADF4382A_MANAGER_OK               0
#define ADF4382A_MANAGER_ERROR_INVALID   -1
#define ADF4382A_MANAGER_ERROR_NOT_INIT  -2
#define ADF4382A_MANAGER_ERROR_SPI       -3

typedef enum {
    SYNC_METHOD_EZSYNC = 0,      // Software synchronization via SPI
    SYNC_METHOD_TIMED = 1        // Hardware synchronization via SYNCP/SYNCN
} SyncMethod;

typedef struct {
    struct adf4382_dev *tx_dev;
    struct adf4382_dev *rx_dev;
    struct no_os_spi_init_param spi_tx_param;
    struct no_os_spi_init_param spi_rx_param;
    bool initialized;
    SyncMethod sync_method;
    uint16_t tx_phase_shift_ps;  // Current TX phase shift in picoseconds
    uint16_t rx_phase_shift_ps;  // Current RX phase shift in picoseconds
} ADF4382A_Manager;

// Public functions
int ADF4382A_Manager_Init(ADF4382A_Manager *manager, SyncMethod method);
int ADF4382A_Manager_Deinit(ADF4382A_Manager *manager);
int ADF4382A_SetupTimedSync(ADF4382A_Manager *manager);
int ADF4382A_SetupEZSync(ADF4382A_Manager *manager);
int ADF4382A_TriggerTimedSync(ADF4382A_Manager *manager);
int ADF4382A_TriggerEZSync(ADF4382A_Manager *manager);
int ADF4382A_CheckLockStatus(ADF4382A_Manager *manager, bool *tx_locked, bool *rx_locked);
int ADF4382A_SetOutputPower(ADF4382A_Manager *manager, uint8_t tx_power, uint8_t rx_power);
int ADF4382A_EnableOutputs(ADF4382A_Manager *manager, bool tx_enable, bool rx_enable);

// New phase delay functions
int ADF4382A_SetPhaseShift(ADF4382A_Manager *manager, uint16_t tx_phase_ps, uint16_t rx_phase_ps);
int ADF4382A_GetPhaseShift(ADF4382A_Manager *manager, uint16_t *tx_phase_ps, uint16_t *rx_phase_ps);
int ADF4382A_SetFinePhaseShift(ADF4382A_Manager *manager, uint8_t device, uint16_t duty_cycle);
int ADF4382A_StrobePhaseShift(ADF4382A_Manager *manager, uint8_t device);

#endif // ADF4382A_MANAGER_H

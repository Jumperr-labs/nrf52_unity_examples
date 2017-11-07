#include "sensor_unit.h"
#include "nrf_drv_rtc.h"
#include "nrf_drv_clock.h"
#include "nrf_drv_rng.h"

	
const nrf_drv_rtc_t rtc = NRF_DRV_RTC_INSTANCE(0); /**< Declaring an instance of nrf_drv_rtc for RTC0. */
static bool has_measurement = false;
static uint8_t measurement = 0;

static void rtc_handler(nrf_drv_rtc_int_type_t int_type)
{
    if (int_type == NRF_DRV_RTC_INT_COMPARE0) {
        measurement++; // use sensor mock here, or you can use the sensor model with a data generator
        has_measurement = true;
    
        nrf_drv_rtc_counter_clear(&rtc);
        uint32_t err_code = nrf_drv_rtc_cc_set(&rtc, 0, 60 * 8, true);
        APP_ERROR_CHECK(err_code);

        nrf_drv_rtc_tick_enable(&rtc, true);        
    }
}

static void RtcConfig() {
    uint32_t err_code = nrf_drv_clock_init();
    APP_ERROR_CHECK(err_code);

	nrf_drv_clock_lfclk_request(NULL);
	
    nrf_drv_rtc_config_t config = NRF_DRV_RTC_DEFAULT_CONFIG;
    config.prescaler = 4095;
    err_code = nrf_drv_rtc_init(&rtc, &config, rtc_handler);
    APP_ERROR_CHECK(err_code);

    nrf_drv_rtc_tick_enable(&rtc, true);

    err_code = nrf_drv_rtc_cc_set(&rtc, 0, 60 * 8, true);
    APP_ERROR_CHECK(err_code);

    nrf_drv_rtc_enable(&rtc);
}

void InitializeSensorModule() {
	RtcConfig();
}

uint8_t GetSensorData() {
    APP_ERROR_CHECK_BOOL(has_measurement);
    has_measurement = false;
    return measurement * 2;
}

bool GetHasMeasurement() {
    return has_measurement;
}
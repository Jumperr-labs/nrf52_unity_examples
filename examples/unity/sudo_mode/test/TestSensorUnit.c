#include "unity.h"
#include "sensor_unit.h"

#include "nrf_delay.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_GetHasMeasurment_Should_Wait(void)
{
    TEST_ASSERT_EQUAL(0, GetHasMeasurement());
}

void test_GetHasMeasurment_Should_Stop_Waiting(void)
{
    TEST_ASSERT_EQUAL(0, GetHasMeasurement());

    (*((uint32_t *) 0x4000B504)) = (59 * 8); // setting the counter to one second before the interrupt to not wait one full minute
    
    nrf_delay_ms(1100);
    
    TEST_ASSERT_EQUAL(1, GetHasMeasurement());
}

void test_Measurment_Should_Grow_Incrementally_Should_Fail_Because_Result_Is_Doubled_by_2(void)
{
    TEST_ASSERT_EQUAL(1, GetHasMeasurement());

    uint32_t first_measurement = GetSensorData();

    (*((uint32_t *) 0x4000B504)) = (59 * 8); // setting the counter to one second before the interrupt to not wait one full minute
    
    nrf_delay_ms(1100);
    
    TEST_ASSERT_EQUAL(1, GetHasMeasurement());

    uint32_t second_measurement = GetSensorData();

    TEST_ASSERT_EQUAL(first_measurement + 1, second_measurement);
}

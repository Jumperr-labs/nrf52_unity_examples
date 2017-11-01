#ifndef __SENSOR_UNIT__
#define __SENSOR_UNIT__
#include <stdbool.h>
#include <stdint.h>


void InitializeSensorModule();
uint8_t GetSensorData();
bool GetHasMeasurement();

#endif
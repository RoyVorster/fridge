#include <stdio.h>

#include "esp_system.h"

#include "mcp9808.h"


extern "C" {
    void app_main(void);
}

void app_main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);

    Sensor sensor = Sensor();
    esp_err_t ret = sensor.initialize();
    ESP_ERROR_CHECK(ret);

    float temp = sensor.get_temperature();
    printf("Temperature: %f\n", temp);
}
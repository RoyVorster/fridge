#include <stdio.h>
#include "esp_system.h"

#include "mcp9808.h"
#include "ESPAsyncWebServer.h"

extern "C" {
    void app_main(void);
}

void app_main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);

    // Init sensor
    Sensor sensor = Sensor();
    esp_err_t ret = sensor.initialize();
    ESP_ERROR_CHECK(ret);

    // Retrieve data
    float temp = 0;
    while (true) {
        temp = sensor.get_temperature();
        printf("Temperature: %f\n", temp);

        vTaskDelay(500/portTICK_PERIOD_MS);
    }
}
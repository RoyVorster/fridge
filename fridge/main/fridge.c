#include <stdio.h>

#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "mqtt_client.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

#include "lwip/err.h"
#include "lwip/sys.h"

#include "mcp9808.h"

#define WIFI_SSID CONFIG_WIFI_SSID
#define WIFI_PWD CONFIG_WIFI_PWD
#define N_RETRIES_MAX 5

#define MQTT_BROKER_URL CONFIG_MQTT_BROKER_URL

static EventGroupHandle_t wifi_event_bits = NULL;
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAILED_BIT BIT1

static EventGroupHandle_t mqtt_event_bits = NULL;
#define MQTT_CONNECTED_BIT BIT0

static int n_retries = 0;

static void event_handler_mqtt(esp_mqtt_event_handle_t event) {
    switch (event->event_id) {
        case MQTT_EVENT_CONNECTED:
            printf("MQTT connected\n");
            xEventGroupSetBits(mqtt_event_bits, MQTT_CONNECTED_BIT);
            break;
        case MQTT_EVENT_DISCONNECTED:
            printf("MQTT disconnected\n");
            xEventGroupClearBits(mqtt_event_bits, MQTT_CONNECTED_BIT);
            break;
        default:
            // printf("Other MQTT event: %d\n", event->event_id);
            break;
    }
}

static void event_handler_wifi(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT) {
        switch (event_id) {
            case WIFI_EVENT_STA_START:
                esp_wifi_connect();
                break;
            case WIFI_EVENT_STA_DISCONNECTED: {
                if (n_retries > N_RETRIES_MAX) {
                    xEventGroupSetBits(wifi_event_bits, WIFI_FAILED_BIT);
                    break;
                }

                wifi_event_sta_disconnected_t *ev = (wifi_event_sta_disconnected_t*) event_data;
                printf("Connect failure reason: %d - retrying...\n", ev->reason);

                esp_wifi_connect(); n_retries++;
                break;
            }
        }
    } else if (event_base == IP_EVENT) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        printf("Got IP: " IPSTR "\n", IP2STR(&event->ip_info.ip));

        xEventGroupSetBits(wifi_event_bits, WIFI_CONNECTED_BIT);
    } else {
        printf("Unexpected event type in event handler...\n");
    }
}

void init_nvs(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
}

void init_wifi(void) {
    wifi_event_bits = xEventGroupCreate();

    ESP_ERROR_CHECK(esp_netif_init());

    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t conf = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&conf));

    // System wifi and IP event handler
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler_wifi, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler_wifi, NULL));

    wifi_config_t wifi_conf = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PWD,
        },
    };

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_conf));
    ESP_ERROR_CHECK(esp_wifi_start());

    EventBits_t bits = xEventGroupWaitBits(wifi_event_bits, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT, pdFALSE, pdFALSE, portMAX_DELAY);
    if (bits & WIFI_CONNECTED_BIT) {
        printf("Connected to wifi " WIFI_SSID "\n");
    } else if (bits & WIFI_FAILED_BIT) {
        printf("Failed to connect to wifi " WIFI_SSID "\n");
    } else {
        printf("Unexpected bit set...\n");
    }

    vEventGroupDelete(wifi_event_bits);
}

esp_mqtt_client_handle_t init_mqtt(void) {
    mqtt_event_bits = xEventGroupCreate();

    esp_mqtt_client_config_t mqtt_conf = {
        .uri = MQTT_BROKER_URL,
        .event_handle = event_handler_mqtt,
        .client_id = "publish",
    };

    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&mqtt_conf);
    esp_mqtt_client_start(client);

    return client;
}

void app_main(void) {
    init_nvs();
    init_wifi();
    esp_mqtt_client_handle_t client = init_mqtt();

    // Send some temperatures
    MCP9808_t sensor = init_sensor();
    while (1) {
        EventBits_t bits = xEventGroupGetBits(mqtt_event_bits);

        if (bits & MQTT_CONNECTED_BIT) {
            get_temperature(&sensor);

            printf("Temperature: %f\n", sensor.temperature);
            esp_mqtt_client_publish(client, "fridge/temperature", (char *) &sensor.temperature, sizeof(sensor.temperature), 1, 0);
        }

        vTaskDelay(500/portTICK_PERIOD_MS);
    }
}

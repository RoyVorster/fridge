#ifndef _MCP9808
#define _MCP9808

#include "driver/i2c.h"

#define I2C_SDA_IO 21
#define I2C_SCL_IO 22
#define I2C_FREQ_HZ 100000
#define I2C_PORT_NUM I2C_NUM_1

#define READ_BIT 0x1
#define WRITE_BIT 0x0
#define ACK_CHECK_DIS 0x0
#define ACK_CHECK_EN 0x1
#define ACK_VAL I2C_MASTER_ACK
#define NACK_VAL I2C_MASTER_NACK

// Device specific
#define MCP9808_REG_CONFIG 0x01
#define MCP9808_REG_AMBIENT_TEMP 0x05
#define MCP9808_REG_MANUF_ID 0x06
#define MCP9808_REG_DEVICE_ID 0x07
#define MCP9808_REG_RESOLUTION 0x08

#define A0 false
#define A1 false
#define A2 false
#define MCP9808_ADDR 0b0011000 | (A2 << 4) | (A1 << 5) | (A0 << 6)


typedef struct {
    i2c_config_t conf;
    uint8_t device_address;
    float temperature;
} MCP9808_t;

MCP9808_t init_sensor();
esp_err_t setup_sensor(MCP9808_t *device);

esp_err_t read_bytes(MCP9808_t *device, uint8_t reg, uint8_t* data, size_t size);
esp_err_t write_bytes(MCP9808_t *device, uint8_t reg, uint8_t* data, size_t size);

uint8_t read_8(MCP9808_t *device, uint8_t reg);
uint16_t read_16(MCP9808_t *device, uint8_t reg);
void write_16(MCP9808_t *device, uint8_t reg, uint16_t data);
void write_8(MCP9808_t *device, uint8_t reg, uint8_t data);

void get_temperature(MCP9808_t *device);


#endif // _MCP9808

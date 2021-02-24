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


i2c_config_t init_sensor();
uint8_t gen_device_address();

class Sensor {
public:
    Sensor();

    esp_err_t initialize();
    float get_temperature();

private:
    i2c_config_t conf;
    uint8_t device_address;

    esp_err_t read_bytes(uint8_t reg, uint8_t* data, size_t size);
    esp_err_t write_bytes(uint8_t reg, uint8_t* data, size_t size);

    uint8_t read_8(uint8_t reg);
    uint16_t read_16(uint8_t reg);
    void write_16(uint8_t reg, uint16_t data);
    void write_8(uint8_t reg, uint8_t data);
};

#endif // _MCP9808

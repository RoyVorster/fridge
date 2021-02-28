#include "mcp9808.h"

MCP9808_t init_sensor(void) {
    i2c_config_t conf;
    conf.mode = I2C_MODE_MASTER;
    conf.sda_io_num = I2C_SDA_IO;
    conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
    conf.scl_io_num = I2C_SCL_IO;
    conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
    conf.master.clk_speed = I2C_FREQ_HZ;

    i2c_param_config(I2C_PORT_NUM, &conf);

    esp_err_t driver_err = i2c_driver_install(I2C_PORT_NUM, conf.mode, 0, 0, 0);
    ESP_ERROR_CHECK(driver_err);

    MCP9808_t device = { .conf = conf, .device_address = (uint8_t) MCP9808_ADDR, .temperature = 0, };
    ESP_ERROR_CHECK(setup_sensor(&device));

    return device;
}

esp_err_t setup_sensor(MCP9808_t *device) {
    uint16_t manufacture_id = read_16(device, MCP9808_REG_MANUF_ID);
    if (manufacture_id != 0x00054) { return ESP_FAIL; };

    uint16_t device_id = read_16(device, MCP9808_REG_DEVICE_ID);
    if (device_id != 0x0400) { return ESP_FAIL; };

    // Empty config
    write_16(device, MCP9808_REG_CONFIG, 0x0);

    // Set resolution to highest
    write_8(device, MCP9808_REG_RESOLUTION, 0x3);

    return ESP_OK;
}

void get_temperature(MCP9808_t *device) {
    uint16_t data = read_16(device, MCP9808_REG_AMBIENT_TEMP);

    if (data != 0xFFFF) {
        device->temperature = data & 0x0FFF;
        device->temperature /= 16.0;

        if (data & 0x1000) {
            device->temperature -= 256;
        }
    }
}

esp_err_t write_bytes(MCP9808_t *device, uint8_t reg, uint8_t* data, size_t size) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();

    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (device->device_address << 1) | WRITE_BIT, ACK_CHECK_EN);
    i2c_master_write_byte(cmd, reg, ACK_CHECK_EN);

    i2c_master_write(cmd, data, size, ACK_CHECK_EN);
    i2c_master_stop(cmd);

    esp_err_t ret = i2c_master_cmd_begin(I2C_PORT_NUM, cmd, 1000 / portTICK_RATE_MS);
    i2c_cmd_link_delete(cmd);

    return ret;
}

esp_err_t read_bytes(MCP9808_t *device, uint8_t reg, uint8_t* data, size_t size) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();

    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (device->device_address << 1) | WRITE_BIT, ACK_CHECK_EN);
    i2c_master_write_byte(cmd, reg, ACK_CHECK_EN);

    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (device->device_address << 1) | READ_BIT, ACK_CHECK_EN);

    if (size > 1) {
        i2c_master_read(cmd, data, size - 1, ACK_VAL);
    }
    i2c_master_read_byte(cmd, data + size - 1, NACK_VAL);
    i2c_master_stop(cmd);

    esp_err_t ret = i2c_master_cmd_begin(I2C_PORT_NUM, cmd, 1000/portTICK_RATE_MS);
    i2c_cmd_link_delete(cmd);

    return ret;
}

void write_8(MCP9808_t *device, uint8_t reg, uint8_t data) {
    esp_err_t ret = write_bytes(device, reg, &data, 1);
    ESP_ERROR_CHECK(ret);
}

void write_16(MCP9808_t *device, uint8_t reg, uint16_t data) {
    uint8_t buffer[2] = { (uint8_t) data, (uint8_t) (data >> 8) };

    esp_err_t ret = write_bytes(device, reg, buffer, 2);
    ESP_ERROR_CHECK(ret);
}

uint8_t read_8(MCP9808_t *device, uint8_t reg) {
    uint8_t buffer;

    esp_err_t ret = read_bytes(device, reg, &buffer, 1);
    ESP_ERROR_CHECK(ret);

    return buffer;
}

uint16_t read_16(MCP9808_t *device, uint8_t reg) {
    uint8_t buffer[2];

    esp_err_t ret = read_bytes(device, reg, buffer, 2);
    ESP_ERROR_CHECK(ret);

    return (buffer[0] << 8) | (buffer[1] & 0xff);
}


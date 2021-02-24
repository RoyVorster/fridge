#include "mcp9808.h"

i2c_config_t init_sensor(void) {
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

    return conf;
}

uint8_t gen_device_address(void) {
    uint8_t addr = 0b0011000;
    addr |= (A2 << 4) | (A1 << 5) | (A0 << 6);

    return addr;
}

Sensor::Sensor() : conf(init_sensor()), device_address(gen_device_address()) {};

esp_err_t Sensor::initialize() {
    uint16_t manufacture_id = this->read_16(MCP9808_REG_MANUF_ID);
    if (manufacture_id != 0x00054) {  return ESP_FAIL; };

    uint16_t device_id = this->read_16(MCP9808_REG_DEVICE_ID);
    if (device_id != 0x0400) {  return ESP_FAIL; };

    // Empty config
    this->write_16(MCP9808_REG_CONFIG, 0x0);

    // Set resolution to highest
    this->write_8(MCP9808_REG_RESOLUTION, 0x3);

    return ESP_OK;
}

float Sensor::get_temperature() {
    float temp = 0;
    uint16_t data = this->read_16(MCP9808_REG_AMBIENT_TEMP);

    if (data != 0xFFFF) {
        temp = data & 0x0FFF;
        temp /= 16.0;

        if (data & 0x1000) {
            temp -= 256;
        }
    }

    return temp;
}

esp_err_t Sensor::write_bytes(uint8_t reg, uint8_t* data, size_t size) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();

    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (this->device_address << 1) | WRITE_BIT, ACK_CHECK_EN);
    i2c_master_write_byte(cmd, reg, ACK_CHECK_EN);

    i2c_master_write(cmd, data, size, ACK_CHECK_EN);
    i2c_master_stop(cmd);

    esp_err_t ret = i2c_master_cmd_begin(I2C_PORT_NUM, cmd, 1000 / portTICK_RATE_MS);
    i2c_cmd_link_delete(cmd);

    return ret;
}

esp_err_t Sensor::read_bytes(uint8_t reg, uint8_t* data, size_t size) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();

    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (this->device_address << 1) | WRITE_BIT, ACK_CHECK_EN);
    i2c_master_write_byte(cmd, reg, ACK_CHECK_EN);

    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (this->device_address << 1) | READ_BIT, ACK_CHECK_EN);

    if (size > 1) {
        i2c_master_read(cmd, data, size - 1, ACK_VAL);
    }
    i2c_master_read_byte(cmd, data + size - 1, NACK_VAL);
    i2c_master_stop(cmd);

    esp_err_t ret = i2c_master_cmd_begin(I2C_PORT_NUM, cmd, 1000/portTICK_RATE_MS);
    i2c_cmd_link_delete(cmd);

    return ret;
}

void Sensor::write_8(uint8_t reg, uint8_t data) {
    esp_err_t ret = this->write_bytes(reg, &data, 1);
    ESP_ERROR_CHECK(ret);
}

void Sensor::write_16(uint8_t reg, uint16_t data) {
    uint8_t buffer[2] = { (uint8_t) data, (uint8_t) (data >> 8) };

    esp_err_t ret = this->write_bytes(reg, buffer, 2);
    ESP_ERROR_CHECK(ret);
}

uint8_t Sensor::read_8(uint8_t reg) {
    uint8_t buffer;

    esp_err_t ret = this->read_bytes(reg, &buffer, 1);
    ESP_ERROR_CHECK(ret);

    return buffer;
}

uint16_t Sensor::read_16(uint8_t reg) {
    uint8_t buffer[2];

    esp_err_t ret = this->read_bytes(reg, buffer, 2);
    ESP_ERROR_CHECK(ret);

    return (buffer[0] << 8) | (buffer[1] & 0xff);
}


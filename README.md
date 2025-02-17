# Smartfan testbench

## Introduction.

This is a testbench utility application for Smartfan devices. It connects to a Device Under Test (DUT) and sends to it commands via MQTT protocol (MS protocol). The device repposnds with various actions and this way it demonstrates its ability to work.

## Installation.

### Requrements.

Requirements are as follows:

1. Windows or Linux OS.
2. Python >= 3.12+
3. pipx >= 1.7.0
4. poetry >= 1.8.5

Other needed dependencies are installed in the process of the installation of the application.

```shell
pip install pipx
pipx ensurepath
pipx install poetry
```

## Configuration.

The configuration system of the application is implemented in core/config.py and cli/app.py. It is organized at three levels:

1. Default settings, hard-coded in the source of the module
2. Configuration file, by default config.toml in current directory
3. Command line options

The line of priority is (lowest) ```default settings``` -> ```configuration file``` -> ```command line options``` (highest).

The default configuration comes with information about the template metadata: template name, version and description. This information can be used by application to know what template it lay on. This information should not be altered. However, new configuration options can be added as needed. The configuration is presented as a ```Dict``` object ```Config.DEFAULT_CONFIG```. This default configuration is created taking in respect most expected values of various options. They should NOT be altered.

Changing configugation and behvior is made in configuration file (config.toml) or at the command line.

### Configuration file.

Configuration file replicates default configuration and freely can be altered so as to adapt to concrete environment. It uses ```toml``` format. Option names in it are self descriptive. Comments are permitted.

### Command-line options.

Command line options are 'last chance' to modify behavior of the application. The have precedence over the configuration file. They are useful in batnch processing, when each device under test has its own data - par example MAC address or serial number.

```smartfan --help``` show all available options with help abput them.

## Operational modes

There are three operational modes:

* testbench - this mode executes sequentaly provided set of tests on Device Under Test (DUT)
* snonly - this mode just stotes serial number into the DUT
* monitor - this mode is used to monitor device state contnuously

`smartfan` can be in one of the three modes. The election is made by the option `--mode`, followed by one of above keywords.

### Testbench

This mode executes series of tests that prove DUT functionality.

### Snonly

This mode is used to set a serial numbr to already tested device that has valid WiFi credentials. Sometims there may be need to change the serial number, or the DUT is tested other ways

### Monitor

This mode executes repatedly `API_SENSORS` command and prints its results in user friendly format omn the screen. It can loop endlessly or for given number of loops. It can be terminated prematurely by pressing Ctrl-C.


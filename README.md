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

Configuration file replicates default configuration and freely can be altered so as to adapt to concrete environment. It uses ```toml``` format.Option names in it are self descriptive. Comments are permitted.

### Command-line options.

Command line options alre 'last chance' to modify behavior of the application. The have precedence over the configuration file. They are useful in batnch processing, when each device under test has its own data - par example MAC address or serial number.



# Synthetic SFTP extension

Each endpoint is a Synthetic Test representing the performance of an SFTP server

### How to use

1. Unzip `custom.remote.python.thirdparty_sftp.zip` to the `plugin_deployment` folder of the ActiveGate
    - By default on Linux: `unzip custom.remote.python.thirdparty_linux_commands.zip -d /opt/dynatrace/remotepluginmodule/plugin_deployment`
    - On windows: `C:\Program Files\dynatrace\remotepluginmodule\plugin_deployment`
2. Upload the extension to Dynatrace
    - Settings > Monitored technologies > Custom extensions > Upload extension
3. Configure your endpoints on the same screen
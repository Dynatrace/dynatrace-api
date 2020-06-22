# Synthetic Port check test extension

Each endpoint can check multiple ports on a single host

### How to use

1. Unzip `custom.remote.python.thirdparty_port.zip` to the `plugin_deployment` folder of the ActiveGate
    - By default on Linux: `unzip custom.remote.python.thirdparty_port.zip -d /opt/dynatrace/remotepluginmodule/plugin_deployment`
    - On windows: `C:\Program Files\dynatrace\remotepluginmodule\plugin_deployment`
2. Upload the extension to Dynatrace
    - Settings > Monitored technologies > Custom extensions > Upload extension   
3. Configure your endpoints on the same screen
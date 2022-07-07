# sewatchdog
### Because Why Let Torch Police Itself?
![Alt text](./screencap.gif?raw=true "Cerberus")
If Torch locks up, the watchdog is never executed. sewatchdog fixes that problem.
## Requires 
> https://torchapi.com/plugins/view/ccfc7807-5691-4cbb-b6e5-f4cb00035ef5

Just run the included file and the config file will autogenerate for you.

Adjust the config file to point to your servers **Instance** directory,
and Make sure you disable any other torch watchdog plugins!

sewatchdog will wait 1 minute before determining that the torch instance
has failed. Once it determines this it will kill the process and start
a new one. Make sure you run this script with the proper permissions.
(ie. With whatever user should run your server)

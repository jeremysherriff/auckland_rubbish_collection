# Auckland Council Rubbish Collection

An alternative if you don't want to leverage a Calendar in Home Assistant for the rubbish/recycling collection schedules.

## Installation

Either click this:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jeremysherriff&repository=auckland_rubbish_collection&category=Integration)

Or: manually add this github repo as a custom repository in HACS then search for and download "Auckland Council Rubbish Collection".

You will need to restart Home Assistant before proceeding.

## Setup
Requires that you find the "Assessment number" value from the Auckland Council [Find your rubbish, recycling, and food scraps collection day](https://www.aucklandcouncil.govt.nz/en/rubbish-recycling/rubbish-recycling-collections/rubbish-recycling-collection-days.html) page.

1.  Browse to the above page
2.  Enter your address, and click to select it
3.  The address selection box will confirm your address and show your **Assessment number**. Note down the Assessment number for the next steps.
<img width="600" alt="screenshot" src="https://github.com/user-attachments/assets/7755c205-7279-4564-bbb8-040525764b47" />


The rest of the setup is the same as any other Integration.

4.  In Home Assistant, browse to **Settings -> Devices & services: Integrations**. Click **+ Add Integration**
5.  Scroll or Search for **Auckland Council Rubbish Collection** and click to add it
6.  Enter an appropriate name for the location/address, and the 11-digit number you noted earlier.

## Additional Configuration
- Sensor data is updated every 5 hours by default. If this schedule does not work for you, can can use an automation to [define a custom polling interval](https://www.home-assistant.io/common-tasks/general/#why-use-an-automation-instead-of-changing-the-integrations-polling-configuration)
- The Geolocation Address sensor is disabled by default - this sensor was intended to assist me with being sure the address being polled was correct. Let me know if you find it useful for something and think it should be enabled by default.

# Auckland Council Rubbish Collection

An alternative if you don't want to leverage a Calendar in Home Assistant for the rubbish/recycling collection schedules.

## Installation

Either click this:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jeremysherriff&repository=auckland_rubbish_collection&category=Integration)

Or: manually add this github repo as a custom repository in HACS then search for and download "Auckland Council Rubbish Collection".

You will need to restart Home Assistant before proceeding.

## Setup
Requires that you find an enter the "an" value from the Auckland Council [Find your rubbish, recycling, and food scraps collection day](https://www.aucklandcouncil.govt.nz/rubbish-recycling/rubbish-recycling-collections/Pages/rubbish-recycling-collection-days.aspx) page.

1.  Browse to the above page
2.  Enter your address
3.  In the resulting **Your collection day** page, note the numbers at the end or the url after `?an=`
*  E.g. If the URL shows `collection-day-detail.aspx?an=12345678901` you need to note the number `12345678901`.

The rest of the setup is the same as any other Integration.

4.  In Home Assistant, browse to **Settings -> Devices & services: Integrations**. Click **+ Add Integration**
5.  Scroll or Search for **Auckland Council Rubbish Collection** and click to add it
6.  Enter an appropriate name for the location/address, and the 11-digit number from the URL above.

## Additional Configuration
- Sensor data is updated every 3 hours by default. If this schedule does not work for you, can can use an automation to update the entities as required.
- 

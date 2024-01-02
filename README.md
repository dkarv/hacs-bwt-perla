# Custom HA integration for the BWT Perla

_BWT Perla integration repository for [HACS](https://github.com/custom-components/hacs)._

### Requirements

* Local API enabled
    * available with firmware 2.02xx
    * enabled in Settings > General > Connection
* "Login-Code" sent to you by mail during registration
* local network connection (you need the ip address during setup)

### Installation

* Add this repository as user-defined repository in HACS
* Setup integration and enter host / ip address and the "Login-Code"
* Optional: set bwt total output as water source in the energy dashboard

### Get monthly / daily / hourly / per 15 minute / ... water usage

Unfortunately, the BWT API does not hand out these values. You can setup a _Utility Meter_ in Home Assistant to calculate them:

<img src="https://github.com/dkarv/hacs-bwt-perla/assets/3708591/f93f6c56-245b-42d7-83f4-0c652dd7268b" height="256" >

and provide a reset cycle to get daily / ... values:

<img src="https://github.com/dkarv/hacs-bwt-perla/assets/3708591/880e827b-b11e-4eb6-8f0e-bd683b50c0a2" height="256" >


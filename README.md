# Custom HACS integration for the BWT Perla

_BWT Perla integration repository for [HACS](https://github.com/custom-components/hacs)._

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dkarv&repository=hacs-bwt-perla)

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

### Entities

| Entity Id(s) | Information |
| ------------- | ------------- |
| total_output | Increasing value of the blended water = the total water consumed. Use this as water source on the energy dashboard. |
| errors, warnings | The fatal errors and non-fatal warnings. Comma separated list or empty if no value present. [List of values](https://github.com/dkarv/bwt_api/blob/main/src/bwt_api/error.py). |
| state | State of the device. Can be OK, WARNING, ERROR |
| holiday_mode | If the holiday mode is active (true) or not (false) |
| holiday_mode_start | Undefined or a timestamp if the holiday mode is set to start in the future |
| hardness_in, hardness_out | dH value of the incoming and outgoing water. Note that this value is not measured, but configured on the device during setup |
| customer_service, technician_service | Timestamp of the last service performed by the customer or technician |
| regenerativ_level | Percentage of salt left |
| regenerativ_days | Estimated days of salt left |
| regenerativ_mass | Total grams of salt used since initial device setup |
| last_regeneration_1, last_regeneration_2 | Last regeneration of column 1 or 2 |
| counter_regeneration_1, counter_regeneration_2 | Total count of regenerations since initial device setup |
| capacity_1, capacity_2 | Capacity the columns have left of water with hardness_out |
| day_output, month_output, year_output | The output of the current day, month and year |
| current_flow | The current flow rate. Please note that this value is not too reliable. Especially short flows might be completely missing, because this value is only queried every 30 seconds in the beginning. Only once a water flow is detected, it is queried more often. Once the flow is zero, the refresh rate cools down to 30 seconds. |

### Get monthly / daily / hourly / per 15 minute / ... water usage

__This is not needed anymore as the integration now reports daily, monthly and yearly consumption.__

You can setup a _Utility Meter_ in Home Assistant to calculate them:

<img src="https://github.com/dkarv/hacs-bwt-perla/assets/3708591/f93f6c56-245b-42d7-83f4-0c652dd7268b" height="256" >

and provide a reset cycle to get daily / ... values:

<img src="https://github.com/dkarv/hacs-bwt-perla/assets/3708591/880e827b-b11e-4eb6-8f0e-bd683b50c0a2" height="256" >


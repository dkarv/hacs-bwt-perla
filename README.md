# Custom HACS integration for the BWT Perla

_BWT Perla integration repository for [HACS](https://github.com/custom-components/hacs)._

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dkarv&repository=hacs-bwt-perla)

### Requirements

* Firmware 2.02xx [(more info)](#firmware)
* Local API enabled in Settings > General > Connection
* "Login-Code" sent to you by mail during registration
* local network connection (you need the ip address during setup)

### Installation

* Add this repository as user-defined repository in HACS
* Setup integration and enter host / ip address and the "Login-Code"
* Optional: set bwt total output as water source in the energy dashboard

### Firmware

The firmware 2.02xx is still in public beta. It can be requested through the customer service by mail and will be remotely installed on your device.
It looks like the customer service does not do the update on devices in the UK - it is still unclear why and what other countries are affected.
For more details and recent news, check out the discussion in the [HomeAssistant forum](https://community.home-assistant.io/t/bwt-best-water-tech-nology-support/270745/9999).

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
| day_output, month_output, year_output | The output of the current day, month and year. **This value sometimes is too low, but it is still unclear why. In general the total_output is more reliable.** [More information](https://github.com/dkarv/hacs-bwt-perla/issues/14) |
| current_flow | The current flow rate. Please note that this value is not too reliable. Especially short flows might be completely missing, because this value is only queried every 30 seconds in the beginning. Only once a water flow is detected, it is queried more often. Once the flow is zero, the refresh rate cools down to 30 seconds. |

and provide a reset cycle to get daily / ... values:

<img src="https://github.com/dkarv/hacs-bwt-perla/assets/3708591/880e827b-b11e-4eb6-8f0e-bd683b50c0a2" height="256" >


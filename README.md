# PowerDNS DynHost Updater Component for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

With the `pdns` integration you can keep your current IP address in sync with yourhostname or domain.  

To use the integration in your installation, add the following to your `configuration.yaml` file:

#### Configuration variables:
| Variable |  Required  |  Type  | Description |
| -------- | ---------- | ----------- | ----------- |
| `domain` | yes | string |  The subdomain you are modifying the DNS configuration for |
| `username` | yes | string | The DynHost username |
| `password` | yes | string | Password for the DynHost username |
| `url` | yes | string | Url for the DynHost server |
| `scan_interval` | no |  time | How often to call the update service. (default: 10 minutes) |

#### Basic Example:

```yaml
pdns:
  domain: subdomain.domain.com
  username: YOUR_USERNAME
  password: YOUR_PASSWORD
  url: http://xxxxx
```
Based on the official [No-IP.com](https://github.com/home-assistant/core/tree/dev/homeassistant/components/no_ip) and [Mythic Beasts](https://github.com/home-assistant/core/blob/dev/homeassistant/components/mythicbeastsdns) integrations. Thanks to the creators!

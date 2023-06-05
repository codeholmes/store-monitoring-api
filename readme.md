# Store Monitoring API

A backend app for monitoring uptime and downtime of the restaurants or stores.

![Python Verson: 3.9.13](https://img.shields.io/badge/Python-3.9.13-green)

## Endpoints

| Endpoints         | Method Allowed | Description                                    |
| ----------------- | -------------- | ---------------------------------------------- |
| `/trigger_report` | `GET`          | Returns a `report_id`                          |
| `/get_report`     | `POST`         | Returns status of report generation & CSV file |

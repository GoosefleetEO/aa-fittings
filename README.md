# Fittings
![pypi latest version](https://img.shields.io/pypi/v/fittings?label=latest)
![python versions](https://img.shields.io/pypi/pyversions/fittings)
![django versions](https://img.shields.io/pypi/djversions/fittings?label=django)
![license](https://img.shields.io/pypi/l/fittings?color=green)

A simple fittings and doctrine management app for [allianceauth](https://gitlab.com/allianceauth/allianceauth).

## Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Updating](#updating)
- [Settings](#settings)
- [Permissions](#permissions)


## Overview
This plugin serves as a replacement for the now defunct fleet-up service integration. It allows you to create and manage ship fits and doctrines all in a 
central location for your members to browse.

## Key Features
Fittings offers the following features:

* Support for importing fittings using the EFT format. 
  * Support for pulling fits from ESI *Coming Soon*
* Support for exporting fits as EFT format.
* Support for saving fits to EVE via ESI.
* Support for copying fits for use with ***Buy All***.
* Categorization of your fittings and doctrines to keep things organized
and easy to manage.
  * Access to categories can be restricted to specific groups.
* Tracks changes to module names.

## Screenshots

### Dashboard/Doctrine List
![dashboard/doctrine list](https://i.imgur.com/AUla6oR.png)

### Add Fitting
![add fitting](https://i.imgur.com/09Ht3Zy.png)

### Fitting List
![fitting list](https://i.imgur.com/JTyaot7.png)

### View Fitting
![view fitting](https://i.imgur.com/3H2PgXC.png)

### Add Doctrine
![add doctrine](https://i.imgur.com/WWSJHmb.png)

### View Doctrine
![view doctrine](https://i.imgur.com/9IJN3jt.png)

### Add a Category
![add category](https://i.imgur.com/0ytpF66.png)

### View all Categories
![view all categories](https://i.imgur.com/kRyr34p.png)

### View a Category
![view category](https://i.imgur.com/hs7DDqp.png)

## Installation
### 1. Install App
Install the app into your allianceauth virtual environment via PIP.

```bash
$ pip install fittings 
```

### 2. Configure AA settings

Configure your AA settings (`local.py`) as follows:

- Add `'fittings',` to `INSTALLED_APPS`
- Add these line to the bottom of the settings file to have module name updates

```python
# Fittings Module
CELERYBEAT_SCHEDULE['fittings_update_types'] = {
    'task': 'fittings.tasks.verify_server_version_and_update_types',
    'schedule': crontab(minute=0, hour='12'),
}
```
### 3. Finalize Install
Run migrations and copy static files. 

```bash
$ python manage.py migrate
$ python manage.py collectstatic
```

Restart your supervisor tasks.

### 4. Populate Types
As of v1.0.0 there is no need to populate types from SDE. This will be done on the fly from
ESI. 

## Updating
To update your existing installation of Fittings first enable your virtual environment.

Then run the following commands from your allianceauth project directory (the one that contains `manage.py`).

```bash
$ pip install -U fittings
$ python manage.py migrate
$ python manage.py collectstatic
```

Lastly, restart your supervisor tasks.

*Note: Be sure to follow any version specific update instructions as well. These instructions can be found on the `Tags` page for this repository.*

## Settings
This application has no settings that need to be added to your allianceauth settings (`local.py`) file.

## Permissions

Permission | Description
-- | --
`fitting.access_fittings` | This permission gives users access to the plugin.
`doctrine.manage` | User can add/delete ship fits and doctrines.

## Active Developers
* [Col Crunch](http://gitlab.com/colcrunch)
* [Crashtec](https://gitlab.com/huideaki)
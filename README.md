# Fittings
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

* Support for inputting fittings using the EFT format. 
  * Support for pulling fits from ESI *Coming Soon*
* Support for exporting fits as EFT format.
* Support for saving fits to EVE via ESI.
* All fits can be copied to the clipboard for ***Buy All***.
* Categorization of your fittings and doctrines to keep things organized
and easy to manage.
  * Access to categories can be restricted to specific groups.

## Screenshots

### Dashboard/Doctrine List
![dashboard/doctrine list](https://i.imgur.com/Xk4Eosh.png)

### Add Fitting
![add fitting](https://i.imgur.com/loFrtjj.png)

### Fitting List
![fitting list](https://i.imgur.com/f01q6wI.png)

### View Fitting
![view fitting](https://i.imgur.com/JwKKWUF.png)

### Add Doctrine
![add doctrine](https://i.imgur.com/MXkPI3c.png)

### View Doctrine
![view doctrine](https://i.imgur.com/FzVCb6S.png)

## Installation
### 1. Install App
Install the app into your allianceauth virtual environment via PIP.

```bash
$ pip install fittings 
```

### 2. Configure AA settings

Configure your AA settings (`local.py`) as follows:

- Add `'fittings',` to `INSTALLED_APPS`

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
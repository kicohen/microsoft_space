# Microsoft Space @ CMU Website
## Author: Kenny Cohen

### Purpose

This webapp is meant to be used both by users of the Microsoft Space and by the management team of the microsoft space. It will allow users to request events and see upcoming events and details about the space. Members of the management team will be able to staff events, approve of events and schedule events.

### Tech Details
* Django Version: 1.10.4
* Python Version: 3.5.1
* Development Database: sqlite
* Production Database: mysql

Uses angularJS, bootstrap and interactJS on clientside libraries included in repo.

### Configuration
To deploy this app, it highly suggested you change database systems to a more heavy duty database system such as mySQL.

You will also need to create your own config.ini file in the main directory of the project. 

### Features Implemented:
* User Registration
* Calendar
* Requesting Events
* Static pages
* Viewing Events
* View users list
* Edit and View User Profile
* Event Locations

### Features Partially Implemented:
* Event Roles

### Features Coming Soon:
* Messages on events (When creating an event there should be a "Event request successfully submitted." message.)

### Bugs:
* Location on event date on event details pages
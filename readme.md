# Microsoft Space @ CMU Website
## Author: Kenny Cohen

### Purpose

This webapp is meant to be used both by users of the Microsoft Space and by the management team of the microsoft space. It will allow users to request events and see upcoming events and details about the space. Members of the management team will be able to staff events, approve of events and schedule events.

### Tech Details
* Django Version: 1.10.4
* Python Version: 3.5.1
* Development Database: sqlite
* Production Database: mysql

### Clientside libraries include:
* angularJS
* bootstrap
* interactJS

Libraries are included in the repo.

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
* Sending Emails

### Features Partially Implemented:
* Event Roles

### Features To Be Added Soon:
* Keycard checkout
* Duplicating Events

### Bugs:
* Change the event status on the profile page to something that is easier to understand
* Responsiveness of slideshow on About page.
* Event Date picker on Event Update page.


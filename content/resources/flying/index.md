---
title: "VFR Flight Planner"
date: '2025-03-01T18:19:34+10:00'
description: "For any student VFR Pilots needing to complete an old fashioned VFR Flight Plan, here's a useful Excel version of the VFR Navigation Log (Jeppesen)"
layout: simple
thumbnail: navigation-log.png
aliases:
  - /good-stuff/vfrflightplanner/
  - /flying
---

For any student VFR Pilots needing to complete an old fashioned VFR Flight Plan, here's a useful Excel version of this flight planning tool.

Many years back I received my Private Pilot's License and in the process spent some time trying to find a decent cross country flight planning tool. I failed, and so created one of my own. Here's some of the highlights of the tool:

- Works on Excel for Windows and Excel for Mac (Excel 365 required)
- Planning check list
- Weight, balance and fuel calculations.
- Weather Log and FAA Flight Plan Form
- Navigation Log
- Weight, balance and fuel considerations
- Extensive automation, including a shared aircraft and airport database.
- No manual input of intermediary calculations. Where ever a figure or item can be calculated or looked up, it will be. No need for your calculator or E6B!
​
The basic layout of the navigation log is similar to the Jeppesen form, but takes it much further. Click on the image above for an example (this was the navigation log for my FAA check ride by the way).

Of course nowadays everyone's using Foreflight, but for those of you that prefer the traditional approach, this tool is for you!

### [Download the VFR Flight Planner v3.53](VFR-Flight-Planner.xltm)

{{< img-float src="/img/icons/icon-excel.jpg" href="VFR-Flight-Planner.xltm" side="left" width=50 >}}
Follow the installation instructions to install the flight planner before using. Requires Excel 365 and macros to be enabled.
{{< clear-float >}}

{{< callout >}}
{{< paypal-donate message="If you find this VFR Flight Planner tool useful, please make a small donation." >}}
{{< /callout >}}

## Some screen shots

{{< img-caption-float side="left" src="check-list.png" caption="Check List" width="450" >}}
{{< img-caption-float side="right" src="navigation-log.png" caption="Navigation Log" width="450" >}}
<br>
{{< img-caption-float side="right" src="weather-and-flight-plan.png" caption="Weather Briefing and Flight Plan" width="450" >}}
{{< clear-float >}}

## Nick's Training Notes

This document is a collection of various bits of information that I accumulated during my private pilot ground and flight training work, which I found difficult to commit to memory and therefore felt the need for somewhere to put it all down on paper. These are my ‘Cliff Notes’ for private pilot training.

{{< callout >}}

{{< img-float src="/img/icons/icon-word.png" href="nicks-notes.docx" side="left" width=50 >}}
{{< img-float src="/img/icons/icon-pdf.jpg" href="nicks-notes.pdf" side="left" width=50 >}}

Click on an icon to open the notes in PDF or Word format

{{< /callout >}}

## VFR Flight Planner Release History

#### March 2025 - Version 3.53

- Fixed a bug in the airport / aircraft database creation process.

#### December 2023 - Version 3.52

- Tested for compatibility with Sonoma (macOS 14.2) and Windows 11.
- Fixed problems with the Ribbon not displaying.
- This version no longer supports Excel 2013. Excel 365 dated Jan 2022 or later is required.
- Checks to confirm that Macros are enabled.
- Streamlined the installation process.
- Windows specific changes:
  - Installs to the User\Documents\Custom Office Templates folder ​if it exists.
  - Sets the Default Personal Templates Location Excel setting so that the File >> New >> Personal tab appears.
​​
#### December 2022 - Version 3.51

- Tested for compatibility with Ventura (macOS 13.1).
- Fixed a bug in the macro installation process. 

#### December 2020 - Version 3.50

- Tested for compatibility with Big Sur (macOS 11.0).
- You can now pick the preferred folder for the Airport & Aircraft database when installing the template (rather than it defaulting to your Documents folder). 

#### February 2020 - Version 3.42 

A couple of bug fixes to maintain compatibility with the latest version of Excel for Mac.

#### March 2019 - Version 3.41 

Fixed bug in calculation of remaining fuel on Navigation Log pages (thanks Scott Stratmoen for reporting).

#### July 2018 - Version 3.40 
Upgraded to work with the latest version of Office on Windows and Mac. Both the Windows and Mac version now use a custom ribbon bar for navigation. This version will only work with Excel 2013 or later for Windows or Mac.

​Mac users please note - Due to limitations with the recent versions of Excel for Mac, the shared Airport / Aircraft database will be stored in this location: _~/Library/Containers/com.microsoft.Excel/Data/Documents_. If you have a database from an earlier version, just copy it to this location.

#### April 2016 - Version 3.13

- Weather Briefing now shows correct total time enroute when using the second page of the nav log.

#### October 2015 - Version 3.12

- Corrected calculation of total distance
- Correct carry over of distance and fuel to second page of planner log

#### July 2015 - Version 3.1

- Corrected Total flight time and fuel consumption formulas on Navigation Log (formula missed two of the way points).
- Changed formatting in Airport Database so that runways (e.g. "08-27") are not reformatted into a date.
- Added a second page to the Navigation Log for longer trips.
- Improved the formatting of the document.

#### April 2013 - Version 3

- Full support for Excel 2011 for Mac including all automation and custom Flight Planner menu.
- New VFR Flight Planner ribbon in Excel 2007 / 2010 / 2013 for Windows
- Improved database management - aircraft and airports automatically synchronised with the shared database (so that you can share airport and aircraft data with fellow students).
- Formatting improvements and Bug fixes.

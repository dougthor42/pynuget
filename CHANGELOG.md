# Changelog for PyNuGet


## Unreleased
+ Updated `flask` to v1.0.2. Fixes CVE-2018-1000656. (#51)
+ Updated `requests` to v2.20.1. Fixes CVE-2018-18074.
+ Updated `lxml` to v4.6.3. Fixes CVE-2018-19787, CVE-2020-27783, and
  CVE-2021-28957. (#55)
+ Dropped support for Python 3.5, add support for Python 3.8 and 3.9. (#55)


## 0.2.5 (2018-07-26)
+ Removed the wrong logging message in the previous release. >_<


## 0.2.4 (2018-07-26) [YANKED]
+ Removed too-verbose logging in find_by_id.


## 0.2.3 (2018-07-26)
+ Fixed multiple instances of missing joins on queries... oops.


## 0.2.2 (2018-07-26)
+ Added line numbers to logging (#33).
+ Optionally run coverage when running in localhost development.
+ Fixed an issue where files with dependencies would break the "List" nuget
  command (#39)
+ Fixed an issue where deleting the last remaining version of a package
  would not delete the row in the Package table, thus causing subsequet pushes
  of the same version to fail. (#38)
+ Added exit codes for all CLI commands. (#37)


## 0.2.1 (2018-07-25)
+ Don't use a static value for the nuspec namespace.


## 0.2.0 (2018-07-23):
+ Added a very simple web UI which allows users to see all packages and
  versions available.
+ Updated where the version number is stored and how it's inlcuded in
  `setup.py`.


## 0.1.0 (2018-07-17): Initial Release
+ First release of working prototype. Contains `push`, `list`, and
  `delete` functionality.


## 0.0.1 (2018-04-20): Project Creation
+ Started work


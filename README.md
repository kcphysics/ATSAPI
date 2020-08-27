# ATSAPI

This project is to create a series of utilities that can be hosted and accessed via RESTful HTTP(S) calls for the [TrekMUSH: Among the Stars game](https://wiki.trekmush.org/index.php/Main_Page).

The goal here is to create both an API, python based Utilities based off those originally created by mar'Qon available [here](https://zen.trekmush.org/ats-navcomp/).

These are in no way comparable to those created by mar'Qon, but are a good shot to allow clients other than MUSHClient to use these with little hassle as most clients can make an HTTP call, or call out to the operating system where `curl` and `Invoke-RestMethod` are available.

## Documentation

The documentation for the API itself will be available at http://<server>:8080/api/doc, where a swagger doc will be listed

The api is developed in conjunction with another project [ATSPythonUtils](https://github.com/kcphysics/ATSPythonUtils).  The api just makes the interfaces built there available via a web server of some sort.

## Configuration

Configuration of this project, as far as getting it setup yourself, is important and will be done, but I haven't gotten there yet.

## Execution

Working on it.
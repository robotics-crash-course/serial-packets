# serial-packets
- A serialization tool used for rcc  

## Copyright & Licensing

Copyright (C) 2023  Michael Giglia [`<michael.a.giglia@gmail.com>`]

Copyright (C) 2023  Catherine Van West [`<cat@vanwestco.com>`]

Distributed under the [GPLv3] or later.

## Overview
- The serial-packets library allows users to make their own serializable data structures with minimal boiler plate. Eventually to be code generated!, to even FURTHER ENHANCE our laziness
- Is used to transfer "simple" information between two objects (think characters, floats, ints) using any sort of serial character stream. The messages are encoded into [base64](https://en.wikipedia.org/wiki/Base64) which allow it to be used by any character streaming interface. Currently it is used over serial and a UDP interface using lwip (but only currently implemented on the pico_w wireless hardware) in the "carrie" car and the rcc-pico lib respectively
- Though this library is in its infancy and current implementations are simply real-time built solutions for projects/courses related to rcc, the goal is to have an easily implementable but also easily customizable library to allow it to be used as a teaching tool that is not too dense to be navigated by programming novices, but not too rudimentary that it provides no value.
- This library was an idea by MG because they were sick of rewriting the same "G-CODE" style communications protocols for micro-controller projects. Thank you to CVW for bringing that idea into the physical world
- 
  
## Examples
### Primary Example
- In examples/inter-thread, mkdir build, cd build, cmake .., make -j4
- ./inter-thread will run an executable that transfers serialized random words between two threads
### Adding your own message boiler plate

### Attaching this interface to a serial hardware device

### Attaching this interface to an lwip implementation


[`<michael.a.giglia@gmail.com>`]: mailto:michael.a.giglia@gmail.com
[`<cat@vanwestco.com>`]: mailto:cat@vanwestco.com
[GPLv3]: LICENSE.md


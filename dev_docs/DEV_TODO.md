# Development TODOs

## Next rewrite

- parse prior month trip.
  - store on package, separate list?
- yaml out
- add equipment field to bid package
  - rename page equipment field to bid_equipment, or status equipment
- support split base/equipment output
  - all the combinations of base/equipment
- write more validations
- collect stats on bid package
- dutyperiod idx is 1 based to match flight.dp_idx
- rename flight.dutperiod_index to flight.dutyperiod_idx for consistency
- catch  errors in cli for better error reporting
- cli log
  - location
  - per parse log
  - 

## Bid Filter Feature

- Bid filter app uses plugin structure to collect filter objects.
- Bid filter app cli out first, for my use.

## Before next release

## Cli example

- Testing
  - cmd line tests
  - test resources
  - test parse against known values
  - tox
  - check output for sanity and usability
  - round trip serialize and test.
- Click
  - bash completion
- PyPi release
- Git
  - write out project structure in dev docs
- Documentation
  - api docs
  - Sphinx
    - Detailed how to instructions
    - installations instructions
    - github readme imports, badges, etc
  - Read the docs
    - Sphinx
    - check out cc for doc format examples
- CLI
  - split output files by base and equipment
- Model
  - BidPackage.base can be singular, satelite bases should be set.

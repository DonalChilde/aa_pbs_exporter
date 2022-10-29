# Development TODOs

## Next rewrite

- Convert to new project layout.
- Parse package to intermediate raw string state
  - include dataclasses with individual fields, and raw string to make debug easier.
  - include data from outside trip, to make a raw trip an atomic unit of data, eg. header or footer lines that may contain date or base
  - raw parse dataclass repr could use json.dumps for formattted output?
- Convert raw trip to a completed trip. Makes it easier to handle different pbs package versions, only have to change raw parse and converter.
- text chunk parser returns a generic parse result, and specific parse handler decides on next parse attempt based on parse result?
  - ParseResult
    - raw string - the string that was parsed
    - parser - the parser used
    - result_obj - the resulting parsed object - parse location only parses could still return a result dataclass to indicate location
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
  - completion time
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

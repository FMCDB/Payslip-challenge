# Payslip challenge

The remit of this project is to use unit tests to verify that a correct mapping exists 
from a GTN file to a Payrun file, to capture cases where a correct mapping does not exist
and to verify that the GTN file's file type and data are in the correct format.

Each test accesses a folder containing test data which causes it to fail.
Finally all tests are run on a folder containing test data which causes the tests to succeed.

## Execution

The tests are executed by running challenge.py. Test data can be changed by altering the files in each test folder.


## Test 1

Verifies that the GTN file is of type excel.


## Test 2

Verifies the existance of breaks in the GTN file.

Changes made to test files:
* Added two empty rows to GTN file at lines 18 and 26.


## Test 3

Verifies the repitition of the GTN file's header row.

Changes made to test files:
* Added additional header rows to GTN file at lines 2, 18, 28.


## Test 4

Checks if employee IDs exist in the Payrun file but not the GTN file.

Changes made to test files:
* Removed employees with IDs 1004, 1008, 1011, 1020, 1023, 1031 from GTN file.


## Test 5

Checks if employee IDs exist in the GTN file but not the Payrun file.

Changes made to test files:
* Removed employees with IDs 1002, 1011, 1017, 1023, 1029, 1031 from the Payrun file


## Test 6

Checks if Pay Elements in the GTN file do not have a mapping in the Payrun file.
Checks if Pay Elements in the GTN file have a mapping to a column in the Payrun file but that column 
does not exist in the Payrun file. 

Changes made to test files:
* Changed values of element7 and element4 GTN elements in mapping file.
* Changed 'BIK Health' to 'BIKHealth' in mapping file.
* Removed Backpay column from Payrun file.


## Test 7

Checks if Pay Elements in the Payrun file do not have a mapping in the GTN file.
Checks if Pay Elements in the GTN have a mapping to a column in the Payrun file but that column 
does not exist in the Payrun file. 

Changes made to test files:
* Changed values of Pension ER, BIK Voucher Payment and Bonus Payrun elements in mapping file.
* Removed element 9 column from GTN file


## Test 8

Verifies that the values of pay elements in the GTN file are of numeric type.

Changes made to test files:
* Replaced 5 GTN element values with strings in GTN file at columns: 'element4', 'element5', 'element8'


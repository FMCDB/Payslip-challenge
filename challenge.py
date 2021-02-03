import os
import unittest
import pandas as pd
import numpy as np
import json


class GetData():
    
    # Helper functions
    
    def get_vendors(mapping_file):
        with open(mapping_file) as json_data:
            data = json.load(json_data)
        mappings = pd.DataFrame(data['mappings'])
        not_used = pd.DataFrame(data['not_used'])
        vendors = pd.DataFrame(mappings.loc['vendor'])
        return {'vendors' : vendors, 'not_used' : not_used}
    
    def get_gtn_data(gtn_file, ids=False, pay_elements=False):
        gtn = pd.read_excel(gtn_file,engine='openpyxl')
        if pay_elements:
            gtn_pay_elements = pd.DataFrame(gtn.columns.values[4:]).rename(columns={0:'vendor'})
            return gtn_pay_elements
        if ids:
            # Rename ID column so join can take place
            gtn = gtn.rename(columns={'employee_id':'Employee ID'})
            gtn_ids = gtn['Employee ID']
            return gtn_ids
        return gtn
    
    def get_payrun_data(payrun_file, ids=False, pay_elements=False):
        payrun = pd.read_excel(payrun_file, engine='openpyxl')
        if pay_elements:
            payrun_elements = payrun.iloc[0][25:]
            # Fix merged cells in second row of payrun file
            payrun_pay_elements = pd.DataFrame(payrun_elements.fillna(payrun_elements.index.to_series()))
            return payrun_pay_elements
        if ids:
            payrun_ids = payrun['Employee ID'][1:-1]
            return payrun_ids
        return payrun



class TestPayslipsData(unittest.TestCase):
    
    # Excel files must not be open while tests are running
    
    def __init__(self, testName, tests_succeed=False):
        super(TestPayslipsData, self).__init__(testName)
        # Select the folder to use for the test
        self.folder = 'tests_succeed' if tests_succeed else testName
    
    # Test Functions
    
    def test_file_type(self):
        types = ['.xlsx','.xlsm','.xlsb','.xltx','.xltm','.xls','.xlt','.xml','.xlam','.xla','.xlw','.xlr']
        os.chdir(self.folder)
        filename = [filename for filename in os.listdir('.') if filename.startswith("GTN")][0]
        os.chdir('..')
        # Extracts the file type
        file_type = os.path.splitext(filename)[1]
        error_msg = '\n\n'+file_type+' is not a valid file type.\n'
        self.assertTrue(file_type in types, error_msg)
    
        
    def test_breaks(self):
        os.chdir(self.folder)
        gtn = pd.read_excel('GTN.xlsx',engine='openpyxl')
        os.chdir('..')
        # Returns index of rows with all NaN values
        breaks = gtn[gtn.isnull().all(axis=1)].index
        # Accounting for header row, Excel rows start at 1
        result = [n+2 for n in breaks]
        error_msg = '\n\nLine breaks found in the GTN file at the following rows:\n'
        self.assertEqual(len(result), 0, error_msg + str(result))
        
        
    def test_header_structure(self):
        os.chdir(self.folder)
        gtn = pd.read_excel('GTN.xlsx',engine='openpyxl')
        os.chdir('..')
        # Checks if there are multiple header rows
        duplicate_headers = gtn[(gtn==gtn.columns).all(axis=1)].index
        # Accounting for header row, Excel rows start at 1
        result = [n+2 for n in duplicate_headers]
        error_msg = '\n\nMultiple header rows found in the GTN file at the following rows:\n'
        self.assertEqual(len(result), 0, error_msg + str(result))
        
        
    def test_employees_missing_gtn(self):
        
        os.chdir(self.folder)
        gtn_ids = GetData.get_gtn_data('GTN.xlsx', ids=True)
        payrun_ids = GetData.get_payrun_data('Payrun.xlsx', ids=True)
        os.chdir('..')
        
        # Retrieve employee IDs which are present in Payrun file but missing in GTN
        missing = (pd.merge(gtn_ids, payrun_ids, how='outer', indicator=True)
                  .query('_merge == "right_only"')
                  .drop(columns='_merge'))
        
        result = list(missing['Employee ID'].astype(int))
        error_msg = '\n\nEmployees present in the Payrun File but missing in the GTN:\n'
        self.assertEqual(len(result), 0, error_msg + str(result))
        
        
    def test_employees_missing_payrun(self):
        
        os.chdir(self.folder)
        gtn_ids = GetData.get_gtn_data('GTN.xlsx', ids=True)
        payrun_ids = GetData.get_payrun_data('Payrun.xlsx', ids=True)
        os.chdir('..')
        
        # Retrieve employee IDs which are present in GTN but missing in Payrun file
        missing = (pd.merge(gtn_ids, payrun_ids, how='outer', indicator=True)
                  .query('_merge == "left_only"')
                  .drop(columns='_merge'))
        
        result = list(missing['Employee ID'].astype(int))
        error_msg = '\n\nEmployees present in the GTN File but missing in the Payrun file:\n'
        self.assertEqual(len(result), 0, error_msg + str(result))
        
        
    def test_elements_missing_payrun(self):
        
        os.chdir(self.folder)
        gtn_pay_elements = GetData.get_gtn_data('GTN.xlsx', pay_elements=True)
        payrun_pay_elements = GetData.get_payrun_data('Payrun.xlsx', pay_elements=True)
        # Changed values of some GTN elements being mapped to Payrun elements
        mapping_data = GetData.get_vendors('mapping.json')
        vendors = mapping_data['vendors']
        os.chdir('..')
        
        # TEST 1: Checks if a GTN element maps to a Payrun element but that element does not exist in the Payrun file
        
        # Removed Backpay column (element 9) from Payrun file
        # Kept mapping in json file
        
        
        # GTN elements which are mapped to payrun elements
        mapped_gtn_elements = pd.merge(gtn_pay_elements, vendors, how='inner')
        
        # Payrun elements which are mapped to by GTN elements
        mapped_payrun_elements = vendors.reset_index().merge(mapped_gtn_elements, how="right")
        
        # Mapped payrun elements not in the payrun file
        payrun_pay_elements = payrun_pay_elements.rename(columns={0:'index'})
        result_not_in_payrun = (pd.merge(payrun_pay_elements, mapped_payrun_elements, on='index', how='outer', indicator=True)
                                .query('_merge == "right_only"')
                                .drop(columns=['_merge','vendor']))
        result_not_in_payrun = list(result_not_in_payrun['index'])
                                
        error_msg = '\n\nThe following mapped Pay Elements are missing from the Payrun file:\n'
        with self.subTest():            
            self.assertEqual(len(result_not_in_payrun), 0, error_msg + str(result_not_in_payrun))
            
        # TEST 2: Checks if pay elements in the GTN do not have a mapping in the Payrun file
        
        missing = (pd.merge(gtn_pay_elements, vendors, how='outer', indicator=True)
                  .query('_merge == "left_only"')
                  .drop(columns='_merge'))
        
        not_used = list(mapping_data['not_used']['vendor'])
        result_not_in_mapping = np.setdiff1d(list(missing.vendor), not_used)
        error_msg = '\n\nPay Elements in the GTN which do not have a mapping in the Payrun File:\n'
        with self.subTest():
            self.assertEqual(len(result_not_in_mapping), 0, error_msg + str(result_not_in_mapping))
    
        
    def test_elements_missing_gtn(self):
        
        os.chdir(self.folder)
        gtn_pay_elements = GetData.get_gtn_data('GTN.xlsx', pay_elements=True)
        payrun_pay_elements = GetData.get_payrun_data('Payrun.xlsx', pay_elements=True)
        # Changed values of some Payrun elements being mapped to by GTN elements
        mapping_data = GetData.get_vendors('mapping.json')
        vendors = mapping_data['vendors']
        os.chdir('..')
    
        # Removed element 9 column (Backpay) from GTN file
        # Kept mapping in json file
        
        # TEST 1: Checks if a Payrun element maps to a GTN element but that element does not exist in the GTN file
        
        # Payrun elements which are mapped to by GTN elements
        vendors_index = pd.DataFrame(vendors.index)
        mapped_payrun_elements = pd.merge(payrun_pay_elements, vendors_index, how='inner')
        
        # GTN elements which are mapped to payrun elements
        mapped_gtn_elements = vendors[vendors.index.isin(mapped_payrun_elements[0])]
        
        result_not_in_gtn = (pd.merge(gtn_pay_elements, mapped_gtn_elements, how='outer', indicator=True)
                             .query('_merge == "right_only"')
                             .drop(columns='_merge'))
        result_not_in_gtn = list(result_not_in_gtn['vendor'])
        
        error_msg = '\n\nThe following mapped Pay Elements are missing from the GTN file:\n'
        with self.subTest():
            self.assertEqual(len(result_not_in_gtn), 0, error_msg + str(result_not_in_gtn))
            
        # TEST 2: Checks if pay elements in the Payrun file do not have a mapping in the GTN
        
        result_not_in_mapping = (pd.merge(payrun_pay_elements, vendors_index, how='outer', indicator=True)
                                 .query('_merge == "left_only"')
                                 .drop(columns='_merge'))
        
        result_not_in_mapping = list(result_not_in_mapping[0])
        error_msg = '\n\nPay Elements in the Payrun file which do not have a mapping in the GTN:\n'
        with self.subTest():
            self.assertEqual(len(result_not_in_mapping), 0, error_msg + str(result_not_in_mapping))
        
    
    
    def test_elements_numeric_gtn(self):
        # Added non-numeric values to gtn file
        os.chdir(self.folder)
        gtn = GetData.get_gtn_data('GTN.xlsx')
        os.chdir('..')
        pay_elements = gtn[gtn.columns[4:]]
        # Checks gtn file for non-numeric elements   
        invalid_columns = pay_elements.select_dtypes(exclude='number').columns.tolist()
        error_msg = '\n\nThe following columns in the GTN file contain non-numeric elements:\n'
        self.assertEqual(len(invalid_columns), 0, error_msg + str(invalid_columns))
        
        

if __name__ == '__main__':
    
    #Driver code
    
    tests_fail = unittest.TestSuite()
    tests_fail.addTest(TestPayslipsData('test_file_type'))
    tests_fail.addTest(TestPayslipsData('test_breaks'))
    tests_fail.addTest(TestPayslipsData('test_header_structure'))
    tests_fail.addTest(TestPayslipsData('test_employees_missing_gtn'))
    tests_fail.addTest(TestPayslipsData('test_employees_missing_payrun'))
    tests_fail.addTest(TestPayslipsData('test_elements_missing_payrun'))
    tests_fail.addTest(TestPayslipsData('test_elements_missing_gtn'))
    tests_fail.addTest(TestPayslipsData('test_elements_numeric_gtn'))
    unittest.TextTestRunner().run(tests_fail)
    
    print('\n')
    tests_succeed = unittest.TestSuite()
    tests_succeed.addTest(TestPayslipsData('test_file_type',tests_succeed))
    tests_succeed.addTest(TestPayslipsData('test_breaks',tests_succeed))
    tests_succeed.addTest(TestPayslipsData('test_header_structure',tests_succeed))
    tests_succeed.addTest(TestPayslipsData('test_employees_missing_gtn',tests_succeed))
    tests_succeed.addTest(TestPayslipsData('test_employees_missing_payrun',tests_succeed))
    tests_succeed.addTest(TestPayslipsData('test_elements_missing_payrun',tests_succeed))
    tests_succeed.addTest(TestPayslipsData('test_elements_missing_gtn',tests_succeed))
    tests_succeed.addTest(TestPayslipsData('test_elements_numeric_gtn',tests_succeed))
    unittest.TextTestRunner().run(tests_succeed)

    
    
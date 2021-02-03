def upper_case_it(lower_file, upper_file):
    upper_data = ''
    with open(lower_file, 'r') as f:
        for line in f.readlines():
            upper_data = upper_data + line.upper()
    print("upper data: ", upper_data)    
        
    with open(upper_file, 'w') as f:
        f.write(upper_data)

upper_case_it('test.txt', 'newfile.txt')


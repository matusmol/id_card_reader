from idcardreader import get_user_data

if __name__ == '__main__':
    customer_data, error_code = get_user_data()
    print("customer_data {}".format(customer_data))
    print("error_code {}".format(error_code))

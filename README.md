id_card_reader
=============
Python driver for DESKO IDenty chrom  
link <https://www.desko.com/site/assets/files/2782/desko_identy-chrom.pdf>  
Script was develop for  REST API to help quick create customer 

Script extract user data from passport or ID

### USAGE 
In your virtual environment install external libraries
> pip install -r requirement.txt

run script
> python example.py


Or in your code import idcardreader.py 
> from idcardreader import get_user_data 
> customer_data, error_code = get_user_data()  

If reader get error (you move quick with ID or data are not readable, ...) script return error_code different than 0  
error_code == 1 its parsing error, when regex canot parse data  
error_code == 2 its card reader sys error (like reader is not connected, reading error,...)

In success customer_data will be filled with a dictionary in format:
* PASSPORT  
{
"issuing_country": ....,  
"last_name": ....,  
"first_name": ....,  
"document_id": ....,  
"date_birth": ....,  
"sex": ....,  
"date_expiration": ....,  
"country": ....,  
"personal_id": ....,  
}

* ID  
{
"issuing_country": ....,  
"document_id": ....,  
"personal_id": ....,  
"date_birth": ....,  
"sex": ....,  
"date_expiration": ....,  
"country": ....,  
"last_name": ....,  
"first_name": ....,  
}
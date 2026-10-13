from backend import database as db

def main():
    db.initialize()
    if db.rows('SELECT id FROM vehicles'):
        print('Existing records found; no demo data added.')
        return
    for make,model,year,price in [('Demo Motors','City',2020,950000),('Example Cars','Family',2022,1450000)]:
        db.write('INSERT INTO vehicles(make,model,year,price_pence) VALUES (?,?,?,?)',(make,model,year,price))
    print('Two fictional vehicles added.')

if __name__ == '__main__':
    main()

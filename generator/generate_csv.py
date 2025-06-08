import csv
import random
import argparse
from datetime import datetime, timedelta

stock_indices = ['S&P500', 'NASDAQ', 'DOWJONES', 'FTSE100', 'DAX']
currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CAD']

initial_values = {}

def get_initial_value(name, row_type):
    if name in initial_values:
        return initial_values[name]
    else:
        if row_type == 'stock':
            value = round(random.uniform(3000, 10000), 2)
        else:
            value = round(random.uniform(0.5, 1.5), 4)
        initial_values[name] = value
        return value

def apply_fluctuation(value, row_type):
    if row_type == 'stock':
        fluctuation = random.uniform(-0.005, 0.005)  # ±0.5%
    else:
        fluctuation = random.uniform(-0.01, 0.01)  # ±1%
    new_value = value * (1 + fluctuation)
    return round(new_value, 4 if row_type == 'currency' else 2)

def generate_random_row(base_time):
    row_type = random.choice(['stock', 'currency'])

    if row_type == 'stock':
        name = random.choice(stock_indices)
    else:
        c1, c2 = random.sample(currencies, 2)
        name = f"{c1}/{c2}"

    previous_value = get_initial_value(name, row_type)
    new_value = apply_fluctuation(previous_value, row_type)
    initial_values[name] = new_value 

    timestamp = base_time.strftime('%Y-%m-%dT%H:%M:%S')
    return [row_type, name, timestamp, new_value]

def generate_csv(filename, num_rows):
    base_time = datetime(2024, 4, 6, 12, 0, 0)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['type', 'name', 'timestamp', 'value'])

        for _ in range(num_rows):
            row = generate_random_row(base_time)
            writer.writerow(row)
            base_time += timedelta(seconds=random.randint(1, 10))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Генератор фінансового CSV з реалістичними коливаннями.')
    parser.add_argument('rows', type=int, help='Кількість рядків, які треба згенерувати')
    parser.add_argument('--output', type=str, default='data.csv', help='Імʼя вихідного файлу')
    
    args = parser.parse_args()
    generate_csv(args.output, args.rows)
    print(f"Згенеровано файл {args.output} з {args.rows} рядками.")

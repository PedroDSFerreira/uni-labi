import csv
import random


def main():
    with open("rand.csv", "w", newline='') as file:
        csv_file = csv.DictWriter(file, delimiter=',', fieldnames=["time", "value"])
        csv_file.writeheader()

        for i in range(1,10):
            csv_file.writerow({"time":i, "value": random.randint(1, 100)})
        
main()
import csv
import sys

def main(argv):
    with open(argv[1], "r") as file:
        csv_file = csv.DictReader(file, delimiter=',')
        temps = [float(row.get("value")) for row in csv_file]

        print(f"Valor mínimo: {min(temps)}")
        print(f"Valor máximo: {max(temps)}")
        print(f"Valor médio: {sum(temps)/len(temps)}")

main(sys.argv)
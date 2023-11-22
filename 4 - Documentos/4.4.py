import json


def main():
    data = [
        {
            "text1":
                [{"time": 1394984189, "name": "cpu", "value": 12},
                 {"time": 1394984190, "name": "cpu", "value": 19}],
            "text5":
                [{"time": 1394984189, "name": "cpu", "value": 12},
                 {"time": 1394984190, "name": "cpu", "value": 19}]

        },
        {
            "text3":
                [{"time": 1394984189, "name": "cpu", "value": 12},
                 {"time": 1394984190, "name": "cpu", "value": 19}]
        }
    ]

    print(json.dumps(data, indent=4, sort_keys=True))

    with open("teste.json", "r") as file:
        print(json.load(file))


main()

import os

def input_only_nums(event):
    keycode = event.GetKeyCode()
    only_nums = list(range(48, 58))
    only_nums.append(8)
    only_nums.append(9)
    if keycode in only_nums:
        event.Skip()

def get_clients_from_csv(csv):
    kontakty = []
    assert os.path.isfile(csv)
    with open(csv, "r") as zawartosc:
        for linia in zawartosc:
            linia = linia.replace("\n", "")
            linia = linia.replace("\r", "")
            rekord = tuple(linia.split(","))
            kontakty.append(rekord)
    return tuple(kontakty)
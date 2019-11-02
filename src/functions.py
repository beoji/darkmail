def input_only_nums(event):
    keycode = event.GetKeyCode()
    only_nums = list(range(48, 58))
    only_nums.append(8)
    only_nums.append(9)
    if keycode in only_nums:
        event.Skip()

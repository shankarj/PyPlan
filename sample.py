pattern = "abcab"
input = "goatdoggoat"

pat_length = len(pattern)
inp_length = len(input)
arr_name = {}
arr_val = []

for val in xrange(pat_length):
    if val not in arr_name.keys():
        arr_name[pattern[val]] = None
        arr_val.append(1)

while arr_val[0] < inp_length:
    if (sum(arr_val) == inp_length):
        is_good = True

        first_val = 0
        for val in xrange(pat_length):
            temp = input[first_val:(first_val + arr_val[val])]
            already_val = arr_name[pattern[val]]
            if already_val == None:
                arr_name[pattern[val]] = temp
            else:
                check = arr_name[pattern[val]]
                if check == temp:
                    pass
                else:
                    is_good = False

            first_val += arr_val[val]

        if is_good:
            print "IT IS A MATCH : " + str(arr_name)
            break
        else:
            for val in arr_name.keys():
                arr_name[val] = None


    arr_val[pat_length - 1] += 1
    for elem in xrange(pat_length - 1, -1, -1):
        if arr_val[elem] > inp_length:
            arr_val[elem] = 1
            arr_val[elem - 1] += 1

if not is_good:
    print "NOT A MATCH"
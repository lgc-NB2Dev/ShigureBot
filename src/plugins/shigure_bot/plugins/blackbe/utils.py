def list_has_same_item(list1, list2):
    for i in list1:
        if i in list2:
            return True
    return False
